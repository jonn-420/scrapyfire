from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Process
import threading
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import*
from selenium.webdriver.common.action_chains import ActionChains
import requests
import json
import os
from pathlib import Path
from random import randrange, randint

BASE_DIR = Path(__file__).resolve().parent.parent

def get_ua_agents():
    with open(os.path.join(BASE_DIR,'user-agents.txt')) as f:
        ua_texts=f.read()
        ua_texts.replace('\n',' ')
        ua_agents=ua_texts.split('Mozilla')
        for index in range(0, len(ua_agents)):
            ua_agents[index] = f'Mozilla{ua_agents[index]}'
            ua_agents[index] = ua_agents[index].replace('\n','')
    return ua_agents
def set_sel_prxy(myProxy):
    """takes ip proxy as args
    returns selenium proxy object"""
    return Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': myProxy,
        'ftpProxy': myProxy,
        'sslProxy': myProxy,
        'noProxy': myProxy})

def get_prxy_list():
    r = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps')
    prxyList=[]
    try:
        data=r.json()
        print(data['data'])
        for i in data['data']:
            pry=i['ip']+':'+i['port']
            prxyList.append(pry)
    except Exception as e:
        print('Proxy timeout limit:'+str(e))
        print(r.status_code)
    return prxyList
def create_driver_profile(agents, ip, port):
    profile = FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', ip)
    profile.set_preference('network.proxy.http_port', int(port))
    #profile.set_preference('network.proxy.https', ip)
    #profile.set_preference('network.proxy.https_port', int(port))
    #profile.set_preference('network.proxy.verify_ssl', False)
    #profile.set_preference('network.proxy.ssl', ip)
    #profile.set_preference('network.proxy.ssl_port', int(port))
    #profile.set_preference('network.proxy.socks_version', 5)
    #profile.set_preference('network.proxy.socks', ip)
    #profile.set_preference('network.proxy.socks_port', int(port))
    profile.set_preference("network.http.use-cache", False)
    profile.set_preference('general.useragent.override',f'userAgent={agents}')
    profile.update_preferences()
    return profile
    
def get_driver_options(ip,port):
    options = firefox_options()
    options.set_preference("acceptInsecureCerts", True)
    options.log.level="trace"
    ua_agents = get_ua_agents()
    agents=ua_agents[randrange(0,len(ua_agents))]
    options.add_argument(f'--user-agent={agents}')
    options.headless=True
    options.profile = create_driver_profile(agents,ip,port)
    return options
def firefoxdriver(prxy):
    proxy=set_sel_prxy(prxy)
    binary = FirefoxBinary(os.path.join(BASE_DIR,'Mozilla Firefox\\firefox.exe'))
    ##service = FirefoxService()
    ip,port=prxy.split(':')
    options=get_driver_options(ip,port)
    driver = FirefoxDriver(options=options,executable_path=os.path.join(BASE_DIR,'geckodriver.exe'),firefox_binary=binary,proxy=prxy)
    return driver
def click(driver,div):
    global click_count
    try:
        hover = ActionChains(driver).move_to_element(div)
        hover.click().perform()
    except Exception as e:
        print(str(e))
    finally:
        handles=driver.window_handles
        driver.switch_to.window(handles[0])
        click_count += 1
        c=driver.current_window_handle

def click_frames(driver, locator):
    global click_count
    frames=WebDriverWait(driver,1000).until(EC.presence_of_all_elements_located(locator))
    for frame in frames:
        try:
            i_frame=WebDriverWait(driver,10).until(EC.frame_to_be_available_and_switch_to_it(frame))
            click_frame(i_frame)
        except Exception as e:
            print(str(e))
            continue
def click(driver,div):
    global click_count
    try:
        hover = ActionChains(driver).move_to_element(div)
        hover.click().perform()
    except Exception as e:
        print(str(e))
    finally:
        handles=driver.window_handles
        driver.switch_to.window(handles[0])
        click_count += 1
        c=driver.current_window_handle
