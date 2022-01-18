from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def init_selenium_browser() -> None:

    opts = Options()
    opts.binary_location = BINARY_PATH
    opts.add_experimental_option('prefs', {'intl.accept_languages': 'es-ES'})
    opts.add_experimental_option('detach', True)
    opts.headless = HEADLESS
    driver = webdriver.Chrome(
        executable_path = DRIVER_PATH,
        options         = opts
    )

    return driver