# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe", headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("https://example.com")
#     print(page.title())
#     browser.close()


import os
import time
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class pyAMZON:

    def __init__(self, mute=False, invisible=True, run=True):
        self.DIR = os.path.dirname(os.path.realpath(__file__))
        self.passwords = self.load(os.path.join(self.DIR, 'passwords.json'))

        # Logging setup
        log_name_time = datetime.now().strftime('%Y%m%d%H%M')
        self.log = logging.getLogger(name=log_name_time + '.log')
        self.log.setLevel(logging.DEBUG)
        self.log.dir = self.DIR
        self.log.filename = os.path.join(self.DIR, 'log')
        fh = RotatingFileHandler(filename=self.log.filename, encoding='utf-8', maxBytes=25*1024*1024, backupCount=10)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.log.addHandler(fh)

        self.log.info('Started script')

        print("This will obtain a list of all your Amazon purchases and save it as a CSV.")

        if run:
            self.year = int(input("What year should we get?\n"))
            self.log.info(f'Year: {self.year}')
            self.get_data()

    def get_data(self):
        self.log.info('Getting data')
        
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe", headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to Amazon orders page
            page.goto('https://www.amazon.com/gp/your-account/order-history/')

            # Log in
            try:
                self.log.info('Entering email...')
                page.fill('input[name="email"]', self.passwords['email'])
                page.click('input[type="submit"]')
                self.log.info('Entering password...')
                page.fill('input[name="password"]', self.passwords['password'])
                page.click('input[type="submit"]')

                # Wait for login to complete
                page.wait_for_timeout(3000)
                self.log.info('Login complete')
            except Exception as e:
                self.log.error(f'Login error: {e}')

            captcha = False
            try: 
                captcha = page.locator('form.cvf-widget-form-captcha')
                # captcha = page.locator('div.cvf-captcha-img')
            except:
                pass

            print('captcha', captcha.count())
            
            print()
            if captcha.count() == 0:
                print("done signing in")
                self.log.info('sign in complete')
            else:
                self.log.warning('triggered Captcha')
                print('😖😖😖')
                print('sign in failed, due to captcha')
                print('1️⃣','pass captcha')
                print('2️⃣' ,'then press enter to continue')
                input('') # this will pause until the user passes captcha
                print('...starting back up')

            self.log.info('captcha passed... thanks')

            
            # Navigate to order history
            order_url = f'https://www.amazon.com/gp/your-account/order-history?orderFilter=year-{self.year}'
            page.goto(order_url)

            # Wait for orders to load
            page.wait_for_timeout(3000)

            # order_details = []
            invoice_links = []

            while True:
                self.log.info('Collecting order links')
                orders = page.locator('.order-info')

                for order in orders.element_handles():
                    links = order.query_selector_all('.a-link-normal')
                    for link in links:
                        href = link.get_attribute('href')
                        if 'print.html' in href and href not in invoice_links:
                            invoice_links.append(href)
                        # elif 'order-details' in href and href not in order_details:
                        #     order_details.append(href)

                # Check for next page
                next_button = page.locator('.a-last a')
                if next_button.is_visible():
                    next_button.click()
                    page.wait_for_timeout(3000)
                else:
                    break

            # print(*invoice_links,sep='\n')

            # Collecting order data
            items = []
            for link in invoice_links:
                self.log.info(f'Processing invoice: {link}')
                page.goto(f'https://www.amazon.com{link}')
                page.wait_for_timeout(500)

                # try:
                #     # //*[@id="pos_view_content"]/table/tbody/tr/td/table/tbody/tr[1]/td/b
                #     order_date = page.locator('//td[contains(text(), "Order Placed:")]').inner_text().replace('Order Placed: ', '')
                #     order_date = datetime.strptime(order_date, "%B %d, %Y").strftime("%Y%m%d")
                # except Exception as e:
                #     order_date = '*ERROR*'
                #     self.log.error(f'Order date error: {e}')

                try:
                    order_date_element = page.locator('//td[./b[contains(text(), "Order Placed:")]]')
                    order_date_raw = order_date_element.inner_text()
                    order_date = order_date_raw.replace('Order Placed:', '').strip()
                    order_date = datetime.strptime(order_date, "%B %d, %Y").strftime("%Y%m%d")
                except Exception as e:
                    order_date = '*ERROR*'
                    self.log.error(f'Order date error: {e}')

                soup = BeautifulSoup(page.content(), 'html.parser')
                rows = soup.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) == 2:
                        item_name = tds[0].text.strip().replace('\n','').replace('\t','')
                        price = tds[1].text.strip()
                        if 'Sold by:' in item_name :
                            items.append({
                                'invoice': f'https://www.amazon.com{link}',
                                'order_date': order_date,
                                'name': item_name,
                                'price': price
                            })

            output_file = os.path.join(self.DIR, f'results_{self.year}.csv')
            pd.DataFrame(items).to_csv(output_file, index=False)
            self.log.info(f'Saved: {output_file}')
            print(f'Saved: {output_file}')

            browser.close()

    def load(self, filepath):
        with open(filepath, 'r') as file:
            return json.load(file)

if __name__ == "__main__":
    pyAMZON()
