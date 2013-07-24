'''
The MIT License (MIT)

Copyright (c) 2013 David Elfi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from twisted.web import http, proxy
from twisted.python import log

tmp_folder = "--To Be Changed--"

#################################################################################
def dataToStore(bufin, headers):
    """
        Unzip and decode the data to be stored in a file
    """
    from re import match
    import StringIO
    import gzip
    
    if headers.has_key("Content-Encoding") and "gzip" in headers["Content-Encoding"].lower():
        '''Decompress content'''
        f = StringIO.StringIO( bufin )
        zf = gzip.GzipFile(fileobj=f)
        buf = zf.read()
        zf.close()
    else:
        buf = bufin
    
  
    '''Encode according to header information'''
    try:
        contentType = headers["Content-Type"]
    except:
        contentType = ""
                    
    m = match( r"(.+);.*charset=([\w|\-]+).*", contentType)           
    if (m is not None and "text" in m.group(1)) or 'text' in contentType:
        if m is not None and len(m.group(2)) > 0:
            return buf.decode(m.group(2))
        else:
            return buf.decode('utf8')
    
    return ""

#################################################################################
def create_tmp_folder(site):
    """
    Create the temporary folder
    """
    from datetime import datetime
    import urllib2
    import os

    # Store the content in the following folder
    ts = datetime.now()
    foldername = urllib2.quote(site)

    # Escape all the / in order to not confuse FS
    foldername = foldername.replace("/", "-")
    tmp_folder = os.sep + "tmp" + os.sep + foldername + os.sep + ts.strftime("%y-%m-%d-%H-%M")
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)
    return tmp_folder

#################################################################################
class CacheProxyClient(proxy.ProxyClient):
    """
        Overwrite our methods for caching data
    """
    
    def connectionMade(self):
        log.msg("Connection made %d" % id(self))
        # Clear the buffer
        self.__resp_data = ""
        self.__resp_headers = {}
        proxy.ProxyClient.connectionMade(self)
    
    def handleStatus(self, version, code, message):
        log.msg("Status: %s - %s" % (code,message))
        proxy.ProxyClient.handleStatus(self, version, code, message)
    
    def handleHeader(self, key, value):
        log.msg("Header CacheProxyClient: %s: %s" % (key, value))
 
        # Save response header. Self.headers contains headers sent to the server
        self.__resp_headers[key] = value
        
        proxy.ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buf):

        #### Store response data. Self.data is the data sent to the server
        self.__resp_data += buf
        
        proxy.ProxyClient.handleResponsePart(self, buf)
        
    def handleResponseEnd(self):        
        import traceback

        '''Preventing request close connection error '''
        try:
            proxy.ProxyClient.handleResponseEnd(self)
        except:
            pass

        # Get the data to write
        buf = dataToStore(self.__resp_data, self.__resp_headers)
        
        # Only store buf with data
        if len(buf) > 0:
            try:
                # filename where to write URL content. Use only 64 characters for file name
                fname_tmp = urllib2.quote(self.rest).replace("/", "-")[:64]
                filename = tmp_folder + os.sep + fname_tmp
                
                f = open(filename, "w")
                f.write( buf.encode('utf8') )
                f.close()
            except:
                # In case that something goes wrong :)
                traceback.print_exc(file=sys.stdout)            


class CacheProxyClientFactory(proxy.ProxyClientFactory):
    protocol = CacheProxyClient

class CacheProxyRequest(proxy.ProxyRequest):
    protocols = dict(http=CacheProxyClientFactory)

class CacheProxy(proxy.Proxy):
    requestFactory = CacheProxyRequest

class CacheProxyFactory(http.HTTPFactory):
    protocol = CacheProxy


#################################################################################
def runSelenium(url, proxy_host = "", proxy_port = 0):
    '''
    Running instance of firefox against our proxy
    '''
    from selenium import webdriver
    from twisted.internet import reactor
    
    if len(proxy_host) > 0:
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.proxy.type", 1)
        fp.set_preference("network.proxy.http", proxy_host)
        fp.set_preference("network.proxy.http_port", proxy_port)
        br = webdriver.Firefox(firefox_profile=fp)
    else:
        br = webdriver.Firefox()
    
    '''Call URL from the recently opened window'''
    br.get(url)
    
    '''Don't forget to close the tested window'''
    br.close()

    'Finished page load'
    reactor.stop()
    
    
#################################################################################
if __name__ == '__main__':
    import sys
    from twisted.internet import endpoints, reactor
    
    url_str = sys.argv[1]
    
    tmp_folder = create_tmp_folder(url_str)

    # Prepare reactor to listen and log
    log.startLogging(sys.stdout)
    endpoint = endpoints.serverFromString(reactor, "tcp:%d:interface=%s" % (8080, "localhost"))
    
    # Configure the Proxy listening class. It will be used for every incoming connection.
    d = endpoint.listen(CacheProxyFactory())
    
    # Since twisted is an event driven framework, single threaded, our call to selenium must be done by the reactor
    reactor.callInThread( runSelenium, url_str, "localhost", 8080)
    reactor.run()