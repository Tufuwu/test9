# Generated by Django 2.1.7 on 2019-04-22 08:57

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailimages", "0001_squashed_0021"),
        ("cms", "0004_add_video_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursepage",
            name="subhead",
            field=models.CharField(
                blank=True,
                help_text="A short subheading to apper below the title on the program/course page",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="background_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Background image size must be at least 1900x650 pixels.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.Image",
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="subhead",
            field=models.CharField(
                blank=True,
                help_text="A short subheading to apper below the title on the program/course page",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="video_title",
            field=wagtail.core.fields.RichTextField(
                blank=True,
                help_text="The title to be displayed for the program/course video",
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video to be displayed for this program/course",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="background_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Background image size must be at least 1900x650 pixels.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.Image",
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="video_title",
            field=wagtail.core.fields.RichTextField(
                blank=True,
                help_text="The title to be displayed for the program/course video",
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video to be displayed for this program/course",
                null=True,
            ),
        ),
    ]
