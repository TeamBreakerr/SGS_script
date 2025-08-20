import random
import sys
from datetime import datetime
from time import sleep
import os # 导入 os 模块

from playwright.sync_api import sync_playwright, Error
import cv2
import numpy as np

# 为调试截图创建一个目录
if not os.path.exists('debug_screenshots'):
    os.makedirs('debug_screenshots')

def login(page, email, password):
    print("Navigating to login page...")
    page.goto("https://web.sanguosha.com/login/index.html")

    print("Entering email...")
    page.fill('#SGS_login-account', email)

    print("Entering password...")
    page.fill('#SGS_login-password', password)

    print("Accepting user agreement...")
    page.click('#SGS_userProto')

    print("Performing login...")
    page.click('#SGS_login-btn')
    print("Login successful.")


# take_screenshot 函数现在可以被 find_and_click 的功能替代，但我们暂时保留它以备不时之需
def take_screenshot(page, filename):
    page.screenshot(path=filename)

def find_and_click(page, template_path, threshold=0.8):
    """
    在屏幕截图中查找并点击目标，并在点击前保存一张带有红色标记框的截图用于调试。
    """
    try:
        # 1. 获取屏幕截图和模板图片
        screenshot_bytes = page.screenshot()
        screenshot = cv2.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv2.IMREAD_COLOR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        if template is None:
            print(f"错误: 无法读取模板图片 {template_path}")
            return False
        
        # 2. 进行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"正在匹配模板: '{template_path}', 最高相似度: {max_val:.2f}")
        
        # 获取模板的宽度和高度
        h, w, _ = template.shape

        # 3. 检查相似度是否达到阈值
        if max_val >= threshold:
            # 计算匹配区域的左上角和右下角坐标
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # (新增) 在截图上用红色框标出匹配区域
            # cv2.rectangle(image, start_point, end_point, color, thickness)
            cv2.rectangle(screenshot, top_left, bottom_right, (0, 0, 255), 2) # (0,0,255) 是红色的 BGR 值, 2 是线条粗细

            # (新增) 保存带有红框的截图
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 从 template_path 中提取基础名字，例如 'templates/fuli_button.png' -> 'fuli_button'
            template_name = os.path.splitext(os.path.basename(template_path))[0]
            screenshot_filename = f"debug_screenshots/{timestamp}_{template_name}_matched.png"
            cv2.imwrite(screenshot_filename, screenshot)
            print(f"已保存带标记的截图到: {screenshot_filename}")

            # 计算中心点并点击
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            print(f"找到目标 '{template_path}' 在坐标 ({center_x}, {center_y}), 相似度: {max_val:.2f}。正在点击...")
            page.mouse.click(center_x, center_y)
            sleep(1)
            return True
        else:
            print(f"未能找到足够匹配的目标 '{template_path}' (最高相似度: {max_val:.2f} < 阈值: {threshold})")
            return False

    except Exception as e:
        print(f"在 find_and_click 函数中发生错误 ({template_path}): {e}")
        return False

def click_evenly_distributed_points(page, top_left, bottom_right, num_clicks=50):
    # (此函数保持不变)
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]

    if num_clicks <= 1:
        if num_clicks == 1:
            x = top_left[0] + width // 2
            y = top_left[1] + height // 2
            page.mouse.click(x, y)
        return

    points_per_side = int(num_clicks**0.5)
    num_rows = points_per_side
    num_cols = points_per_side
    
    while num_rows * num_cols < num_clicks:
        num_cols += 1
    
    x_spacing = width / (num_cols - 1) if num_cols > 1 else 0
    y_spacing = height / (num_rows - 1) if num_rows > 1 else 0

    click_count = 0
    for j in range(num_rows):
        for i in range(num_cols):
            if click_count >= num_clicks:
                break
            x = top_left[0] + i * x_spacing
            y = top_left[1] + j * y_spacing
            page.mouse.click(x, y)
            sleep(0.05)
            click_count += 1
        if click_count >= num_clicks:
            break


