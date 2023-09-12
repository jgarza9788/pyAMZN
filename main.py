import sys
import os, re, time
import json5 as json
import logging 
from logging import Logger
from logging.handlers import RotatingFileHandler
import pandas as pd
from datetime  import datetime
import selenium.common.exceptions as seleniume
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

def ask(prompt, datatype):
    '''
    Prompts the user for input and returns the input value of the specified datatype.

    Args:
        prompt (str): The prompt to display to the user.
        datatype (type): The expected datatype of the input.

    Returns:
        The input value of the specified datatype.

    Raises:
        TypeError: If `datatype` is not a valid Python type.
        ValueError: If the input value does not match the specified datatype.

    Example:
        >>> name = ask("Enter your name:", str)
        Enter your name:
        John Doe
        >>> print(name)
        John Doe
    '''

    prompt = str(prompt)

    if not isinstance(datatype, type):
        raise TypeError('datatype should be a type (i.e. str, int, float, etc)')

    done = False
    while not done:
        try:
            if datatype != list:
                i = datatype(input(prompt + '\n'))
                return i
            else:
                i = input(prompt + '? \n')
                i = i.split(',')
                if len(i) == 0:
                    return []
                else:
                    return i
        except ValueError:
            print('***ERROR*** it should be a ' + datatype.__name__ + ', try again')
        except TypeError:
            print('***ERROR*** it should be a ' + datatype.__name__ + ', try again')
        except Exception:
            print('***ERROR*** An unexpected error occurred, please try again')

def bar(num,denom,length=50,fillchar='#',emptychar=' '):
    fillnum = ((int)( (num/denom) * length))
    return '[' + ( fillnum * fillchar ).ljust(length,emptychar)  + ']'

