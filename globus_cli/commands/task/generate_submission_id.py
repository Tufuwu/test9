from globus_cli.parsing import command
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command(
    "generate-submission-id",
    short_help="Get a task submission ID",
    adoc_output=(
        "When text output is requested, the generated 'UUID' is the only output."
    ),
    adoc_examples="""Submit a transfer, using a submission ID generated by this command:

[source,bash]
----
$ sub_id="$(globus task generate-submission-id)"
$ globus transfer --submission-id "$sub_id" ...
----
""",
)
def generate_submission_id():
    """
    Generate a new task submission ID for use in  `globus transfer` and `gloubs delete`.
    Submission IDs allow you to safely retry submission of a task in the presence of
    network errors. No matter how many times you submit a task with a given ID, it will
    only be accepted and executed once. The response status may change between
    submissions.

    \b
    Important Note: Submission IDs are not the same as Task IDs.
    """
    client = get_client()

    res = client.get_submission_id()
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="value")
