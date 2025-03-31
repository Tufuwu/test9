"""Tests for auditing"""
from unittest.mock import (
    call,
    DEFAULT,
    Mock
)
import copy
import tempfile

from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from nacl.public import PrivateKey, SealedBox
from nacl.encoding import Base64Encoder
import pytest

from exams.pearson import audit

# pylint: disable=missing-docstring,redefined-outer-name


DEFAULT_SETTINGS = {
    'EXAMS_AUDIT_ENABLED': True,
    'EXAMS_AUDIT_S3_BUCKET': '.test.bucket.name.',
    'EXAMS_AUDIT_AWS_ACCESS_KEY_ID': 'test.id',
    'EXAMS_AUDIT_AWS_SECRET_ACCESS_KEY': 'test.access.key',
}


@pytest.fixture()
def private_key():
    """Creates a new NaCl private key"""
    return PrivateKey.generate()


@pytest.fixture()
def valid_settings(private_key):
    """
    Fixture that provides valid (passes checks in configure()) configuration
    """
    settings = copy.copy(DEFAULT_SETTINGS)
    settings.update({
        'EXAMS_AUDIT_NACL_PUBLIC_KEY': Base64Encoder.encode(bytes(private_key.public_key)),
    })

    with override_settings(**settings):
        yield DEFAULT_SETTINGS


@pytest.fixture()
def invalid_settings():
    """
    Fixture that runs a test against a set of invalid configurations
    """
    settings = copy.copy(DEFAULT_SETTINGS)
    settings.update({
        'EXAMS_AUDIT_NACL_PUBLIC_KEY': Base64Encoder.encode('bad'),
    })

    with override_settings(**settings):
        yield settings


@pytest.fixture()
def missing_settings():
    """
    Fixture that runs a test with each of the specified settings keys set to None
    """
    settings = copy.copy(DEFAULT_SETTINGS)
    settings["EXAMS_AUDIT_NACL_PUBLIC_KEY"] = None

    with override_settings(**settings):
        yield settings


@pytest.fixture()
def s3_store(valid_settings):  # pylint: disable=unused-argument
    """S3 storage for tests"""
    return audit.S3AuditStorage()


@pytest.fixture
def auditor(valid_settings):  # pylint: disable=unused-argument
    """
    ExamDataAuditor that cleans up the GPG keys after itself
    """
    yield audit.ExamDataAuditor(store=Mock(spec=audit.S3AuditStorage))


def test_s3_store_get_connection_valid(s3_store, mocker):
    """Test get_connection given valid settings"""
    mock = mocker.patch('boto.s3.connection.S3Connection')
    s3_store.get_bucket()
    mock.assert_called_once_with('test.id', 'test.access.key')


@pytest.mark.parametrize('key', [
    'EXAMS_AUDIT_S3_BUCKET',
    'EXAMS_AUDIT_AWS_ACCESS_KEY_ID',
    'EXAMS_AUDIT_AWS_SECRET_ACCESS_KEY',
])
def test_s3_store_missing_settings(s3_store, key):
    """Test configure() against missing settings"""
    with override_settings(**{
        key: None,
    }):
        with pytest.raises(ImproperlyConfigured):
            s3_store.upload('filename', 'data', 'filetype')


def test_s3_store_get_s3_key(s3_store, mocker):
    """Test that the S3 store generates a key object witht he correct bucket and key"""
    mocker.patch.object(s3_store, 'get_bucket', return_value='.the.bucket.')
    key = s3_store.get_s3_key('filename', 'filetype')
    s3_store.get_bucket.assert_called_once_with()
    assert key.bucket == s3_store.get_bucket()
    assert key.key == 'exam_audits/filetype/filename'


def test_exam_data_s3_store_upload(s3_store, mocker):
    """Test that the S3 store uploads a file with the correct headers"""
    mocker.patch.object(s3_store, 'get_s3_key')

    s3_store.upload('filename', 'data', 'filetype')
    mock_key = s3_store.get_s3_key.return_value

    assert mock_key.set_contents_from_string.call_count == 1
    assert mock_key.set_contents_from_string.call_args == call(
        'data',
        headers={
            'x-amz-server-side-encryption': 'AES256'
        }
    )


@pytest.mark.usefixtures('missing_settings')
@pytest.mark.parametrize('is_enabled', [True, False])
def test_exam_data_auditor_enabled(auditor, mocker, is_enabled):
    """Test that audit_file() respected the enabled flag"""
    mocker.patch.multiple(auditor, encrypt=DEFAULT, upload_encrypted_file=DEFAULT)
    with tempfile.NamedTemporaryFile() as audit_file:
        with override_settings(**{
            'EXAMS_AUDIT_ENABLED': is_enabled,
        }):
            auditor.audit_file(audit_file.name, 'filetype')
        assert auditor.upload_encrypted_file.call_count == (1 if is_enabled else 0)


@pytest.mark.usefixtures('missing_settings')
def test_exam_data_auditor_configure_missing_settings(auditor):
    """Test that configure() fails with missing settings"""
    with tempfile.NamedTemporaryFile() as audit_file:
        with pytest.raises(ImproperlyConfigured):
            auditor.audit_file(audit_file.name, 'filetype')


def test_exam_data_auditor_audit_file(auditor, private_key):
    """Test that the auditor encrypts and uploads the file"""
    with tempfile.NamedTemporaryFile() as audit_file:
        # the auditor encrypts the file to a local path
        expected_encrypted_filename = '{}.nacl'.format(audit_file.name)
        expected_encrypted_keypath = 'keypath'  # computed inside _upload_to_s3
        file_contents = b'unencrypted file contents'

        audit_file.write(file_contents)
        audit_file.flush()

        def upload_side_effect(encrypted_filename, encrypted_data, file_type):
            """Verify the encrypted file exists at this point"""
            # verify the upload was triggered with the expected encrypted filename and that file exists
            assert SealedBox(private_key).decrypt(encrypted_data) == file_contents
            assert encrypted_filename == expected_encrypted_filename
            assert file_type == 'sometype'
            return expected_encrypted_keypath
        auditor.store.upload.side_effect = upload_side_effect

        assert auditor.audit_file(audit_file.name, 'sometype') == expected_encrypted_keypath


def test_exam_data_auditor_audit_request_file(auditor, mocker):
    """Test that request files are uploaded with the correct type"""
    mocker.patch.object(auditor, 'audit_file', return_value=True)
    assert auditor.audit_request_file('test.file') is True
    auditor.audit_file.assert_called_once_with('test.file', auditor.REQUEST)


def test_exam_data_auditor_audit_response_file(auditor, mocker):
    """Test that response files are uploaded with the correct type"""
    mocker.patch.object(auditor, 'audit_file', return_value=True)
    assert auditor.audit_response_file('test.file') is True
    auditor.audit_file.assert_called_once_with('test.file', auditor.RESPONSE)
