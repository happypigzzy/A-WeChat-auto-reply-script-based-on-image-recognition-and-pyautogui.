import cv2
import numpy as np
import pyautogui as pa
import time
import pyperclip
from PIL import ImageGrab

# 设置检测区域 (x, y, width, height) - 覆盖395*1193的大区域
detection_area = (2159, 886, 395, 1193)

# 定义红色范围 (HSV颜色空间)
red_lower1 = np.array([0, 120, 120])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([160, 120, 120])
red_upper2 = np.array([180, 255, 255])

def detect_red_circles():
    """检测指定区域内所有红色圆圈的位置"""
    # 截取指定区域
    screenshot = ImageGrab.grab(bbox=(
        detection_area[0],
        detection_area[1],
        detection_area[0] + detection_area[2],
        detection_area[1] + detection_area[3]
    ))

    # 转换为OpenCV格式
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screenshot_hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)

    # 创建红色掩码
    mask1 = cv2.inRange(screenshot_hsv, red_lower1, red_upper1)
    mask2 = cv2.inRange(screenshot_hsv, red_lower2, red_upper2)
    red_mask = mask1 + mask2

    # 形态学操作，增强红色区域检测
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

    # 寻找轮廓
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    red_circles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 8:  # 面积阈值，可根据需要调整
            # 计算轮廓的圆形度
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
                
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # 如果圆形度接近1，说明是圆形
            if circularity > 0.7:
                # 计算轮廓的中心点
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    # 转换为屏幕绝对坐标
                    screen_x = detection_area[0] + cx
                    screen_y = detection_area[1] + cy
                    red_circles.append((screen_x, screen_y, area, circularity))
    
    # 按Y坐标排序（从上到下）
    red_circles.sort(key=lambda circle: circle[1])
    
    return red_circles

def process_unread_message(red_circle_position=None):
    """处理未读消息"""
    print("检测到未读消息，正在处理...")
    
    # 如果有指定红圈位置，先点击红圈
    if red_circle_position:
        print(f"点击红圈位置: {red_circle_position}")
        pa.moveTo(red_circle_position[0], red_circle_position[1])
        pa.click()
        time.sleep(1.5)  # 等待聊天窗口打开
    
    # 移动到指定位置并点击
    pa.moveTo(2583, 1780)
    pa.click()
    time.sleep(0.5)
    pa.click()

    # 复制并发送文本
    text = "☺Working!I may be slow to respond!"
    pyperclip.copy(text)
    time.sleep(0.5)
    pa.hotkey('ctrl', 'v')
    pa.press('enter')  # 发送消息

    print("消息已发送")
    
    # 发送完成后点击指定位置
    pa.moveTo(2583, 1780)
    pa.click()
    time.sleep(0.5)

def main():
    print("开始监控微信未读消息...")
    print(f"监控区域: {detection_area}")
    print("按 Ctrl+C 停止监控")

    # 存储检测到的红圈坐标
    red_circles_positions = []
    
    try:
        while True:
            current_red_circles = detect_red_circles()
            
            if current_red_circles:
                print(f"检测到 {len(current_red_circles)} 个红色圆圈未读消息")
                
                # 更新红圈位置列表
                red_circles_positions = [(x, y) for x, y, area, circularity in current_red_circles]
                
                # 处理所有红圈
                for i, (x, y) in enumerate(red_circles_positions):
                    print(f"处理第 {i+1} 个未读消息 (位置: {x}, {y})")
                    process_unread_message((x, y))
                    
                    # 处理完一个后检查是否还有红圈
                    time.sleep(2)
                    remaining_circles = detect_red_circles()
                    if not remaining_circles:
                        print("所有未读消息已处理完毕")
                        red_circles_positions = []  # 清空红圈列表
                        break
                
                # 所有红圈处理完后等待一段时间
                print("等待新消息...")
                time.sleep(5)
            else:
                # 没有检测到未读消息，清空红圈列表
                if red_circles_positions:
                    print("未读消息已全部处理")
                    red_circles_positions = []
                
                # 等待一段时间再检查
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n监控已停止")

# 调试函数：可视化检测区域和红圈
def debug_red_detection():
    """调试函数：显示检测区域和红圈位置"""
    screenshot = ImageGrab.grab(bbox=(
        detection_area[0],
        detection_area[1],
        detection_area[0] + detection_area[2],
        detection_area[1] + detection_area[3]
    ))
    
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screenshot_hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
    
    # 创建红色掩码
    mask1 = cv2.inRange(screenshot_hsv, red_lower1, red_upper1)
    mask2 = cv2.inRange(screenshot_hsv, red_lower2, red_upper2)
    red_mask = mask1 + mask2
    
    # 形态学操作
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    
    # 寻找轮廓并绘制
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 8:
            # 计算圆形度
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # 如果是圆形，绘制轮廓和中心点
                if circularity > 0.7:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.circle(screenshot_cv, (cx, cy), 5, (0, 255, 0), -1)
                        cv2.drawContours(screenshot_cv, [contour], -1, (0, 255, 0), 2)
    
    # 显示结果
    cv2.imshow('Red Circle Detection Debug', screenshot_cv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 安装所需库:
    # pip install opencv-python pyautogui pyperclip pillow numpy
    
    # 使用前请调整以下参数:
    # 1. detection_area: 微信未读消息红色圆点的屏幕区域坐标
    # 2. 点击坐标 (2583, 1780): 微信聊天窗口的输入框位置
    
    # 调试模式（可选）
    # debug_red_detection()
    
    main()