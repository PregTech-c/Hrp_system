from django import template
import urllib, io, base64

register = template.Library()

@register.filter
def get64(url):
    """
    Method returning base64 image data instead of URL
    """
    if url.startswith("http"):
        image = io.StringIO(urllib.urlopen(url).read())
        return 'data:image/jpg;base64,' + base64.b64encode(image.read())
    else:
        try:
            with open(url, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
        except:
            return ''
        else:
            return 'data:image/jpg;base64,' + encoded_string
