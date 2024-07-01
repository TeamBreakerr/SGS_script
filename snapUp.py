import pyautogui
import time

# 配置按钮和对话框的坐标
button1_coords = (981, 1008)  # 第一个按钮的实际坐标
button2_coords = (1373, 1008)  # 第二个按钮的实际坐标
button3_coords = (1767, 1008)  # 第三个按钮的实际坐标
test_button_coords = (303, 708)

dialog_coords = (1192, 848)  # 弹出框确认按钮的实际坐标
test_dialog_coords = (1950, 383)

close_coords = (1726, 454)
clock_coords = (1818, 1074)
close_dialog_coords = (1950, 383)


# 选择点击哪些按钮
buttons_to_click = [button2_coords]  # 根据需要调整此列表

def click_button(coords):
    """ 点击指定坐标的按钮 """
    pyautogui.click(coords)

def handle_dialog(coords):
    """ 点击对话框确认 """
    pyautogui.click(coords)

# 主程序
def main():
    while True:  # 创建一个死循环，持续执行下面的操作
        for button_coords in buttons_to_click:
            click_button(button_coords)  # 点击按钮
            time.sleep(0.001)
            handle_dialog(dialog_coords)  # 处理弹出框
            time.sleep(0.001)

    # while True:  # 创建一个死循环，持续执行下面的操作
    #     click_button(test_button_coords)  # 点击按钮
    #     # time.sleep(0.01)  # 为了确保UI反应，这里设置了1秒等待时间
    #     handle_dialog(test_dialog_coords)  # 处理弹出框
    #     # time.sleep(0.01)  # 再次等待1秒后继续下一个按钮的点击

if __name__ == "__main__":
    main()
