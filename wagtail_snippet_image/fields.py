from django.db.models import (
    ForeignKey,
    SET_NULL,
)
from wagtail.images.models import Image
from django_snippet_image.fields import BaseSnippetImageFieldMixin
from django_snippet_image.attributes import Attributes

from .attributes import ImageDescriptionAttributes


class SnippetImageField(BaseSnippetImageFieldMixin, ForeignKey):
    default_related_prefix = 'snippet_image'

    def __init__(
            self,
            snippet_type='default',
            **kwargs
    ):
        self.kwargs = self.extract_specific_kwargs(kwargs)
        image_description_kwargs = self.extract_image_description_kwargs(kwargs)
        self.kwargs.update(image_description_kwargs)
        self.snippet_type = snippet_type
        kwargs['related_name'] = kwargs.get('related_name') or '{}_{}'.format(snippet_type, self.default_related_prefix)
        kwargs['on_delete'] = kwargs.get('on_delete') or SET_NULL
        kwargs['blank'] = True
        if kwargs.get('to'):
            kwargs.pop('to')
        super().__init__(
            to='wagtailimages.Image',
            **kwargs
        )

    def extract_image_description_kwargs(self, kwargs):
        return self.extract_kwargs(kwargs, ImageDescriptionAttributes)

    def get_image_description(self, instance):
        description = {
            'title': self.get_attribute_value(instance, ImageDescriptionAttributes.title)
                     or self.get_attribute_value(instance, Attributes.text),
            'tags': self.get_attribute_value(instance, ImageDescriptionAttributes.tags),
        }

        return description

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        specific_attributes_values = self.get_specific_deconstruct_kwargs()
        kwargs.update(specific_attributes_values)

        return name, path, args, kwargs

    def pre_save(self, instance, add):
        image_pk = super().pre_save(instance, add)
        if not image_pk and self.should_be_created(instance):
            image = self.create_image(instance)
            image_pk = image.pk
            setattr(instance, self.attname, image_pk)

        return image_pk

    def save_form_data(self, instance, image):
        if (not image or not image.file) and self.should_be_created(instance):
            image = self.create_image(instance)

        super().save_form_data(instance, image)

    def create_image(self, instance):
        data = self.collect_data(instance)
        image_description = self.get_image_description(instance)
        tags = image_description.get('tags') and image_description.pop('tags')
        image = Image(
            **image_description
        )
        snippet_image = self.create_snippet_image(data)
        file_name = self.get_file_name()
        image.file.save(file_name, snippet_image, save=False)
        image.save()
        if tags:
            image.tags.set(*tags, clear=True)
            image.save()

        return image
