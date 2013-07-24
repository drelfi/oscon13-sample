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


#################################################################################
def runSelenium(url, proxy_host = "", proxy_port = 0):
    '''
    Running instance of firefox against our proxy
    '''
    from selenium import webdriver
    
    if len(proxy_host) > 0:
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.proxy.type", 1)
        fp.set_preference("network.proxy.http", "localhost")
        fp.set_preference("network.proxy.http_port", 8080)
        br = webdriver.Firefox(firefox_profile=fp)
    else:
        br = webdriver.Firefox()
    
    '''Call URL from the recently opened window'''
    br.get(url)
    
    '''Don't forget to close the tested window'''
    br.close()

if __name__ == '__main__':
    runSelenium("http://www.intel.com")