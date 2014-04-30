from django.contrib.gis.geos import geometry
from PIL import Image
from PIL.ExifTags import TAGS

def point_from_exif(photo_path):
    tags = {TAGS.get(t): v for t, v in
            Image.open(photo_path)._getexif().items()}

    n_sec = tags['GPSInfo'][2][2][0] / float(tags['GPSInfo'][2][2][1])
    n_min = tags['GPSInfo'][2][1][0] / float(tags['GPSInfo'][2][1][1])
    n_deg = tags['GPSInfo'][2][0][0] / float(tags['GPSInfo'][2][0][1])
    w_sec = tags['GPSInfo'][4][2][0] / float(tags['GPSInfo'][4][2][1])
    w_min = tags['GPSInfo'][4][1][0] / float(tags['GPSInfo'][4][1][1])
    w_deg = tags['GPSInfo'][4][0][0] / float(tags['GPSInfo'][4][0][1])

    lat = n_deg + (n_min + n_sec/60.0)/60.0
    lng = w_deg + (w_min + w_sec/60.0)/60.0

    if tags['GPSInfo'][1] != 'N':
        lat *= -1
    if tags['GPSInfo'][3] != 'E':
        lng *= -1

    return geometry.Point(x=lng, y=lat, srid=4326)


class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data

        return super(MultipartResource, self).deserialize(request, data, format)

    def post_list(self, request, **kwargs):
        if not hasattr(request, '_body') and request.META.get('CONTENT_TYPE').startswith('multipart'):
            request._body = request.POST

        return super(MultipartResource, self).post_list(request, **kwargs)
