import random
import sys
from datetime import datetime
from time import sleep

import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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


def take_screenshot(driver, filename):
    driver.save_screenshot(filename)
    return cv2.imread(filename)


def find_and_click(driver, screen, template_path, threshold=0.8):
    screenshot = take_screenshot(driver, 'screenshot.png')
    _, W, H = screenshot.shape[::-1]

    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        top_left = pt
        bottom_right = (top_left[0] + w, top_left[1] + h)
        centre = (bottom_right[0] + top_left[0]) / 2, (bottom_right[1] + top_left[1]) / 2

        ActionChains(driver).move_to_element_with_offset(screen, centre[0] - W / 2, centre[1] - H / 2).click().perform()
        sleep(5)
        break


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
    screen = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'layaCanvas')))

    # print("Closing FUCKING window...")
    # find_and_click(driver, screen, 'templates/quxiao.png')

    driver.save_screenshot('0.png')

    print("Closing windows...")
    for _ in range(3):
        find_and_click(driver, screen, 'templates/close_window.png')
    driver.save_screenshot('1.png')

    print("Clicking sign-in button...")
    find_and_click(driver, screen, 'templates/fuli_button.png')
    driver.save_screenshot('2.png')

    find_and_click(driver, screen, 'templates/meiriqiandao_button.png')
    driver.save_screenshot('3.png')

    find_and_click(driver, screen, 'templates/qiandao_button.png')
    driver.save_screenshot('4.png')

    find_and_click(driver, screen, 'templates/close_window.png')
    driver.save_screenshot('5.png')

    print("Navigating to 免费武将包...")
    find_and_click(driver, screen, 'templates/wujiang_button.png')  # Click 武将 button
    driver.save_screenshot('6.png')

    print("Clicking 招武将...")
    find_and_click(driver, screen, 'templates/zhaowujiang_button.png')
    driver.save_screenshot('7.png')

    # 获取当前日期中的日（number of the day in the month）
    current_day = datetime.now().day

    # 根据当前日期延迟相应秒数
    sleep(current_day * 60)

    print("Clicking open once...")
    find_and_click(driver, screen, 'templates/kaiqiyici_button.png')
    driver.save_screenshot('8.png')

    print("Clicking cancel to prevent purchase...")
    find_and_click(driver, screen, 'templates/quxiao_button.png')
    driver.save_screenshot('9.png')

    print("Closing windows...")
    for _ in range(3):
        find_and_click(driver, screen, 'templates/close_window.png')

    print("Clicking more to access 发财树...")
    find_and_click(driver, screen, 'templates/gengduo_button.png')
    driver.save_screenshot('10.png')

    print("Clicking money tree...")
    find_and_click(driver, screen, 'templates/facaishu_button.png')
    driver.save_screenshot('11.png')

    print("Clicking 斧头...")
    find_and_click(driver, screen, 'templates/futou_button.png')
    driver.save_screenshot('12.png')

    print("Randomly clicking on 桃子区域...")
    click_random_points(driver, screen, (-241, 170), (285, 273))
    driver.save_screenshot('13.png')

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
        sleep(60)

        print("Performing game actions...")
        perform_game_actions(driver)

        print("Waiting for two hours...")
        # WebDriverWait(driver, 7200).until(lambda d: False)
        print("Script finished.")


if __name__ == "__main__":
    main()
