"""Exam auditing"""
import logging
import os

from boto.s3 import (
    connection,
    key,
)
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from nacl.encoding import Base64Encoder
from nacl.public import PublicKey, SealedBox

from micromasters import utils

SSE_ENCRYPTION_ALGORITHM = 'AES256'

log = logging.getLogger(__name__)


class S3AuditStorage:
    """Audit storage mechanism for S3"""

    def _validate(self):
        """
        Configures / validates the storage configuration

        Raises:
            ImproperlyConfigured: if a required setting is not set
        """
        missing_settings = [key for key in (
            'EXAMS_AUDIT_S3_BUCKET',
            'EXAMS_AUDIT_AWS_ACCESS_KEY_ID',
            'EXAMS_AUDIT_AWS_SECRET_ACCESS_KEY',
        ) if not getattr(settings, key)]

        if missing_settings:
            raise ImproperlyConfigured(
                'The following setting(s) are required but not set: {}'.format(missing_settings)
            )

    def get_connection(self):
        """
        Creates a connection to S3

        Returns:
            boto.s3.connection.S3Connection: a connection to S3
        """
        self._validate()
        return connection.S3Connection(
            settings.EXAMS_AUDIT_AWS_ACCESS_KEY_ID,
            settings.EXAMS_AUDIT_AWS_SECRET_ACCESS_KEY
        )

    def get_bucket(self):
        """
        Gets the configured bucket

        Raises:
            ImproperlyConfigured: if a required setting is not set

        Returns:
            boto.s3.bucket.Bucket: the S3 bucket for storage
        """
        return self.get_connection().get_bucket(settings.EXAMS_AUDIT_S3_BUCKET)

    def get_s3_key(self, filename, file_type):
        """
        Determines the S3 key to store the file under

        Args:
            filename (str): filename of the encrypted file
            file_type (str): type of the encrypted file

        Returns:
            boto.s3.key.Key: the key to store the file in
        """
        basename = os.path.basename(filename)
        return key.Key(
            self.get_bucket(),
            'exam_audits/{file_type}/{filename}'.format(
                filename=basename,
                file_type=file_type,
            )
        )

    def upload(self, filename, data, file_type):
        """
        Uploads the file to S3

        Args:
            filename (str): filename of the encrypted file
            data (str): the encrypted data
            file_type (str): type of the encrypted file

        Returns:
            str: the key path in S3 where the file was stored
        """
        s3_key = self.get_s3_key(filename, file_type)
        s3_key.set_contents_from_string(
            data,
            headers={
                'x-amz-server-side-encryption': SSE_ENCRYPTION_ALGORITHM,
            }
        )
        return s3_key.key


def _get_public_key():
    """
    Get the configured PublicKey instance

    Returns:
        PublicKey:
            the public key as configured in settings
    """
    if not settings.EXAMS_AUDIT_NACL_PUBLIC_KEY:
        raise ImproperlyConfigured(
            "EXAMS_AUDIT_NACL_PUBLIC_KEY is required but not set"
        )

    return PublicKey(settings.EXAMS_AUDIT_NACL_PUBLIC_KEY, encoder=Base64Encoder)


def _get_sealed_box():
    """
    Get a NaCl SealedBox configured with the public key

    Returns:
        SealedBox:
            the configured SealedBox
    """
    return SealedBox(_get_public_key())


class ExamDataAuditor:
    """
    Encrypted file auditor for exam requests/responses
    """
    REQUEST = 'request'
    RESPONSE = 'response'

    def __init__(self, store=None):
        self.store = store or S3AuditStorage()

    def encrypt(self, filename, encrypted_filename):
        """
        Encrypts the local file

        Args:
            filename (str): absolute path to the local file
            encrypted_filename (str): absolute path to the local encrypted file

        Returns:
            str:
                the encrypted data
        """
        log.debug('Encrypting file %s to %s', filename, encrypted_filename)

        with open(filename, 'rb') as source_file:
            return _get_sealed_box().encrypt(source_file.read())

    def upload_encrypted_file(self, filename, file_type):
        """
        Uploads the file to S3

        Args:
            filename (str): absolute path to the local file
            file_type (str): the type of file, either RESPONSE or REQUEST

        Returns:
            str: path to the stored file
        """
        encrypted_filename = '{}.nacl'.format(filename)
        try:
            encrypted_data = self.encrypt(filename, encrypted_filename)

            return self.store.upload(encrypted_filename, encrypted_data, file_type)
        finally:
            utils.safely_remove_file(encrypted_filename)

    def audit_file(self, filename, file_type):
        """
        Audits the given file - this means we encrypt it and store it on S3

        Args:
            filename (str): path to the unencrypted file
            file_type (str): the type of file, either RESPONSE or REQUEST

        Returns:
            str: the path where the file was stored
        """
        if not settings.EXAMS_AUDIT_ENABLED:
            return None

        return self.upload_encrypted_file(filename, file_type)

    def audit_response_file(self, filename):
        """
        Audits the given response file, see audit() for details

        Args:
            filename (str): path to the unencrypted file

        Returns: :
            str: the path where the file was stored
        """
        return self.audit_file(filename, self.RESPONSE)

    def audit_request_file(self, filename):
        """
        Audits the given request file, see audit() for details

        Args:
            filename (str): path to the unencrypted file

        Returns:
            str: the path where the file was stored
        """
        return self.audit_file(filename, self.REQUEST)
