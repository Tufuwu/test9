"""Configure pytest"""
import pytest


@pytest.fixture(autouse=True)
def auditor(request, mocker):
    """Default mock for auditor"""
    mock = mocker.patch('exams.pearson.audit.ExamDataAuditor', autospec=True)

    # compatability for unitest tests
    if request.instance is not None:
        request.instance.auditor = mock

    # yield for vanilla pytest usages
    yield mock
