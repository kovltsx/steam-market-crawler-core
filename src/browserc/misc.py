import  time, string, random
from os.path import join

from selenium import webdriver
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    StaleElementReferenceException
)

import cfg as config


def hclick(driver, click_object, rand=True) -> bool:

    try:
        size = click_object.size
    except StaleElementReferenceException:
        print("There was an error on hclick func: StaleElementReferenceException")
        return False

    sizeList = list(size.values())
    height = int(sizeList[0])-1
    width = int(sizeList[1])-1
    if rand == True:
        try:
            height_rand = random.randint(1,height)
        except ValueError:
            height_rand = 1
        try:
            width_rand = random.randint(1,width)
        except ValueError:
            width_rand = 1
    if rand == False:
        height_rand = height
        width_rand = width
    action = webdriver.common.action_chains.ActionChains(driver)

    try:
        action.move_to_element_with_offset(click_object, width_rand, height_rand)
    except StaleElementReferenceException:
        return False
    action.click()

    try:
        action.perform()
    except MoveTargetOutOfBoundsException:
        return False
    except StaleElementReferenceException:
        return False

    return True


def hwrite(driver, elem, text) -> None:

    # init
    actions = webdriver.common.action_chains.ActionChains(driver)
    actions.move_to_element(elem)
    actions.click()

    # set writing in time
    for c in text:
        a, b = 0.1, 0.2 # 0.2, 0.3
        # Aumentamos espera para caracteres: !"#$%&'()*+,-./:;<=>?@[\]^_` {|}~
        if c in string.printable[62:]:
            a, b = a + 0.1, b + 0.2
        actions.pause(random.uniform(a, b))
        actions.send_keys(c)
    
    # Execute
    actions.perform()


def save_screenshot(driver: webdriver, ctx: str):
    ext = '.png'
    f = f'{ctx}_' + time.strftime("%d-%M-%y_%H:%M:%S") + ext
    path = join(config.LOGS_PATH, f)

    print('save_screenshot path:', path)

    try:
        el = driver.find_element_by_tag_name('body')
        el.screenshot(path)
    except Exception as e:
        print('There was an error trying to get screenshot', e)
        raise e

    return