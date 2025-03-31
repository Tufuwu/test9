# Generated by Django 2.2.6 on 2019-10-31 16:24

import apps.cms.blocks
from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('a4_candy_cms_pages', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simplepage',
            name='body_de',
        ),
        migrations.RemoveField(
            model_name='simplepage',
            name='body_en',
        ),
        migrations.AddField(
            model_name='simplepage',
            name='body_streamfield_de',
            field=wagtail.core.fields.StreamField([('html', wagtail.core.blocks.RawHTMLBlock()), ('richtext', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('entries', wagtail.core.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.CharBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('columns_cta', wagtail.core.blocks.StructBlock([('columns_count', wagtail.core.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('body', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.CharBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('documents', wagtail.core.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.core.blocks.StructBlock([('color', wagtail.core.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.core.blocks.TextBlock()), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simplepage',
            name='body_streamfield_en',
            field=wagtail.core.fields.StreamField([('html', wagtail.core.blocks.RawHTMLBlock()), ('richtext', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('entries', wagtail.core.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.CharBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('columns_cta', wagtail.core.blocks.StructBlock([('columns_count', wagtail.core.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('body', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.CharBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('documents', wagtail.core.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.core.blocks.StructBlock([('color', wagtail.core.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.core.blocks.TextBlock()), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], blank=True),
        ),
    ]
