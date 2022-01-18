import time, os

# selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# local modules
from . import _vars, misc
from cfg import *


class Browser:

    def __init__(self):

        opts = Options()
        opts.binary_location = LINUX_BINARYPATH if os.name != 'nt' else NT_BINARYPATH
        opts.headless = HEADLESS
        opts.add_argument(f"user-data-dir={USERDATA_PATH}") 
        opts.add_experimental_option('prefs', {'intl.accept_languages': 'es-ES'})
        opts.add_experimental_option('detach', True)
        opts.headless = HEADLESS
        self.driver = webdriver.Chrome(
            executable_path = LINUX_DRIVERPATH if os.name != 'nt' else NT_DRIVERPATH,
            options = opts
        )


    def hsignin(self, username: str, password: str) -> bool:

        try:
            self.driver.get(U_STEAM_SIGNIN)

        except Exception as e:
            print('There was an error trying to access steam\'s login page', e)
            raise e

        # type in username
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables["login"]["input_username"]
            ))).send_keys(username)

        except Exception as e:
            print('There was an error trying to type in username', e)
            raise e

        # type in password
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables["login"]["input_password"]
            ))).send_keys(password)

        except Exception as e:
            print('There was an error trying to type in password', e)
            raise e

        # press login btn
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables["login"]["signin_button"]
            ))).click()

        except Exception as e:
            print('There was an error trying to click on submit', e)
            raise e
        
        # if steamguard modal is open, handle steamguard authentication
        try:
            _ = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                '/html/body/div[3]/div[3]/div/div/div' # TODO: save in xpath_variables
            )))

            self.hsteamguard_auth(self.driver)
        except:
            pass

        return True


    def hsteamguard_auth(self, driver: webdriver):

        # type in auth code
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables["login"]["twofactorcode_input"]
            ))).send_keys(
                input('Please type Steam Guard code: ')
            )

        except Exception as e:
            misc.save_screenshot(self.driver, 'hsteamguard_auth')
            print('There was an error trying to type in steamguard code', e)
            raise e

        # submit
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables["login"]["twofactorcode_code"]
            ))).click()

            time.sleep(5)
            misc.save_screenshot(self.driver, 'hsteamguard_auth') # after steamguard code submit
        except Exception as e:
            print('There was an error trying to submit steamguard code', e)
            raise e

        return


    def hpurchase_item(self, listings_url: str, market_action_script: str) -> bool:

        try:
            self.driver.get(listings_url)

        except Exception as e:
            print('There was an error trying to access listings page', e)
            raise e

        # execute market_action_script on every page to open buy_modal
        try:
            self.find_right_page(market_action_script)
        except Exception as e:
            raise e

        # Accept legal terms (sometimes this checkbox doesn't appear)
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables['market_purchase']['accept_ssa']
            ))).click()

        except:
            pass
        
        # Press buy btn
        try:

            misc.save_screenshot(self.driver, 'hpurchase_item') # save screenshot
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables['market_purchase']['btn_buy']
            ))).click()

            time.sleep(1)
        except Exception as e:
            raise e

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                _vars.xpath_variables['market_purchase']['dialog_close']
            ))).click()
    
        except Exception as e:
            raise e

        return True


    def find_right_page(self, market_action_script: str):

        page_count = 1
        page_limit = 5

        while page_count <= page_limit:
            self.driver.execute_script(market_action_script)

            print('# Going to the next page ...')
            try:
                self.handle_next_page()
            except:
                break

            page_count += 1
            time.sleep(1)


    def handle_next_page(self):

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="searchResults_btn_next"]' # TODO: save in xpath_variables
            ))).click()

        except Exception as e:
            raise e


    def exit(self):
        self.driver.close()
        self.driver.quit()