def click_divs(driver):
    global click_count
    divs=WebDriverWait(driver,100).until(EC.presence_of_all_elements_located((By.XPATH,"/html/div")))
    for div in divs:
        try:
            hover = ActionChains(driver).move_to_element(div)
            hover.click().perform()
        except Exception as e:
            print(str(e))
        finally:
            handles=driver.window_handles
            driver.switch_to.window(handles[0])
            click_count += 1
            c=driver.current_window_handle
        #EC.presence_of_element_located((By.CSS_SELECTOR,f"div[style='{style}']")))
        #EC.presence_of_element_located((By.CLASS_NAME,class_name)))

def click_frame(driver,i_frame):
    global click_count
    driver.switch_to.frame(i_frame)
    ad =  WebDriverWait(driver,1000).until(EC.presence_of_element_located(By.TAG_NAME,'html'))
    ad.click()
    try:
        driver.switch_to.default_content()
    except Exception as e:
        print(str(e))
    finally:
        handles=driver.window_handles
        driver.switch_to.window(handles[0])
        click_count += 1
def start_scraping(driver,url):
    try:
        global click_count
        driver.execute_script('Object.defineProperty(navigator,"webdriver",{get: ()=>undefined})')
        driver.get(url)
        driver.delete_all_cookies()
        html = driver.page_source
        print(html)
        driver.get(url)
        print("Page title: "+ driver.title)
        try:
            uri ='https://diclotrans.com/redirect?id=19334&auth=c506479a454684638d2c7b8d647d9387b57c714e'
            x_path='//a[@href="'+uri+'"]'
            link=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,x_path)))
            click(driver,link)
        except Exception as e:
            print(str(e))
            try:
                click_divs(driver)
            except Exception as e:
                print(str(e))
                try:
                    locator=(By.TAG_NAME,"iframe")
                    click_frames(driver,locator)
                except Exception as e:
                    print(str(e))
                    try:
                        locator=(By.XPATH,"/html/iframe")
                        click_frames(driver,locator)
                    except Exception as e:
                        print(str(e))
                        
        print(click_count)
        print(driver.execute_script('return navigator.userAgent'))
    except Exception as e:
        print('Timeout Exception error:'+str(e))
    finally:
        driver.close()
        driver.quit()


def start_single_scrape(url):
    try:
        r=requests.get('http://pubproxy.com/api/proxy?https=true')
        data=r.json()
        my_data=data['data']
        prxy_data=my_data[0]
        prxy=prxy_data['ip']+':'+prxy_data['port']
        print(data)
        driver=firefoxdriver(prxy)
        start_scraping(driver,url)
    except Exception as e:
        print('Proxy timeout limits:'+str(e))
def thread_action(url,batch=[]):
    for prxy in batch:
        try:
            driver=firefoxdriver(prxy)
            driver.set_window_size(340,695)
            start_scraping(driver,url)
        except Exception as e:
            print('Proxy Exception error:'+str(e))
def start_scraping_threads(url):
    prxy_list=get_prxy_list()
    if len(prxy_list) > 0:
        thread_count=len(prxy_list)/100
        for i in range(0,len(prxy_list),100):
            batch =prxy_list[i:i+100]
            scraping_thread = threading.Thread(target=thread_action,args=(url,batch))
            scraping_thread.start()
def launchScraper(url):
    try:
        start_single_scrape(url)
    except Exception as e:
        print(f'Data not found :{str(e)}')
    finally:
        start_scraping_threads(url)
click_count=0
def start_main_loop(prxy_flag):
    global click_count
    total_clicks = 6273
    count_break = randint(4777,total_clicks)
    url="https://tpsychic.onrender.com/"
    koyeb_url="https://tdemo-safuh.koyeb.app/"
    if prxy_flag :
        while click_count <= count_break:
            url_thread = threading.Thread(target=no_proxy_scrape,args=(url,))
            ua_thread = threading.Thread(target=ua_scrape,args=(url,))
            url_thread.start()
            ua_thread.start()
    else:
        while click_count <= count_break:
            print(f"loop counter :{click_count}")
            ua_thread = threading.Thread(target=ua_scrape,args=(url,))
            ua_thread.start()
            launchScraper(url)
        #url_thread = threading.Thread(target=launchScraper,args=(url,click_count))
        #koyeb_url_thread = threading.Thread(target=launchScraper,args=(koyeb_url,click_count))
        #url_thread.start()
        #koyeb_url_thread.start()

