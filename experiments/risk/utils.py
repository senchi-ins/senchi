import math
import base64
import hashlib
import hmac
from urllib import parse as urlparse


def get_tile_coordinates(zoom: float, lat: float, lon: float) -> tuple[int, int, int]:
    """
    Get the tile coordinates for a given latitude, longitude, and zoom level.

    Args:
        zoom: The zoom level of the tile.
        lat: The latitude of the location.
        lon: The longitude of the location.
    """
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat * math.pi / 180.0) + (1 / math.cos(lat * math.pi / 180.0))) / math.pi) / 2.0 * n)
    return zoom, xtile, ytile

# From: https://developers.google.com/maps/documentation/streetview/digital-signature#sample-code-for-url-signing
def sign_url(input_url=None, secret=None):
    """ Sign a request URL with a URL signing secret.
      Usage:
      from urlsigner import sign_url
      signed_url = sign_url(input_url=my_url, secret=SECRET)
      Args:
      input_url - The URL to sign
      secret    - Your URL signing secret
      Returns:
      The signed request URL
  """

    if not input_url or not secret:
        raise Exception("Both input_url and secret are required")

    url = urlparse.urlparse(input_url)

    # We only need to sign the path+query part of the string
    url_to_sign = url.path + "?" + url.query

    # Decode the private key into its binary format
    # We need to decode the URL-encoded private key
    decoded_key = base64.urlsafe_b64decode(secret)

    # Create a signature using the private key and the URL-encoded
    # string using HMAC SHA1. This signature will be binary.
    signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

    # Encode the binary signature into base64 for use within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

    # Return signed URL
    return original_url + "&signature=" + encoded_signature.decode()

