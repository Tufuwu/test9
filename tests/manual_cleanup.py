#!/usr/bin/env python
import click

from globus_cli.services.transfer import get_client as get_tc
from tests.utils import patch_config


def cleanup_bookmarks(tc):
    for bm in tc.bookmark_list():
        tc.delete_bookmark(bm["id"])


def cleanup_tasks(tc):
    tasks = tc.task_list(num_results=None, filter="status:ACTIVE,INACTIVE")
    for t in tasks:
        tc.cancel_task(t["task_id"])


@click.command("cleanup")
@click.option("--cancel-jobs", is_flag=True)
def main(cancel_jobs):
    with patch_config():
        tc = get_tc()
        cleanup_bookmarks(tc)

        if cancel_jobs:
            cleanup_tasks(tc)


if __name__ == "__main__":
    main()