class pyAMZON():

    def __init__(self,mute=False,invisible=True):
        self.DIR = os.path.dirname(os.path.realpath(__file__))
        self.passwords = self.load(os.path.join(self.DIR,'passwords.json'))

        # log
        log_name_time = datetime.now().strftime('%Y%m%d%H%M')
        self.log = logging.getLogger(name=log_name_time + '.log')
        self.log.setLevel(logging.DEBUG)
        self.log.dir = self.DIR
        self.log.filename = os.path.join(self.DIR, 'log')
        fh = RotatingFileHandler(filename=self.log.filename,encoding='utf-8',maxBytes=25*1024*1024,backupCount=10)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
            )
        fh.setFormatter(formatter)
        self.log.addHandler(fh)


        self.log.info('started script')

        print("This will obtain a list of all your Amazon purchases and save it as a csv.")

        while True:
            self.year = ask("what year should we get?",int)
            # self.year = 2022
            self.log.info(f'Year {self.year}')
            self.get_data()

    def wait(self,t=1):
        for i in range(t):
            print('{0}/{1}'.format(i+1,t),end='\r')
            time.sleep(1)

    def get_data(self):
        self.log.info('getting data')

        result = []

        self.b = self.get_browser()
        # time.sleep(1000)
        self.b.get('https://www.amazon.com/gp/your-account/order-history/')

        try:
            print('entering email...')
            self.log.info('entering email...')
            emailField = self.b.find_element(By.CSS_SELECTOR,'input[name=email]')
            emailField.send_keys(self.passwords["email"])
            self.b.find_element(By.CSS_SELECTOR,'input[type=submit]').click()
        except Exception as ex:
            print(ex)
            self.log.error(ex)

        try:
            print('entering password...')
            self.log.info('entering password...')
            passwordField = self.b.find_element(By.CSS_SELECTOR,'input[name=password]')
            passwordField.send_keys(self.passwords["password"])
            self.b.find_element(By.CSS_SELECTOR,'input[type=submit]').click()
        except Exception as ex:
            print(ex)
            self.log.error(ex)

        captcha = False
        try: 
            captcha = self.b.find_element(By.CLASS_NAME,'cvf-widget-input-captcha')
        except:
            pass

        try: 
            captcha = self.b.find_element(By.CSS_SELECTOR,'input[name=guess]')
            # captcha = self.b.find_element(By.CLASS_NAME,'cvf-widget-input-captcha')
        except:
            pass

        # print('captcha', captcha)
        
        print()
        if captcha == False:
            print("done signing in")
            self.log.info('sign in complete')
        else:
            self.log.warn('triggered Captcha')
            print('😖😖😖')
            print('sign in failed, due to captcha')
            print('1️⃣','pass captcha')
            print('2️⃣' ,'then press enter to continue')
            input('') # this will pause until the user passes captcha
            print('...starting back up')

        self.log.info('captcha passed... thanks')

        self.wait(3)
        
        self.b.get(f'https://www.amazon.com/gp/your-account/order-history?orderFilter=year-{self.year}')

        print('loading...')
        self.wait(3)

        invoice_links = []
        order_detail_links = []
        count_il = -1 


        self.log.info('collecting order info')
        order_infos = self.b.find_elements(By.CLASS_NAME,'order-info')

        order_card_loop = True
        while order_card_loop:

            for oi in order_infos:
                for uli in oi.find_elements(By.CLASS_NAME,'a-link-normal'):
                    uliurl = uli.get_attribute('href')
                    try:
                        if 'print.html' in uliurl:
                            if uliurl not in invoice_links:
                                invoice_links.append(uliurl)
                        elif 'order-details' in uliurl:
                            if uliurl not in order_detail_links:
                                order_detail_links.append(uliurl)

                    except:
                        pass

            try:
                next_button = self.b.find_element(By.CLASS_NAME,'a-last')
                next_button.click()
            except:
                pass

            order_infos = self.b.find_elements(By.CLASS_NAME,'order-info')

            if len(invoice_links) == count_il:
                order_card_loop = False
            
            count_il = len(invoice_links)

        #name links and category list    
        nlc_list = []

        self.log.info('collecting name,links, and category')
        for index,odl in enumerate(order_detail_links):
            print(bar(index+1,len(order_detail_links)),end='\r')
            self.b.get(odl)
            items = self.b.find_elements(By.CLASS_NAME,'yohtmlc-item')
            for i in items:
                a_link = i.find_element(By.TAG_NAME,'a')
                name = a_link.get_attribute('innerText')
                link = a_link.get_attribute('href')
                # print(name,link,'\n')
                nlc_list.append(
                    {
                        'name': name,
                        'link': link
                    }
                )
        
        for index,nlc in enumerate(nlc_list):
            print(bar(index+1,len(nlc_list)),end='\r')
            try:
                self.b.get(nlc['link'])
                bc = self.b.find_element(By.ID,'wayfinding-breadcrumbs_feature_div')
                nlc['category'] = bc.find_elements(By.CLASS_NAME,'a-link-normal')[0].get_attribute('innerText')
            except Exception as ex:
                print(ex)
                pass
            

        # print(*nlc_list,sep='\n')

        self.log.info('collecting item list')
        item_list = []
        for index,i in enumerate(invoice_links):
            print(bar(index+1,len(invoice_links)),end='\r')
            self.b.get(i)
            body = self.b.find_element(By.TAG_NAME,'body')

            # for t in tables:
            soup = BeautifulSoup(body.get_attribute("innerHTML"), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                try:
                    tds = row.find_all('td')
                    if len(tds) == 2:
                        item_name = tds[0].find('i').text.strip()
                        price = tds[1].text.strip()

                        category = '???'

                        for nlc in nlc_list:
                            if nlc['name'] == item_name:
                                category = nlc['category']

                        item_list.append({'invoice': i,'name': item_name, 'category': category, 'price': price})
                except:
                    pass

        # print(*item_list,sep='\n')

        outputfile = os.path.join(self.DIR,'results_{0}.csv'.format(self.year))
        pd.DataFrame(item_list).to_csv(outputfile,index=False)
        print('saved: ', outputfile)
        self.log.info(f' saved: {outputfile}')

        self.b.quit()

    def clean_price_string(self,s):
        # print('\'' + s + '\'')
        return re.sub('(\$|,| )','',s)

    def get_browser(self,visible= True):
        # #options
        # options = webdriver.ChromeOptions()
        # options.add_argument('test-type')
        # options.add_argument('--js-flags=--expose-gc')
        # options.add_argument('--enable-precise-memory-info')
        # options.add_argument('--disable-popups-blocking')
        # options.add_argument('--disable-default-apps')
        # options.add_argument('test-type=browser')
        # options.add_argument('disable-infobars')
        # options.add_argument('window-size=800x600')
        # options.add_argument('log-level=3')

        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # # options.add_argument("user-data-dir=C:\\Users\\JGarza\\AppData\\Local\\Google\\Chrome\\User Data\\Default") 

        if visible == False:
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode

        service = Service(executable_path=os.path.join(self.DIR,'chromedriver.exe'))
        return webdriver.Chrome(service = service,options=chrome_options)

    def load(self, filepath):
        with open(filepath,'r') as file:
            return json.load(file)

    def save(self,filepath, data):
        with open(filepath,'w') as file:
            file.write(json.dumps(data,indent=4))


if __name__ == "__main__":
    
    pAZ = pyAMZON()
    


