# cell_detector.py
import cv2
import numpy as np
import pyautogui
import time
import argparse
from cell_clicker import click_cells

class CellDetector:
    def __init__(self, hsv_range=None, size_filter=None, circularity=0.7,
                 overlap_sensitivity=0.5, morph_operations=None):
        """
        初始化CellDetector，配置参数。

        Args:
            hsv_range: 包含hueMin, hueMax, satMin, satMax, valMin, valMax值的字典
            size_filter: 包含minSize和maxSize值的字典
            circularity: 作为细胞的最小圆度值 (0-1)
            overlap_sensitivity: 检测重叠细胞的灵敏度 (0-1)
            morph_operations: 包含erosion和dilation迭代值的字典
        """
        # 如果未提供，则设置默认的HSV范围
        if hsv_range is None:
            self.hsv_range = {
                'hueMin': 40, 'hueMax': 80,
                'satMin': 50, 'satMax': 255,
                'valMin': 50, 'valMax': 255
            }
        else:
            self.hsv_range = hsv_range

        # 如果未提供，则设置默认的大小过滤器
        if size_filter is None:
            self.size_filter = {'minSize': 100, 'maxSize': 2000}
        else:
            self.size_filter = size_filter

        self.circularity = circularity
        self.overlap_sensitivity = overlap_sensitivity

        # 如果未提供，则设置默认的形态学操作
        if morph_operations is None:
            self.morph_operations = {'erosion': 1, 'dilation': 1}
        else:
            self.morph_operations = morph_operations

    def capture_screen(self, region=None):
        """
        捕获屏幕或屏幕的特定区域。

        Args:
            region: 定义要捕获区域的元组 (left, top, width, height)。

        Returns:
            包含捕获图像的NumPy数组。
        """
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()

        # 将截图转换为NumPy数组（OpenCV的BGR格式）
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def detect_cells(self, image, is_red=False):
        """
        根据配置的参数检测给定图像中的细胞。

        Args:
            image: 要处理的图像（BGR格式的NumPy数组）
            is_red: 指示是否检测红色细胞的标志（需要特殊的HSV处理）

        Returns:
            cell_centers: 包含检测到的细胞中心的(x, y)元组列表
            processed_image: 突出显示细胞的处理后图像
        """
        # 转换为HSV以获得更好的颜色分割
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 根据HSV范围创建蒙版
        if is_red:
            # 红色在HSV空间中回绕（0-10和160-179都是红色）
            lower_red1 = np.array([0, self.hsv_range['satMin'], self.hsv_range['valMin']])
            upper_red1 = np.array([10, self.hsv_range['satMax'], self.hsv_range['valMax']])
            lower_red2 = np.array([160, self.hsv_range['satMin'], self.hsv_range['valMin']])
            upper_red2 = np.array([179, self.hsv_range['satMax'], self.hsv_range['valMax']])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            # 对于其他颜色（绿色等）
            lower = np.array([self.hsv_range['hueMin'], self.hsv_range['satMin'], self.hsv_range['valMin']])
            upper = np.array([self.hsv_range['hueMax'], self.hsv_range['satMax'], self.hsv_range['valMax']])
            mask = cv2.inRange(hsv, lower, upper)

        # 应用形态学操作
        kernel = np.ones((5, 5), np.uint8)

        # 腐蚀去除小噪声
        if self.morph_operations['erosion'] > 0:
            mask = cv2.erode(mask, kernel, iterations=self.morph_operations['erosion'])

        # 膨胀增强细胞结构
        if self.morph_operations['dilation'] > 0:
            mask = cv2.dilate(mask, kernel, iterations=self.morph_operations['dilation'])

        # 在蒙版中查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 处理每个轮廓以检测细胞
        cell_centers = []
        processed_image = image.copy()

        for contour in contours:
            # 计算面积和周长
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # 按大小过滤
            if self.size_filter['minSize'] <= area <= self.size_filter['maxSize']:
                # 计算圆度
                circularity = 0
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)

                # 按圆度过滤
                if circularity >= self.circularity:
                    # 计算矩以找到中心
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])

                        # 将细胞中心添加到列表
                        cell_centers.append((cX, cY))

                        # 绘制细胞轮廓
                        cv2.drawContours(processed_image, [contour], -1, (0, 255, 0), 2)

                        # 绘制中心点
                        cv2.circle(processed_image, (cX, cY), 5, (255, 0, 0), -1)

                        # 添加带有细胞信息的文本
                        info_text = f"A:{int(area)}, C:{circularity:.2f}"
                        cv2.putText(processed_image, info_text, (cX - 40, cY - 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 如果灵敏度足够高，则使用分水岭算法分离重叠细胞
        if self.overlap_sensitivity > 0.3 and len(cell_centers) > 0:
            cell_centers = self._separate_overlapping_cells(mask, processed_image, cell_centers)

        return cell_centers, processed_image

    def _separate_overlapping_cells(self, mask, image, initial_centers):
        """
        使用距离变换和分水岭算法分离重叠细胞。

        Args:
            mask: 来自HSV阈值处理的二进制蒙版
            image: 要绘制的原始图像
            initial_centers: 检测到的初始细胞中心

        Returns:
            cell_centers: 更新的细胞中心列表
        """
        # 应用距离变换
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = sure_fg.astype(np.uint8)

        # 查找未知区域
        sure_bg = cv2.dilate(mask, None, iterations=3)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # 标记标签
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0

        # 应用分水岭
        watershed_image = image.copy()
        markers = cv2.watershed(watershed_image, markers)

        # 查找分割区域的中心
        cell_centers = []
        for label in range(2, np.max(markers) + 1):
            # 为此细胞创建蒙版
            cell_mask = np.zeros_like(markers, dtype=np.uint8)
            cell_mask[markers == label] = 255

            # 计算矩以找到中心
            M = cv2.moments(cell_mask)
            if M["m00"] > 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # 计算面积
                area = cv2.countNonZero(cell_mask)

                # 仅在满足大小标准时才包括
                if self.size_filter['minSize'] <= area <= self.size_filter['maxSize']:
                    cell_centers.append((cX, cY))

                    # 在分水岭图像中绘制边界（用于可视化）
                    watershed_image[markers == label] = [0, 255, 0]

        # 仅当分水岭找到比初始检测更多的细胞时才使用分水岭结果
        if len(cell_centers) > len(initial_centers):
            # 使用分水岭可视化更新处理后的图像
            alpha = 0.7  # 透明度因子
            cv2.addWeighted(watershed_image, alpha, image, 1 - alpha, 0, image)
            return cell_centers
        else:
            return initial_centers

    def save_processed_image(self, image, filename="processed_image.png"):
        """
        将处理后的图像保存到磁盘。

        Args:
            image: 要保存的图像
            filename: 要保存到的文件名
        """
        cv2.imwrite(filename, image)
        print(f"已将处理后的图像保存到 {filename}")

    def process_and_click(self, region=None, cell_color="green"):
        """
        捕获屏幕，检测细胞并执行点击。

        Args:
            region: 定义要捕获区域的元组 (left, top, width, height)
            cell_color: 要检测的细胞颜色（“green”或“red”）

        Returns:
            cell_count: 检测到的细胞数量
            click_count: 点击的细胞数量
        """
        # 解析区域（如果作为字符串提供）
        if isinstance(region, str):
            region = tuple(map(int, region.split(',')))

        # 捕获屏幕
        print(f"正在捕获屏幕区域：{region}")
        image = self.capture_screen(region)

        # 检测细胞
        is_red = (cell_color.lower() == "red")
        cell_centers, processed_image = self.detect_cells(image, is_red)

        # 保存处理后的图像以进行调试
        self.save_processed_image(processed_image)

        # 报告检测到的细胞数量
        cell_count = len(cell_centers)
        print(f"检测到 {cell_count} 个细胞")

        # 如果有细胞，则点击细胞
        click_count = 0
        if cell_count > 0:
            print("开始点击细胞...")

            # 点击细胞并获取点击计数
            # 注意：cell_clicker模块应返回成功的点击次数
            click_count = click_cells(cell_centers, region)

            print(f"点击了 {click_count} 个细胞")

        return cell_count, click_count


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='检测和点击染色的细胞。')
    parser.add_argument('--region', type=str, default=None,
                        help='要捕获的屏幕区域 (left,top,width,height)')
    parser.add_argument('--color', type=str, default='green',
                        choices=['green', 'red'], help='要检测的细胞颜色')
    parser.add_argument('--hue-min', type=int, default=40,
                        help='最小色调值 (0-179)')
    parser.add_argument('--hue-max', type=int, default=80,
                        help='最大色调值 (0-179)')
    parser.add_argument('--sat-min', type=int, default=50,
                        help='最小饱和度值 (0-255)')
    parser.add_argument('--sat-max', type=int, default=255,
                        help='最大饱和度值 (0-255)')
    parser.add_argument('--val-min', type=int, default=50,
                        help='最小亮度值 (0-255)')
    parser.add_argument('--val-max', type=int, default=255,
                        help='最大亮度值 (0-255)')
    parser.add_argument('--min-size', type=int, default=100,
                        help='最小细胞大小（像素）')
    parser.add_argument('--max-size', type=int, default=2000,
                        help='最大细胞大小（像素）')
    parser.add_argument('--circularity', type=float, default=0.7,
                        help='最小圆度 (0-1)')
    parser.add_argument('--overlap', type=float, default=0.5,
                        help='重叠检测灵敏度 (0-1)')
    parser.add_argument('--erosion', type=int, default=1,
                        help='腐蚀迭代')
    parser.add_argument('--dilation', type=int, default=1,
                        help='膨胀迭代')
    parser.add_argument('--preview-only', action='store_true',
                        help='仅预览检测而不点击')

    args = parser.parse_args()

    # 解析区域（如果提供）
    region = None
    if args.region:
        try:
            region = tuple(map(int, args.region.split(',')))
        except:
            print("解析区域时出错。格式应为：left,top,width,height")
            exit(1)

    # 创建HSV范围字典
    hsv_range = {
        'hueMin': args.hue_min,
        'hueMax': args.hue_max,
        'satMin': args.sat_min,
        'satMax': args.sat_max,
        'valMin': args.val_min,
        'valMax': args.val_max
    }

    # 创建大小过滤器字典
    size_filter = {
        'minSize': args.min_size,
        'maxSize': args.max_size
    }

    # 创建形态学操作字典
    morph_operations = {
        'erosion': args.erosion,
        'dilation': args.dilation
    }

    # 使用指定的参数创建检测器
    detector = CellDetector(
        hsv_range=hsv_range,
        size_filter=size_filter,
        circularity=args.circularity,
        overlap_sensitivity=args.overlap,
        morph_operations=morph_operations
    )

    # 如果仅预览，则仅检测并显示细胞
    if args.preview_only:
        image = detector.capture_screen(region)
        is_red = (args.color.lower() == "red")
        cell_centers, processed_image = detector.detect_cells(image, is_red)

        # 显示处理后的图像
        print(f"检测到 {len(cell_centers)} 个细胞")
        detector.save_processed_image(processed_image)

        # 显示处理后的图像
        cv2.imshow("Processed Image", processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        # 处理和点击细胞
        cell_count, click_count = detector.process_and_click(region, args.color)
        print(f"摘要：检测到 {cell_count} 个细胞，点击了 {click_count} 个细胞")
