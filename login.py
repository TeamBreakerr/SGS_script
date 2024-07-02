import random
import sys
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    return driver


def login(driver, email, password):
    print("Navigating to login page...")
    driver.get("https://web.sanguosha.com/login/index.html")

    print("Entering email...")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'SGS_login-account'))).send_keys(email)

    print("Entering password...")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'SGS_login-password'))).send_keys(password)

    print("Accepting user agreement...")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'SGS_userProto'))).click()

    print("Performing login...")
    login_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'SGS_login-btn')))
    ActionChains(driver).move_to_element(login_btn).click().perform()
    print("Login successful.")


def click_with_offset(driver, element, x_offset, y_offset, wait_time=1):
    ActionChains(driver).move_to_element_with_offset(element, x_offset, y_offset).click().perform()
    WebDriverWait(driver, wait_time).until(lambda d: True)  # Simple wait


def click_random_points(driver, element, top_left, bottom_right, num_clicks=10):
    """
    在指定元素的给定区域内随机点击若干点。

    参数:
    driver -- WebDriver 实例。
    element -- Selenium 元素，点击动作的基础位置。
    top_left (tuple) -- 区域的左上角坐标 (x, y)。
    bottom_right (tuple) -- 区域的右下角坐标 (x, y)。
    num_clicks (int) -- 要执行的点击次数，默认为10次。
    """
    for _ in range(num_clicks):
        # 生成随机坐标点
        x = random.randint(top_left[0], bottom_right[0])
        y = random.randint(top_left[1], bottom_right[1])

        # 使用 ActionChains 执行点击
        ActionChains(driver).move_to_element_with_offset(element, x, y).click().perform()


def perform_game_actions(driver):
    print("Waiting for game screen to load...")
    screen = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'layaCanvas')))

    print("Closing activity window...")
    click_with_offset(driver, screen, 342, -234)
    sleep(5)

    print("Clicking sign-in button...")
    click_with_offset(driver, screen, 408, 239)
    sleep(5)

    print("Closing additional windows...")
    for _ in range(3):
        click_with_offset(driver, screen, 512, -290)
        sleep(1)

    print("Navigating to 免费武将包...")
    click_with_offset(driver, screen, 646, 417)  # Click 武将 button
    sleep(5)

    print("Clicking 招武将...")
    click_with_offset(driver, screen, 463, 286)
    sleep(5)

    print("Clicking open once...")
    click_with_offset(driver, screen, -146, 190)
    sleep(5)

    print("Clicking cancel to prevent purchase...")
    click_with_offset(driver, screen, 62, 68)
    sleep(5)

    print("Closing windows...")
    for _ in range(3):
        click_with_offset(driver, screen, 529, -314)
        sleep(1)

    print("Clicking more to access 发财树...")
    click_with_offset(driver, screen, 925, 417)
    sleep(5)

    print("Clicking money tree...")
    click_with_offset(driver, screen, 836, 255)
    sleep(5)

    print("Clicking 斧头...")
    click_with_offset(driver, screen, 147, 40)
    sleep(5)

    print("Randomly clicking on 桃子区域...")
    click_random_points(driver, screen, (-312, 128), (356, 267))
    print("Completed game actions.")


def main():
    acccounts = int(len(sys.argv[1:]) / 2)
    print(f'Config {acccounts} accounts')
    for i in range(acccounts):
        email = sys.argv[1 + i]
        passwd = sys.argv[1 + i + acccounts]
        print('----------------------------')

        driver = setup_driver()

        print("Starting login process...")
        login(driver, email, passwd)

        print("Entering game...")
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'gameItemOl'))).click()
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'goInGameBtn'))).click()
        sleep(40)

        print("Performing game actions...")
        perform_game_actions(driver)

        print("Waiting for two hours...")
       # WebDriverWait(driver, 7200).until(lambda d: False)
        print("Script finished.")


if __name__ == "__main__":
    main()
