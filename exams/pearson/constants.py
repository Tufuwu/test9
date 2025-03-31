"""Pearson-related constants"""
from types import SimpleNamespace

# Pearson TSV constants
PEARSON_DATETIME_FORMATS = [
    "%Y/%m/%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S"
]
PEARSON_DEFAULT_DATETIME_FORMAT = PEARSON_DATETIME_FORMATS[0]
PEARSON_DEFAULT_DATE_FORMAT = PEARSON_DEFAULT_DATETIME_FORMAT.split(' ')[0]

PEARSON_FILE_TYPES = SimpleNamespace(
    EAC='eac',
    VCDC='vcdc',
    EXAM='exam',
    CAND='cand',
    SURV='surv',
    CMNT='cmnt',
    SECT='sect',
    RESP='resp',
    ITEM='item',
)

# these are files we intentionally skip, but treat as if we processed them
PEARSON_INTENDED_SKIP_FILE_TYPES = (
    PEARSON_FILE_TYPES.CAND,
    PEARSON_FILE_TYPES.SURV,
    PEARSON_FILE_TYPES.CMNT,
    PEARSON_FILE_TYPES.SECT,
    PEARSON_FILE_TYPES.ITEM,
    PEARSON_FILE_TYPES.RESP,
)

# SFTP Upload constants
PEARSON_UPLOAD_REQUIRED_SETTINGS = [
    "EXAMS_SFTP_HOST",
    "EXAMS_SFTP_PORT",
    "EXAMS_SFTP_USERNAME",
    "EXAMS_SFTP_PASSWORD",
    "EXAMS_SFTP_UPLOAD_DIR",
]

# Common options for Pearson TSV readers/writers
PEARSON_DIALECT_OPTIONS = {
    'delimiter': '\t',
}

# Only for these countries does Pearson require/support state/zip
PEARSON_STATE_SUPPORTED_COUNTRIES = (
    "US",
    "CA",
)

# Vue Candidate Data Confirmation (VCDC) file statuses
VCDC_SUCCESS_STATUS = "Accepted"
VCDC_FAILURE_STATUS = "Error"

# Exam Authorization Confirmation (EAC) file statuses
EAC_SUCCESS_STATUS = "Accepted"
EAC_FAILURE_STATUS = "Error"

# EXAM constants
EXAM_GRADE_PASS = 'pass'
EXAM_GRADE_FAIL = 'fail'
EXAM_GRADES = (
    EXAM_GRADE_PASS,
    EXAM_GRADE_FAIL,
)
