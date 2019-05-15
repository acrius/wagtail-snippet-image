# wagtail-snippet-image

Package for creating a snippet images for sharing in social networks and etc.
Based on [django-snippet-image](https://github.com/acrius/django-snippet-image)
and [snippet-image](https://github.com/acrius/snippet-image).
But for storage of images used [Wagtail Images](https://docs.wagtail.io/en/stable/advanced_topics/images/index.html).

## Installation

```bash
pip3 install wagtail-snippet-image
```

## How use it

```python
from django.db.models import (
    CharField,
    ForeignKey,
    SET_NULL,
    CASCADE,
)
from wagtail_snippet_image import SnippetImageField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class PageTag(TaggedItemBase):
    content_object = ParentalKey(
        'home.HomePage',
        on_delete=CASCADE,
        related_name='tagged_items',
    )


class Statuses:
    DRAFT = 'draft'
    PUBLISH = 'publish'

    CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISH, 'Publish'),
    )


class HomePage(Page):
    background = ForeignKey(
        'wagtailimages.Image',
        verbose_name='Изображение для обложки',
        related_name='cover_images',
        on_delete=SET_NULL,
        blank=True,
        null=True,
    )

    snippet_image_field = SnippetImageField(
        verbose_name='Example snippet image field',
        null=True,
    )

    status = CharField(
        max_length=20,
        choices=Statuses.CHOICES,
        default=Statuses.DRAFT,
    )

    tags = ClusterTaggableManager(through=PageTag, blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('background'),
        ImageChooserPanel('snippet_image_field'),
        FieldPanel('status'),
        FieldPanel('tags'),
    ]

    def get_snippet_image_background(self, snippet_type):
        return self.background and self.background.file and self.background.file.path \
            if snippet_type == 'default' else None

    def get_snippet_image_center(self, snippet_type):
        return (self.background.focal_point_x, self.background.focal_point_y) \
            if snippet_type == 'default' and self.background \
               and self.background.focal_point_x and self.background.focal_point_y \
            else None

    def get_snippet_image_text(self, snippet_type):
        return self.title if snippet_type == 'default' else None

    def snippet_image_should_be_created(self):
        return self.status == Statuses.PUBLISH

    # Wagtail custom methods for create wagtail images for sharing snippet image
    def get_snippet_image_title(self, snippet_type):
        return self.title if snippet_type == 'default' else None

    def get_snippet_image_tags(self, snippet_type):
        return self.tags.names() if snippet_type == 'default' else None

```

And use it in template:

```html
<meta property="og:image" content="{{ image(page.snippet_image_field, 'original') }}" />
```

## API

Use [django-snippet-image](https://github.com/acrius/django-snippet-image) api.

New arguments in wagtail-snippet-image:

* title - Title of wagtail image;
* tag - Tags of wagtail image;

Example of use:

```python
...

class Page(Page):
    snippet_image_field = SnippetImageField(
        verbose_name='Example snippet image field',
        null=True,
    )
    
    ...

    def get_snippet_image_title(self, snippet_type):
        return self.title if snippet_type == 'default' else None

    def get_snippet_image_tags(self, snippet_type):
        return self.tags.names() if snippet_type == 'default' else None
```

or

```python
...

class Page(Page):
    snippet_image_field = SnippetImageField(
        title='Title of image',
        tags=('tag1', 'tag2',),
        verbose_name='Example snippet image field',
        null=True,
    )

    ...
```

## Example

To run the example, install dependencies.
For example use poetry:

```bash
poetry install
```

Go to the "exmaple" directory and execute:

```bash
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```

## Tests

To run the tests, install dependencies.
For example use poetry:

```bash
poetry install
```

Go to the "exmaple" directory and exec0.0.0.0:8000ute:

```bash
python3 manage.py runserver test
```
