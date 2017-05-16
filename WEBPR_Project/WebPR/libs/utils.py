import os
import hashlib
import random
import pdfkit
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string


def get_random_filename(filename):
    rand_str = str(datetime.now()) + filename + str(random.randint(1, 10000))
    return (hashlib.md5(rand_str.encode('UTF-8')).hexdigest() +
            os.path.splitext(filename)[1])


def calculate_age(birthdate):
    diff = datetime.now() - birthdate
    return diff.days // 365


pdf_default_options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
}


def template2pdf(template=None, **kwargs):
    """
    Convert string to pdf field
    :param template:
        django template path
    :param kwargs:
        pass here parameters that will be submitted inside HTML template as is
    :param output:
        if False function would return in-memory file, otherwise it will be stored on disk
        (this will be part of KWARGS)
    :return:
        file if kwargs.output is not set or is false
    """
    str_ = render_to_string(template, kwargs)
    output = kwargs.get('output', False)
    ret = pdfkit.from_string(
        str_, output, settings.WKHTMLTOPDF_OPTIONS or pdf_default_options)
    return (ret, str_)