def with_ua():
    binary = FirefoxBinary(os.path.join(BASE_DIR,'Mozilla Firefox\\firefox.exe'))
    options = firefox_options()
    options.add_argument('--dsiable-blink-features=AutomationControlled')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    ua_agents = get_ua_agents()
    agents=ua_agents[randrange(0,len(ua_agents))]
    options.add_argument(f'--user-agent={agents}')
    options.headless=True
    #service = FirefoxService()
    driver = FirefoxDriver(options=options,executable_path=os.path.join(BASE_DIR,'geckodriver.exe'),firefox_binary=binary)
    return driver
    
def bilaproxy():
    binary = FirefoxBinary(os.path.join(BASE_DIR,'Mozilla Firefox\\firefox.exe'))
    options = firefox_options()
    options.add_argument('--dsiable-blink-features=AutomationControlled')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.headless=True
    #service = FirefoxService()
    driver = FirefoxDriver(options=options,executable_path=os.path.join(BASE_DIR,'geckodriver.exe'),firefox_binary=binary)
    return driver
def no_proxy_scrape(url):
    try:
        driver=bilaproxy()
        #driver.set_window_size(340,695)
        start_scraping(driver,url)
    except Exception as e:
        print('Proxy timeout limits:'+str(e))
def ua_scrape(url):
    try:
        driver=with_ua()
        driver.set_window_size(340,695)
        start_scraping(driver,url)
    except Exception as e:
        print('Proxy timeout limits:'+str(e))

if __name__ == "__main__":
    start_main_loop(True)

#binary = FirefoxBinary(os.path.join(BASE_DIR,'Mozilla Firefox\\firefox.exe'))
#driver = FirefoxDriver(executable_path=os.path.join(BASE_DIR,'geckodriver.exe'),firefox_binary=binary)
#url="https://tpsychic.onrender.com/"
#click_count=0
#start_scraping(driver,url,click_count)
#print(click_count)
##def setChromeDriver(prxyList):
##	options =chrome_options()
##	options.add_argument('user-agent=<ua>')
##	options.headless=True
##	prxy=selProxy(prxyList[-1])
##	prxyList=getPrxylist.pop()
##	driver=webdriver.Chrome(proxy=prxy,options=options,executable_path=os.path.join(BASE_DIR,'chromedriver.exe'))
##	return driver
##def dailyusage(driver,url,savedCookies):
##	driver.get(url)
##	driver.delete_all_cookies()
##	for cookie in savedCookies:
##		if not cookie['domain'].startsWith('.'):
##			cookie['domain'] = f'.{cookie['domain']}'
##		driver.add_cookie(cookie)
##	driver.get(url)
##	driver.get_cookies()
##	return driver
##def adHandle(driver,c):
##    """opens ad page"""
##    for i in driver.window_handles:
##        if i != c:
##            d = i
##            driver.switch_to.window(d)
##            break
##        print("Ad title: "+ driver.title)
##        driver.switch_to.window(c)
##        break
##    print("Main Page title: "+ driver.title)
##    return
##def doClick(button,driver):
##    """takes an element and simulates clicks"""
##    hover = ActionChains(driver).move_to_element(button)
##    hover.click().perform()
##    time.sleep(5)
##    c=driver.current_window_handle
##    adHandle(driver,c)
##    return

def setChromeDriver():
    ua_agents = get_ua_agents()
    agent = ua_agents[randrange(0,len(ua_agents))]
    options =chrome_options()
    options.add_argument(f'user-agent={agent}')
    options.headless=False
    service=Service(executable_path=os.path.join(BASE_DIR,'chromedriver.exe'))
    driver=webdriver.Chrome(options=options,service=service)
    return driver