def perform_game_actions(page):
    print("Waiting for game screen to load...")
    page.wait_for_selector('#layaCanvas', timeout=60000)
    sleep(5) # 等待Canvas内动画加载

    print("Closing initial pop-up windows...")
    find_and_click(page, 'templates/quxiao_button.png')

    find_and_click(page, 'templates/qiandao_button.png')
    sleep(2)

    for _ in range(3):
        find_and_click(page, 'templates/close_window.png')
        sleep(0.5)

        find_and_click(page, 'templates/qiandao_button.png')
    sleep(2)

    #print("Performing daily sign-in...")
    #find_and_click(page, 'templates/fuli_button.png')
    #sleep(2)
    #find_and_click(page, 'templates/meiriqiandao_button.png')
    #sleep(2)
    #find_and_click(page, 'templates/qiandao_button.png')
    #sleep(2)
    #find_and_click(page, 'templates/close_window.png')
    #sleep(2)

    print("Accessing and using money tree...")
    find_and_click(page, 'templates/gengduo_button.png')
    sleep(2)
    
    take_screenshot(page, 'test.png')
 
    find_and_click(page, 'templates/facaishu_button.png')
    sleep(2)
    find_and_click(page, 'templates/futou_button.png')
    sleep(2)

    print("Clicking on peach area...")
    canvas_box = page.locator('#layaCanvas').bounding_box()
    
    if canvas_box:
        # 新的坐标计算逻辑
        # 画布的中心点坐标
        center_x = canvas_box['x'] + canvas_box['width'] / 2
        center_y = canvas_box['y'] + canvas_box['height'] / 2

        # 1. 计算宽度区域
        # 区域总宽度为画布的 2/3
        click_area_width = canvas_box['width'] * (2 / 3)
        # 区域的左侧X坐标 = 中心点X - 区域宽度的一半
        top_left_x = center_x - (click_area_width / 2)
        # 区域的右侧X坐标 = 中心点X + 区域宽度的一半
        bottom_right_x = center_x + (click_area_width / 2)

        # 2. 计算高度区域
        # 区域的顶部Y坐标从画布的垂直中心线开始
        top_left_y = center_y
        # 区域的高度为画布总高度的 1/4
        click_area_height = canvas_box['height'] / 4
        # 区域的底部Y坐标 = 顶部Y坐标 + 区域高度
        bottom_right_y = top_left_y + click_area_height
        
        print(f"Calculated click area Top-Left: ({top_left_x:.0f}, {top_left_y:.0f}), Bottom-Right: ({bottom_right_x:.0f}, {bottom_right_y:.0f})")
        click_evenly_distributed_points(page, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y))
    else:
        print("Error: Could not find game canvas to calculate the click area.")
 
    sleep(2)
    print("Closing windows after money tree...")
    for _ in range(3):
        find_and_click(page, 'templates/close_window.png')
        sleep(0.5)

    print("Navigating to free hero pack...")
    find_and_click(page, 'templates/wujiang_button.png')
    sleep(2)
    find_and_click(page, 'templates/zhaowujiang_button.png')
    sleep(2)

    # 获取当前日期并进行长时间等待
    current_day = datetime.now().day
    wait_minutes = current_day
    print(f"Today is the {current_day}th. Waiting for {wait_minutes} minutes as requested...")
    # sleep(wait_minutes * 60) # 注意：这里是分钟级的长时间等待，如果您只是测试，可以注释掉
    print(f"Finished waiting for {wait_minutes} minutes.")

    print("Clicking open once...")
    find_and_click(page, 'templates/kaiqiyici_button.png')
    sleep(2)
    print("Clicking cancel to prevent purchase...")
    find_and_click(page, 'templates/quxiao_button.png')
    sleep(2)

    print("Completed all game actions.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 'login_cv.py' <email1> <email2> ... <pass1> <pass2> ...")
        sys.exit(1)

    accounts_count = int((len(sys.argv) - 1) / 2)
    print(f'Configured for {accounts_count} accounts')

    emails = sys.argv[1:accounts_count + 1]
    passwords = sys.argv[accounts_count + 1:]

    for i in range(accounts_count):
        email = emails[i]
        passwd = passwords[i]
        print(f'----------------------------')
        print(f'Processing account: {email}')

        with sync_playwright() as p:
            browser = None # 初始化 browser 变量
            try:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                print("Starting login process...")
                login(page, email, passwd)

                print("Entering game...")
                page.wait_for_selector('#gameItemOl', timeout=30000).click()
                page.wait_for_selector('#goInGameBtn', timeout=30000).click()

                # 等待游戏环境加载，这个时间可能需要根据网络情况调整
                sleep(60) 

                print("Performing game actions...")
                perform_game_actions(page)

                print(f"Account {email} finished.")

            except Error as e:
                print(f"A Playwright error occurred for account {email}: {e}")
            except Exception as e:
                print(f"A general error occurred for account {email}: {e}")
            finally:
                if browser and browser.is_connected():
                    browser.close() # 确保浏览器被关闭

    print("All accounts processed.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 'login cv.py' <email1> <email2> ... <pass1> <pass2> ...")
        sys.exit(1)

    accounts_count = int((len(sys.argv) - 1) / 2)
    print(f'Configured for {accounts_count} accounts')

    emails = sys.argv[1:accounts_count + 1]
    passwords = sys.argv[accounts_count + 1:]

    for i in range(accounts_count):
        email = emails[i]
        passwd = passwords[i]
        print(f'----------------------------')
        print(f'Processing account: {email}')

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                print("Starting login process...")
                login(page, email, passwd)

                print("Entering game...")
                page.wait_for_selector('#gameItemOl', timeout=30000).click()
                page.wait_for_selector('#goInGameBtn', timeout=30000).click()
                sleep(60)

                print("Performing game actions...")
                perform_game_actions(page)

                print(f"Account {email} finished.")

            except Error as e:
                print(f"A Playwright error occurred for account {email}: {e}")
            except Exception as e:
                print(f"A general error occurred for account {email}: {e}")
            finally:
                if 'browser' in locals() and browser.is_connected():
                    browser.close()

    print("All accounts processed.")


if __name__ == "__main__":
    main()

