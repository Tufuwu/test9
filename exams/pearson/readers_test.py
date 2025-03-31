
"""
Tests for TSV readers
"""
import io
from collections import namedtuple
from datetime import datetime
from unittest import TestCase as UnitTestCase

import pytz

from django.conf import settings
from exams.pearson.readers import (
    BaseTSVReader,
    EACReader,
    EACResult,
    VCDCReader,
    VCDCResult,
    EXAMReader,
)
from exams.pearson.exceptions import InvalidTsvRowException

FIXED_DATETIME = datetime(2016, 5, 15, 15, 2, 55, tzinfo=pytz.UTC)


class BaseTSVReaderTest(UnitTestCase):
    """
    Tests for Pearson reader code
    """

    def test_reader_init(self):
        """
        Tests that the reader initializes correctly
        """

        PropTuple = namedtuple('PropTuple', ['prop2'])
        fields = {
            ('prop2', 'Prop2', int),
        }

        reader = BaseTSVReader(fields, PropTuple)

        assert reader.field_mappers == fields
        assert reader.read_as_cls == PropTuple

    def test_map_row(self):
        """
        Tests map_row with a prefix set
        """
        PropTuple = namedtuple('PropTuple', ['prop2'])
        reader = BaseTSVReader({
            ('Prop2', 'prop2'),
        }, PropTuple)

        row = {
            'Prop1': '12',
            'Prop2': '145',
        }

        result = reader.map_row(row)
        assert result == PropTuple(
            prop2='145',
        )
        assert isinstance(result.prop2, str)

        reader = BaseTSVReader({
            ('Prop2', 'prop2', int),
        }, PropTuple)

        row = {
            'Prop1': 12,
            'Prop2': 145,
        }

        result = reader.map_row(row)
        assert result == PropTuple(
            prop2=145,
        )
        assert isinstance(result.prop2, int)

        with self.assertRaises(InvalidTsvRowException):
            reader.map_row({})

    def test_read(self):
        """
        Tests the read method outputs correctly
        """
        PropTuple = namedtuple('PropTuple', ['prop1', 'prop2'])
        tsv_file = io.StringIO(
            "Prop1\tProp2\r\n"
            "137\t145\r\n"
            "\tnot_an_int\r\n"
        )
        reader = BaseTSVReader([
            ('Prop1', 'prop1'),
            ('Prop2', 'prop2', int),
        ], PropTuple)

        valid_row = PropTuple(
            prop1='137',
            prop2=145,
        )

        results = reader.read(tsv_file)

        assert results == ([valid_row], [{
            'Prop1': '',
            'Prop2': 'not_an_int'
        }])


class VCDCReaderTest(UnitTestCase):
    """Tests for VCDCReader"""
    def test_vcdc_read(self):  # pylint: disable=no-self-use
        """Test that read() correctly parses a VCDC file"""
        sample_data = io.StringIO(
            "ClientCandidateID\tStatus\tDate\tMessage\r\n"
            "1\tAccepted\t2016/05/15 15:02:55\t\r\n"
            "145\tAccepted\t2016/05/15 15:02:55\tWARNING: There be dragons\r\n"
            "345\tError\t2016/05/15 15:02:55\tEmpty Address\r\n"
        )

        reader = VCDCReader()
        results = reader.read(sample_data)

        assert results == ([
            VCDCResult(
                client_candidate_id=1, status='Accepted', date=FIXED_DATETIME, message=''
            ),
            VCDCResult(
                client_candidate_id=145, status='Accepted', date=FIXED_DATETIME, message='WARNING: There be dragons'
            ),
            VCDCResult(
                client_candidate_id=345, status='Error', date=FIXED_DATETIME, message='Empty Address'
            ),
        ], [])


class EACReaderTest(UnitTestCase):
    """Tests for EACReader"""
    def test_eac_read(self):  # pylint: disable=no-self-use
        """Test that read() correctly parses a EAC file"""
        sample_data = io.StringIO(
            "ClientAuthorizationID\tClientCandidateID\tStatus\tDate\tMessage\r\n"
            "4\t1\tAccepted\t2016/05/15 15:02:55\t\r\n"
            "5\t2\tAccepted\t2016/05/15 15:02:55\tWARNING: There be dragons\r\n"
            "6\t3\tError\t2016/05/15 15:02:55\tInvalid profile\r\n"
        )

        reader = EACReader()
        results = reader.read(sample_data)

        assert results == ([
            EACResult(
                client_authorization_id=4,
                client_candidate_id=1,
                date=FIXED_DATETIME,
                status='Accepted',
                message=''
            ),
            EACResult(
                client_authorization_id=5,
                client_candidate_id=2,
                date=FIXED_DATETIME,
                status='Accepted',
                message='WARNING: There be dragons'
            ),
            EACResult(
                client_authorization_id=6,
                client_candidate_id=3,
                date=FIXED_DATETIME,
                status='Error',
                message='Invalid profile'
            )
        ], [])


class EXAMReaderTest(UnitTestCase):
    """Tests for EXAMReader"""
    def test_exam_read_no_shows(self):
        """Test that a typical no-show result from Perason does not result in any errors"""
        test_file_path = '{}/exams/pearson/test_resources/noshow.dat'.format(settings.BASE_DIR)

        reader = EXAMReader()
        with open(test_file_path, 'r') as test_file:
            results = reader.read(test_file)

        # Assert that there are no error messages in the results tuple
        assert len(results[1]) == 0
