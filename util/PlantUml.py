# -*- coding: utf-8 -*-
# python 3.x
# Filename: PlantUml.py
# 定义一个PlantUml类实现PlantUml转换图片相关的功能

from __future__ import print_function

import base64
import string
from io import open
from os import environ, path, makedirs
from zlib import compress
import httplib2
import six
from six.moves.urllib.parse import urlencode

from util.FileUtil import FileUtil
from util.NetworkUtil import NetworkUtil

if six.PY2:
    from string import maketrans
else:
    maketrans = bytes.maketrans

__version__ = 0, 3, 0
__version_string__ = '.'.join(str(x) for x in __version__)

__author__ = 'Doug Napoleone, Samuel Marks, Eric Frederich'
__email__ = 'doug.napoleone+plantuml@gmail.com'

plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))


class PlantUMLError(Exception):
    """
    Error in processing.
    """
    pass


class PlantUMLConnectionError(PlantUMLError):
    """
    Error connecting or talking to PlantUML Server.
    """
    pass


class PlantUMLHTTPError(PlantUMLConnectionError):
    """
    Request to PlantUML server returned HTTP Error.
    """

    def __init__(self, response, content, *args, **kwdargs):
        super(PlantUMLConnectionError, self).__init__(*args, **kwdargs)
        self.response = response
        self.content = content
        if not self.message:
            self.message = "%d: %s" % (
                self.response.status, self.response.reason)


