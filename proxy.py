from selenium import webdriver

import proxyscrape
collector = proxyscrape.create_collector('my-collector', 'https')  # Create a collector for http resources
proxy_info = collector.get_proxy({'country': 'united states'})  # Retrieve a united states proxy

proxy = f"{proxy_info.host}:{proxy_info.port}"

print(proxy) # print the proxy

# from Proxy_List_Scrapper import Scrapper, Proxy, ScrapperException
# scrapper = Scrapper(category='NEW', print_err_trace=False)

# # Get ALL Proxies According to your Choice
# data = scrapper.getProxies()
# for item in data.proxies:
#     proxy = '{}:{}'.format(item.ip, item.port)

# print(proxy)
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=%s' % proxy)

chrome = webdriver.Chrome(options=options)
chrome.get("https://www.google.com")




# #!/usr/bin/env python3
# from selenium import webdriver
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

# req_proxy = RequestProxy(); #you may get different number of proxy when  you run this at each time
# proxies = req_proxy.get_proxy_list() #this will create proxy list

# br = [] #int is list of Indian proxy
# for proxy in proxies:
#     if proxy.country == 'Brazil':
#         br.append(proxy)
        
# print("print", br)
# PROXY = proxies[0].get_address()
# webdriver.DesiredCapabilities.FIREFOX['proxy']={
#     "httpProxy":PROXY,
#     "ftpProxy":PROXY,
#     "sslProxy":PROXY,

#     "proxyType":"MANUAL",

# }
# driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
# driver.get('https://whatismyipaddress.com')
