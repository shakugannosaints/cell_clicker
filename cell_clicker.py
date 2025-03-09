# cell_clicker.py
import pyautogui
import time
import random
import keyboard  # Used to interrupt the clicking process

def click_cells(cell_centers, region=None, delay=(0.1, 0.2)):
    """
    点击检测到的细胞中心。

    Args:
        cell_centers:  细胞中心坐标列表，每个坐标为 (x, y) 形式的元组。
        region:      屏幕区域的坐标，格式为 (left, top, width, height)。如果为 None，则使用整个屏幕。
        delay:       点击之间的延迟时间，可以是一个数值，也可以是一个元组 (min_delay, max_delay)。
                     如果是一个元组，则每次点击的延迟时间在 min_delay 和 max_delay 之间随机选择。

    Returns:
        int: 成功点击的细胞数量
    """
    if region:
        left, top, width, height = region
    else:
        # 如果没有指定区域，则获取屏幕的宽度和高度
        width, height = pyautogui.size()
        left, top = 0, 0

    print(f"屏幕区域：left={left}, top={top}, width={width}, height={height}")

    click_count = 0
    try:
        for center_x, center_y in cell_centers:
            # 图像坐标转换为屏幕坐标
            screen_x = left + center_x
            screen_y = top + center_y

            # 点击安全检查
            if not (0 <= screen_x <= left + width and 0 <= screen_y <= top + height):
                print(f"坐标 ({screen_x}, {screen_y}) 超出屏幕区域，跳过点击。")
                continue

            #  设置点击延迟参数
            if isinstance(delay, tuple):
                min_delay, max_delay = delay
                click_delay = random.uniform(min_delay, max_delay)
            else:
                click_delay = delay

            print(f"正在点击屏幕坐标：({screen_x}, {screen_y}), 延迟: {click_delay:.2f} 秒")

            # 使用pyautogui实现精确点击，添加可视化反馈
            pyautogui.moveTo(screen_x, screen_y, duration=0.05)  # 鼠标移动到目标位置
            pyautogui.click()  # 点击
            pyautogui.sleep(click_delay) # 等待一段时间

            click_count += 1
            print(f"已点击 {click_count} 个细胞。")

            # 检测是否按下中断键 (例如，Esc键)
            if keyboard.is_pressed('esc'):  # 使用 keyboard 库检测按键
                print("检测到 Esc 键被按下，停止点击。")
                break

    except Exception as e:
        print(f"点击过程中发生错误：{e}")

    finally:
        print("点击完成。")
        return click_count


if __name__ == '__main__':
    # 示例用法
    # 假设 cell_centers 是一个包含细胞中心坐标的列表
    # 例如：cell_centers = [(100, 150), (300, 200), (500, 400)]
    # region 是要点击的屏幕区域，例如：region = (100, 100, 800, 600)

    # 模拟细胞中心坐标
    cell_centers = [(random.randint(0, 799), random.randint(0, 599)) for _ in range(10)]
    region = (100, 100, 800, 600)  # (left, top, width, height)

    print("准备点击以下细胞中心坐标:")
    for center in cell_centers:
        print(center)

    input("请将鼠标移动到指定区域，然后按 Enter 键开始点击...") # 提示用户移动鼠标

    click_cells(cell_centers, region=region, delay=(0.2, 0.5)) # 调用点击函数，指定区域和延迟时间

    print("测试完成！")
