# Generated by Django 3.0.11 on 2020-11-20 19:32

from django.db import migrations


def move_wp_editcounts_to_logs(apps, schema_editor):
    Editor = apps.get_model("users", "Editor")
    EditorLog = apps.get_model("users", "EditorLog")
    for editor in Editor.objects.all():
        if (
            editor.wp_editcount_prev
            and editor.wp_editcount_prev_updated
            and (editor.wp_editcount_prev_updated != editor.wp_editcount_updated)
        ):
            log = EditorLog()
            log.editor = editor
            log.editcount = editor.wp_editcount_prev
            log.timestamp = editor.wp_editcount_prev_updated
            log.save()
        if editor.wp_editcount and editor.wp_editcount_updated:
            log = EditorLog()
            log.editor = editor
            log.editcount = editor.wp_editcount
            log.timestamp = editor.wp_editcount_updated
            log.save()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0065_editorlog"),
    ]

    operations = [migrations.RunPython(move_wp_editcounts_to_logs)]
