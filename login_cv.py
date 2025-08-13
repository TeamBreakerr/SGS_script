import random
import sys
from datetime import datetime
from time import sleep

from playwright.sync_api import sync_playwright
import cv2
import numpy as np


def setup_driver():
    # 使用Playwright启动浏览器并确保事件循环正常
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 启动无头浏览器
        page = browser.new_page()  # 创建一个新的页面
        return page, browser


def login(page, email, password):
    print("Navigating to login page...")
    page.goto("https://web.sanguosha.com/login/index.html")  # 打开登录页面

    print("Entering email...")
    page.fill('#SGS_login-account', email)  # 填写邮箱

    print("Entering password...")
    page.fill('#SGS_login-password', password)  # 填写密码

    print("Accepting user agreement...")
    page.click('#SGS_userProto')  # 点击同意协议

    print("Performing login...")
    page.click('#SGS_login-btn')  # 点击登录按钮
    print("Login successful.")


def take_screenshot(page, filename):
    page.screenshot(path=filename)


def find_and_click(page, template_path, threshold=0.8):
    screenshot = page.screenshot()
    template = cv2.imread(template_path, 0)

    orb = cv2.ORB_create()
    keypoints_screenshot, descriptors_screenshot = orb.detectAndCompute(screenshot, None)
    keypoints_template, descriptors_template = orb.detectAndCompute(template, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors_template, descriptors_screenshot, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    if len(good_matches) >= 4:
        src_pts = np.float32([keypoints_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints_screenshot[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = template.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        rect = np.int32(dst)
        centre = rect.mean(axis=0).flatten()

        page.mouse.click(centre[0], centre[1])


def click_random_points(page, element, top_left, bottom_right, num_clicks=20):
    for _ in range(num_clicks):
        x = random.randint(top_left[0], bottom_right[0])
        y = random.randint(top_left[1], bottom_right[1])
        element.mouse.click(x, y)


def click_evenly_distributed_points(page, element, top_left, bottom_right, num_clicks=50):
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]

    points_per_row = int(num_clicks ** 0.5)
    points_per_col = points_per_row

    if points_per_row * points_per_col < num_clicks:
        points_per_col += 1

    x_spacing = width // (points_per_row - 1)
    y_spacing = height // (points_per_col - 1)

    click_points = []
    for i in range(points_per_row):
        for j in range(points_per_col):
            if len(click_points) < num_clicks:
                x = top_left[0] + i * x_spacing
                y = top_left[1] + j * y_spacing
                click_points.append((x, y))

    for point in click_points:
        element.mouse.click(point[0], point[1])


def perform_game_actions(page):
    print("Waiting for game screen to load...")
    page.wait_for_selector('#layaCanvas')  # 等待游戏画面加载

    print("Closing FUCKING window...")
    find_and_click(page, 'templates/quxiao_button.png')

    take_screenshot(page, '0.png')

    print("Closing windows...")
    for _ in range(3):
        find_and_click(page, 'templates/close_window.png')
    take_screenshot(page, '1.png')

    print("Clicking sign-in button...")
    find_and_click(page, 'templates/fuli_button.png')
    take_screenshot(page, '2.png')

    find_and_click(page, 'templates/meiriqiandao_button.png')
    take_screenshot(page, '3.png')

    find_and_click(page, 'templates/qiandao_button.png')
    take_screenshot(page, '4.png')

    find_and_click(page, 'templates/close_window.png')
    take_screenshot(page, '5.png')

    print("Clicking more to access 发财树...")
    find_and_click(page, 'templates/gengduo_button.png')
    take_screenshot(page, '6.png')

    print("Clicking money tree...")
    find_and_click(page, 'templates/facaishu_button.png')
    take_screenshot(page, '7.png')

    print("Clicking 斧头...")
    find_and_click(page, 'templates/futou_button.png')
    take_screenshot(page, '8.png')

    print("Randomly clicking on 桃子区域...")
    screen_size = page.size

    width = screen_size['width']
    height = screen_size['height']
    top_left_x = -width // 6
    top_left_y = 0
    bottom_right_x = width // 6
    bottom_right_y = height // 4
    print(f"Top-left corner: ({top_left_x}, {top_left_y})")
    print(f"Bottom-right corner: ({bottom_right_x}, {bottom_right_y})")

    click_evenly_distributed_points(page, page, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y))

    take_screenshot(page, '9.png')

    print("Closing windows...")
    for _ in range(3):
        find_and_click(page, 'templates/close_window.png')

    print("Navigating to 免费武将包...")
    find_and_click(page, 'templates/wujiang_button.png')  # Click 武将 button
    take_screenshot(page, '10.png')

    print("Clicking 招武将...")
    find_and_click(page, 'templates/zhaowujiang_button.png')
    take_screenshot(page, '11.png')

    current_day = datetime.now().day
    sleep(current_day * 60)

    print("Clicking open once...")
    find_and_click(page, 'templates/kaiqiyici_button.png')
    take_screenshot(page, '12.png')

    print("Clicking cancel to prevent purchase...")
    find_and_click(page, 'templates/quxiao_button.png')
    take_screenshot(page, '13.png')

    print("Completed game actions.")


def main():
    acccounts = int(len(sys.argv[1:]) / 2)
    print(f'Config {acccounts} accounts')
    for i in range(acccounts):
        email = sys.argv[1 + i]
        passwd = sys.argv[1 + i + acccounts]
        print('----------------------------')

        page, browser = setup_driver()  # 获取页面和浏览器对象

        print("Starting login process...")
        login(page, email, passwd)  # 执行登录

        print("Entering game...")
        page.click('#gameItemOl')
        page.click('#goInGameBtn')
        sleep(60)

        print("Performing game actions...")
        perform_game_actions(page)  # 执行游戏操作

        print("Waiting for two hours...")
        print("Script finished.")
        browser.close()  # 关闭浏览器


if __name__ == "__main__":
    main()
