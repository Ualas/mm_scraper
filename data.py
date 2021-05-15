#!/usr/bin/env python3
from selenium import webdriver

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
proxies = req_proxy.get_proxy_list() #this will create proxy list

br = [] #int is list of Indian proxy
for proxy in proxies:
    if proxy.country == 'Brazil':
        br.append(proxy)
        
PROXY = proxies[0].get_address()
webdriver.DesiredCapabilities.FIREFOX['proxy']={
    "httpProxy":PROXY,
    "ftpProxy":PROXY,
    "sslProxy":PROXY,

    "proxyType":"MANUAL",

}
driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
driver.get('https://www.maxmilhas.com.br/busca-passagens-aereas/OW/BSB/IAH/2020-04-06/1/0/0/EC')
