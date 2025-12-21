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

            browser2 = p.chromium.launch(executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe", headless=False)
            page2 = browser2.new_context().new_page()

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

            time.sleep(5)
            
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
            order_url = f'https://www.amazon.com/your-orders/orders?timeFilter=year-{self.year}'
            page.goto(order_url)

            # Wait for orders to load
            page.wait_for_timeout(1000)

            # order_details = []
            invoice_links = []

            while True:
                self.log.info('Collecting order links')

                odl = page.query_selector_all('.a-link-normal')
                for link in odl:
                    href = link.get_attribute('href')
                    if 'order-details?orderID=' in href:
                        invoice_links.append(href)
                        self.log.info(f"{len(invoice_links)=}")

                # orders = page.locator('.order-info')

                # for order in orders.element_handles():
                #     links = order.query_selector_all('yohtmlc-order-details-link')
                #     for link in links:
                #         href = link.get_attribute('href')
                #         # if 'print.html' in href and href not in invoice_links:
                #         invoice_links.append(href)
                #         # elif 'order-details' in href and href not in order_details:
                #         #     order_details.append(href)

                # Check for next page
                next_button = page.locator('.a-last a')
                if next_button.is_visible():
                    self.log.info("next page")
                    next_button.click()
                    page.wait_for_timeout(3000)
                else:
                    break

            # print(*invoice_links,sep='\n')

            # Collecting order data
            items = []
            for link in invoice_links:
                self.log.info(f'Processing invoice: {link}')
                page.goto(f'https://www.amazon.com{link}', wait_until="domcontentloaded", timeout=60000)
                # page.wait_for_timeout(500)

                # try:
                #     # //*[@id="pos_view_content"]/table/tbody/tr/td/table/tbody/tr[1]/td/b
                #     order_date = page.locator('//td[contains(text(), "Order Placed:")]').inner_text().replace('Order Placed: ', '')
                #     order_date = datetime.strptime(order_date, "%B %d, %Y").strftime("%Y%m%d")
                # except Exception as e:
                #     order_date = '*ERROR*'
                #     self.log.error(f'Order date error: {e}')

                # try:
                #     order_date_element = page.locator('//td[./b[contains(text(), "Order Placed:")]]')
                #     order_date_raw = order_date_element.inner_text()
                #     order_date = order_date_raw.replace('Order Placed:', '').strip()
                #     order_date = datetime.strptime(order_date, "%B %d, %Y").strftime("%Y%m%d")
                # except Exception as e:
                #     order_date = '*ERROR*'
                #     self.log.error(f'Order date error: {e}')

                # soup = BeautifulSoup(page.content(), 'html.parser')
                # rows = soup.find_all('tr')
                # for row in rows:
                #     tds = row.find_all('td')
                #     if len(tds) == 2:
                #         item_name = tds[0].text.strip().replace('\n','').replace('\t','')
                #         price = tds[1].text.strip()
                #         if 'Sold by:' in item_name :
                #             items.append({
                #                 'invoice': f'https://www.amazon.com{link}',
                #                 'order_date': order_date,
                #                 'name': item_name,
                #                 'price': price
                #             })

                try:
                    soup = BeautifulSoup(page.content(), "html.parser")

                    # Order date (Amazon uses various spans/divs; this covers common cases)
                    order_date = soup.find("span", string=lambda x: x and "Order placed" in x)
                    if order_date:
                        order_date = order_date.find_next("span").get_text(strip=True)
                    
                    self.log.info(order_date)

                    # Items: name + price
                    # items = []
                    for i in soup.select("div.a-fixed-left-grid-inner"):
                        # self.log.info(f'{len(i)}')
                        # name_tag = i.select_one("a.a-link-normal")
                        # price_tag = i.select_one("span.a-color-price")
                        # quanity_tag = i.select_one("div.od-item-view-qty")
                        # if name_tag and price_tag:
                        #     name = name_tag.get_text(strip=True)
                        #     price = price_tag.get_text(strip=True)
                        #     qty = 1
                        #     if (quanity_tag):
                        #         qty = quanity_tag.get_text(strip=True)
                        #     # items.append((name, price))
                        #     items.append({
                        #         'invoice': f'https://www.amazon.com{link}',
                        #         'order_date': order_date,
                        #         'name': name,
                        #         'price': price,
                        #         'quality':qty
                        #     })
                        # self.log.info(f'{len(items)=}')

                            # right/left columns inside this item row
                        right = i.select_one("[data-component='purchasedItemsRightGrid']")
                        if not right:
                            continue  # skip non-item rows

                        # --- title ---
                        title_el = right.select_one("[data-component='itemTitle'] a.a-link-normal") \
                                or right.select_one("a.a-link-normal")
                        title = title_el.get_text(strip=True) if title_el else None


                        page2.goto(f'https://www.amazon.com{title_el.get("href")}'
                                   , wait_until="domcontentloaded", timeout=60000)
                        # page2.wait_for_selector("#wayfinding-breadcrumbs_feature_div")
                        # page2.wait_for_timeout(100)
                        breadcrumb = "N/A"
                        try:
                            breadcrumb_items = page2.locator("#wayfinding-breadcrumbs_feature_div li a")
                            crumbs = [breadcrumb_items.nth(i).inner_text().strip() 
                                    for i in range(breadcrumb_items.count())]
                            breadcrumb =  "-".join(crumbs)
                        except:
                            pass

                        # --- unit price ---
                        # prefer the screen-reader price; fall back to visible span if needed
                        price_el = right.select_one("[data-component='unitPrice'] .a-offscreen") \
                                or right.select_one("[data-component='unitPrice'] span[aria-hidden='true']")
                        price_text = price_el.get_text(strip=True) if price_el else None

                        # --- quantity (overlay badge in the left grid). Default to 1 if not present ---
                        qty_el = i.select_one(".od-item-view-qty > span")
                        qty = int(qty_el.get_text(strip=True)) if qty_el and qty_el.get_text(strip=True).isdigit() else 1

                        total = float(price_text.replace("$", "").replace(",", "").strip()) * int(str(qty).strip())

                        items.append({
                            'invoice': f'https://www.amazon.com{link}',
                            'order_date': order_date,
                            'name': title,
                            'price': price_text,
                            'quality':qty,
                            'total_price': total,
                            'breadcrumb': breadcrumb
                        }) 

                except Exception as e:
                    self.log.error(e)


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
