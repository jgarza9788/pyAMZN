import sys
import os, re, time
import json5 as json
import pandas as pd
from datetime  import datetime
from seleniumwire import webdriver 
import selenium.common.exceptions as seleniumex

def ask(prompt, datatype):
    '''
    '''

    prompt = str(prompt)

    if isinstance(datatype,type) == False:
        raise ValueError('datatype should be a type (i.e. str, int, float, etc)')

    done = False
    while done == False:
        try:
            if datatype != list:
                i = datatype(input( prompt + '\n'))
                return i
            else:
                i = input( prompt + '? \n')
                i = i.split(',')
                if len(i) == 0:
                    return []
                else:
                    return i
        except:
            print('***ERROR*** it should be a ' + datatype.__name__ + ', try again')


class pyAMZON():

    def __init__(self,mute=False,invisible=True):
        self.DIR = os.path.dirname(os.path.realpath(__file__))
        self.passwords = self.load(os.path.join(self.DIR,'passwords.json'))

        print("This will obtain a list of all your Amazon purchases and save it as a csv.")

        while True:
            self.year = ask("what year should we get?",int)
            # self.year = 2022
            self.get_data()

            

    def wait(self,t=1):
        for i in range(t):
            print('{0}/{1}'.format(i+1,t),end='\r')
            time.sleep(1)


    def get_data(self):

        result = []

        self.b = self.get_browser()
        # time.sleep(1000)
        self.b.get('https://www.amazon.com/gp/your-account/order-history/')


        print('entering email...')
        emailField = self.b.find_element_by_css_selector('input[name=email]')
        emailField.send_keys(self.passwords["email"])
        self.b.find_element_by_css_selector('input[type=submit]').click()

        print('entering password...')
        passwordField = self.b.find_element_by_css_selector('input[name=password]')
        passwordField.send_keys(self.passwords["password"])
        self.b.find_element_by_css_selector('input[type=submit]').click()


        captcha = False
        try: 
            captcha = self.b.find_element_by_css_selector('input[name=guess]')
        except:
            pass

        # print('captcha', captcha)
        
        print()
        if captcha == False:
            print("done signing in")
        else:
            print('😖😖😖')
            print('sign in failed, due to captcha')
            print('1️⃣','pass captcha')
            print('2️⃣' ,'then press enter to continue')
            x = input('') # this will pause until the user passes captcha
            print('...starting back up')

        self.wait(3)

        self.b.get(f'https://www.amazon.com/gp/your-account/order-history?orderFilter=year-{self.year}')

        print('loading...')
        self.wait(3)

        order_urls = []

        order_cards = self.b.find_elements_by_class_name('js-order-card')
        # print('number or orders: ',len(order_cards))

        order_card_loop = True
        while order_card_loop:

            if len(order_cards) < 10:
                order_card_loop = False

            for oc in order_cards:
                order_urls.append(oc.find_elements_by_class_name('a-link-normal')[0].get_attribute("href"))

            try:
                next_button = self.b.find_element_by_class_name('a-last')
                next_button.click()

                order_cards = self.b.find_elements_by_class_name('js-order-card')
            except:
                order_card_loop = False

        # for iurl,url in enumerate(order_urls):
        #     print(iurl,url)

        order_urls = list(set(order_urls))

        # for iurl,url in enumerate(order_urls):
        #     print(iurl,url)

        print('number of order urls',len(order_urls))

        for iurl,url in enumerate(order_urls):
            try:
                print('{0} / {1}'.format(iurl+1,len(order_urls)),end='\r')
                self.b.get(url)

                shipments = self.b.find_elements_by_class_name('shipment')

                for s in shipments:
                    item = s.find_element_by_class_name('yohtmlc-item')
                    item_rows = item.find_elements_by_class_name('a-row')

                    result_row = {}
                    result_row['url'] = url
                    result_row['item_name'] = item_rows[0].get_attribute("innerText")
                    result_row['qty'] = 1
                    result_row['price'] = None

                    try:
                        result_row['qty'] = s.find_element_by_class_name('item-view-qty').get_attribute("innerText").strip() 
                    except:
                        pass

                    for ir in item_rows:
                        irit = ir.get_attribute("innerText")
                        irit = irit.strip()
                        
                        if re.search('\d+.\d+',irit):
                            result_row['price'] = irit

                    result.append(result_row)
            
            except seleniumex.NoSuchElementException as nseex: # it's not a shipment... maybe it's a delivery

                deliveryItems = self.b.find_elements_by_class_name('deliveryItem')
                for di in deliveryItems:
                    result_row = {}
                    result_row['url'] = url
                    

                    temp = di.find_element_by_class_name('deliveryItem-details')
                    temp = temp.find_element_by_class_name('a-link-normal')
                    result_row['item_name'] = temp.get_attribute("innerText").strip()
                    result_row['qty'] = 1
                    result_row['price'] = di.find_element_by_class_name('deliveryItem-price').get_attribute("innerText").strip() 

                    result.append(result_row)

            except Exception as ex:
                print(ex)
                result_row = {}
                result_row['url'] = url
                result_row['note'] = 'error-sorry'
                result.append(result_row)

        self.b.close()

        
        df = pd.DataFrame(result)

        #removes the $ , and spaces
        df['price'] = df['price'].apply(self.clean_price_string)

        df['price'] = df['price'].astype(float,errors='ignore')
        df['qty'] = df['qty'].astype(float,errors='ignore')


        # print(df.dtypes)
        df['total'] = df['qty'] * df['price']

        outputfile = os.path.join(self.DIR,'results_{0}.csv'.format(self.year))
        df.to_csv(outputfile,index=False)

        print('saved: ', outputfile)


        time.sleep(1*60)

    def clean_price_string(self,s):
        # print('\'' + s + '\'')
        return re.sub('(\$|,| )','',s)


    def get_browser(self,visible= True):
        #options
        options = webdriver.ChromeOptions()
        options.add_argument('test-type')
        options.add_argument('--js-flags=--expose-gc')
        options.add_argument('--enable-precise-memory-info')
        options.add_argument('--disable-popups-blocking')
        options.add_argument('--disable-default-apps')
        options.add_argument('test-type=browser')
        options.add_argument('disable-infobars')
        options.add_argument('window-size=800x600')
        options.add_argument('log-level=3')
        # options.add_argument("user-data-dir=C:\\Users\\JGarza\\AppData\\Local\\Google\\Chrome\\User Data\\Default") 

        if visible == False:
            options.add_argument('headless')
        
        return webdriver.Chrome(executable_path=os.path.join(self.DIR,'chromedriver.exe'),options=options)

    def load(self, filepath):
        with open(filepath,'r') as file:
            return json.load(file)

    def save(self,filepath, data):
        with open(filepath,'w') as file:
            file.write(json.dumps(data,indent=4))


if __name__ == "__main__":
    
    pAZ = pyAMZON()