def deflate_and_encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server.
    """
    zlibbed_str = compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')


class PlantUML(object):
    """Connection to a PlantUML server with optional authentication.

    All parameters are optional.

    :param str url: URL to the PlantUML server image CGI. defaults to
                    http://www.plantuml.com/plantuml/img/
    :param dict basic_auth: This is if the plantuml server requires basic HTTP
                    authentication. Dictionary containing two keys, 'username'
                    and 'password', set to appropriate values for basic HTTP
                    authentication.
    :param dict form_auth: This is for plantuml server requires a cookie based
                    webform login authentication. Dictionary containing two
                    primary keys, 'url' and 'body'. The 'url' should point to
                    the login URL for the server, and the 'body' should be a
                    dictionary set to the form elements required for login.
                    The key 'method' will default to 'POST'. The key 'headers'
                    defaults to
                    {'Content-type':'application/x-www-form-urlencoded'}.
                    Example: form_auth={'url': 'http://example.com/login/',
                    'body': { 'username': 'me', 'password': 'secret'}
    :param dict http_opts: Extra options to be passed off to the
                    httplib2.Http() constructor.
    :param dict request_opts: Extra options to be passed off to the
                    httplib2.Http().request() call.

    """

    def __init__(self, url='http://www.plantuml.com/plantuml/img/', basic_auth={}, form_auth={},
                 http_opts={}, request_opts={}):
        self.HttpLib2Error = httplib2.HttpLib2Error
        self.url = url
        self.request_opts = request_opts
        self.auth_type = 'basic_auth' if basic_auth else (
            'form_auth' if form_auth else None)
        self.auth = basic_auth if basic_auth else (
            form_auth if form_auth else None)

        # Proxify
        try:
            from urlparse import urlparse
            import socks

            proxy_uri = urlparse(environ.get('HTTPS_PROXY', environ.get('HTTP_PROXY')))
            if proxy_uri:
                proxy = {'proxy_info': httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP,
                                                          proxy_uri.hostname, proxy_uri.port)}
                http_opts.update(proxy)
                self.request_opts.update(proxy)
        except ImportError:
            pass

        self.http = httplib2.Http(**http_opts)

        if self.auth_type == 'basic_auth':
            self.http.add_credentials(
                self.auth['username'], self.auth['password'])
        elif self.auth_type == 'form_auth':
            if 'url' not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'url' must be provided and point to "
                    "the login url.")
            if 'body' not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'body' must be provided and include "
                    "a dictionary with the form elements required to log in. "
                    "Example: form_auth={'url': 'http://example.com/login/', "
                    "'body': { 'username': 'me', 'password': 'secret'}")
            login_url = self.auth['url']
            body = self.auth['body']
            method = self.auth.get('method', 'POST')
            headers = self.auth.get(
                'headers', {'Content-type': 'application/x-www-form-urlencoded'})
            try:
                response, content = self.http.request(
                    login_url, method, headers=headers,
                    body=urlencode(body))
            except self.HttpLib2Error as e:
                raise PlantUMLConnectionError(e)
            if response.status != 200:
                raise PlantUMLHTTPError(response, content)
            self.request_opts['Cookie'] = response['set-cookie']

    def get_url(self, plantuml_text):
        """Return the server URL for the image.
        You can use this URL in an IMG HTML tag.

        :param str plantuml_text: The plantuml markup to render
        :returns: the plantuml server image URL
        """
        return self.url + deflate_and_encode(plantuml_text)

    def processes(self, plantuml_text):
        """Processes the plantuml text into the raw PNG image data.

        :param str plantuml_text: The plantuml markup to render
        :returns: the raw image data
        """
        url = self.get_url(plantuml_text)
        try:
            response, content = self.http.request(url, **self.request_opts)
        except self.HttpLib2Error as e:
            # raise PlantUMLConnectionError(e)
            content = NetworkUtil.get(url)
        return content

    def processesFile(self, filename, outfile=None, errorfile=None, directory=''):
        """Take a filename of a file containing plantuml text and processes
        it into a .png image.

        :param str filename: Text file containing plantuml markup
        :param str outfile: Filename to write the output image to. If not
                    supplied, then it will be the input filename with the
                    file extension replaced with '.png'.
        :param str errorfile: Filename to write server html error page
                    to. If this is not supplined, then it will be the
                    input ``filename`` with the extension replaced with
                    '_error.html'.
        :returns: ``True`` if the image write succedded, ``False`` if there was
                    an error written to ``errorfile``.
        """
        if outfile is None:
            outfile = path.splitext(filename)[0] + '.png'
        if errorfile is None:
            errorfile = path.splitext(filename)[0] + '_error.html'
        if directory and not path.exists(directory):
            makedirs(directory)
        data = open(filename).read()
        try:
            content = self.processes(data)
        except PlantUMLHTTPError as e:
            err = open(path.join(directory, errorfile), 'w')
            err.write(e.content)
            err.close()
            return False
        out = open(path.join(directory, outfile), 'wb')
        out.write(content)
        out.close()
        return True

    def processesContent(self, content, outfile, errorfile=None, directory=''):
        """Take  plantuml text and processes it into a .png image.
        :param str content: Text containing plantuml markup
        :param str outfile: Filename to write the output image to.
        :param str errorfile: Filename to write server html error page
                    to. If this is not supplined, then it will be the
                    input ``outfile`` with the extension replaced with
                    '_error.html'.
        :returns: ``out file path`` if the image write succedded, ``None`` if there was
                    an error written to ``errorfile``.
        """
        if not outfile:
            return None
        outfile = path.splitext(outfile)[0] + '.png'
        FileUtil.removeFile(outfile)
        if errorfile is None:
            errorfile = path.splitext(outfile)[0] + '_error.html'
        if directory and not path.exists(directory):
            makedirs(directory)
        try:
            content = self.processes(content)
        except PlantUMLHTTPError as e:
            err = open(path.join(directory, errorfile), 'w')
            err.write(e.content)
            err.close()
            return None
        fp = path.join(directory, outfile)
        out = open(fp, 'wb')
        out.write(content)
        out.close()
        return fp


if __name__ == '__main__':
    # PlantUML().processesFile('testData')
    PlantUML().processesContent("""@startuml
hide empty description
state A #green
state B #green
state C #green
state D #green
state FAILED #green
[*] --> init
init --> check
check --> C
C --> D
D --> E
D --> Failed
C --> Failed
check --> Failed
init --> Failed
@enduml""", 'testData1')
