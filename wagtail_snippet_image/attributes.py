from enum import Enum
from django_snippet_image.attributes import Attribute


class ImageDescriptionAttributes(Enum):
    title = Attribute()
    tags = Attribute()
