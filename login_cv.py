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

    # 初始化SIFT检测器
    sift = cv2.SIFT_create()

    # 对屏幕截图和模板图像使用SIFT进行关键点和描述符的检测
    keypoints_screenshot, descriptors_screenshot = sift.detectAndCompute(screenshot, None)
    keypoints_template, descriptors_template = sift.detectAndCompute(template, None)

    # 创建BFMatcher对象，使用默认参数
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors_template, descriptors_screenshot, k=2)

    # 使用比率测试筛选出好的匹配点
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # 仅当有足够的好的匹配点时，尝试找到单应性矩阵
    if len(good_matches) >= 4:
        src_pts = np.float32([keypoints_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints_screenshot[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 计算单应性矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = template.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # 找到变换后的四个角点在主图像中的位置
        rect = np.int32(dst)
        centre = rect.mean(axis=0).flatten()

        # 使用ActionChains点击找到的中心点
        ActionChains(driver).move_to_element_with_offset(screen, centre[0] - W / 2, centre[1] - H / 2).click().perform()
        print(centre[0] - W / 2, centre[1] - H / 2)
        sleep(5)


def click_random_points(driver, element, top_left, bottom_right, num_clicks=20):
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

    print("Closing FUCKING window...")
    find_and_click(driver, screen, 'templates/quxiao_button.png')

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

    print("Clicking more to access 发财树...")
    find_and_click(driver, screen, 'templates/gengduo_button.png')
    driver.save_screenshot('6.png')

    print("Clicking money tree...")
    find_and_click(driver, screen, 'templates/facaishu_button.png')
    driver.save_screenshot('7.png')

    print("Clicking 斧头...")
    find_and_click(driver, screen, 'templates/futou_button.png')
    driver.save_screenshot('8.png')

    print("Randomly clicking on 桃子区域...")
    screen_size = screen.size

    width = screen_size['width']
    height = screen_size['height']
    top_left_x = -width // 6
    top_left_y = 0
    bottom_right_x = width // 6
    bottom_right_y = height // 4
    print(f"Top-left corner: ({top_left_x}, {top_left_y})")
    print(f"Bottom-right corner: ({bottom_right_x}, {bottom_right_y})")

    click_random_points(driver, screen, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y))
    driver.save_screenshot('9.png')

    print("Closing windows...")
    for _ in range(3):
        find_and_click(driver, screen, 'templates/close_window.png')

    print("Navigating to 免费武将包...")
    find_and_click(driver, screen, 'templates/wujiang_button.png')  # Click 武将 button
    driver.save_screenshot('10.png')

    print("Clicking 招武将...")
    find_and_click(driver, screen, 'templates/zhaowujiang_button.png')
    driver.save_screenshot('11.png')

    # 获取当前日期中的日（number of the day in the month）
    current_day = datetime.now().day

    # 根据当前日期延迟相应秒数
    sleep(current_day * 60)

    print("Clicking open once...")
    find_and_click(driver, screen, 'templates/kaiqiyici_button.png')
    driver.save_screenshot('12.png')

    print("Clicking cancel to prevent purchase...")
    find_and_click(driver, screen, 'templates/quxiao_button.png')
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
        driver.quit()


if __name__ == "__main__":
    main()
