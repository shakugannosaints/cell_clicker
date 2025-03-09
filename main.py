# main.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from cell_detector import CellDetector
from cell_clicker import click_cells

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 默认配置
DEFAULT_CONFIG = {
    "cell_color": "green",
    "hsv_range": {"hueMin": 40, "hueMax": 80, "satMin": 50, "satMax": 255, "valMin": 50, "valMax": 255},
    "size_filter": {"minSize": 100, "maxSize": 2000},
    "circularity": 0.7,
    "overlap_sensitivity": 0.5,
    "morph_operations": {"erosion": 1, "dilation": 1},
    "region": {"x": 0, "y": 0, "width": 800, "height": 600}
}

# 配置文件路径
CONFIG_FILE = "config.json"

# 加载配置
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("配置文件未找到，使用默认配置")
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        print("配置文件格式错误，使用默认配置")
        return DEFAULT_CONFIG

# 保存配置
def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("配置已保存到 config.json")
    except Exception as e:
        print(f"保存配置时出错：{e}")

# 程序状态
config = load_config()
detector = CellDetector(
    hsv_range=config["hsv_range"],
    size_filter=config["size_filter"],
    circularity=config["circularity"],
    overlap_sensitivity=config["overlap_sensitivity"],
    morph_operations=config["morph_operations"]
)

# API 路由
@app.route('/api/preview-detection', methods=['POST'])
def preview_detection():
    global config, detector
    try:
        params = request.get_json()
        print(f"接收到的参数：{params}")

        # 更新配置
        config["cell_color"] = params["cellColor"]
        config["hsv_range"] = params["hsvRange"]
        config["size_filter"] = params["sizeFilter"]
        config["circularity"] = params["circularity"]
        config["overlap_sensitivity"] = params["overlapSensitivity"]
        config["morph_operations"] = params["morphOperations"]
        config["region"] = params["region"]
        save_config(config)

        # 更新detector
        detector = CellDetector(
            hsv_range=config["hsv_range"],
            size_filter=config["size_filter"],
            circularity=config["circularity"],
            overlap_sensitivity=config["overlap_sensitivity"],
            morph_operations=config["morph_operations"]
        )

        # 获取屏幕区域
        region = (config["region"]["x"], config["region"]["y"],
                  config["region"]["width"], config["region"]["height"])

        # 检测细胞
        cell_count, _ = detector.process_and_click(region, config["cell_color"])

        return jsonify({"success": True, "cell_count": cell_count})
    except Exception as e:
        print(f"预览检测时出错：{e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start-clicking', methods=['POST'])
def start_clicking():
    global config, detector
    try:
        params = request.get_json()
        print(f"接收到的参数：{params}")

        # 更新配置
        config["cell_color"] = params["cellColor"]
        config["hsv_range"] = params["hsvRange"]
        config["size_filter"] = params["sizeFilter"]
        config["circularity"] = params["circularity"]
        config["overlap_sensitivity"] = params["overlapSensitivity"]
        config["morph_operations"] = params["morphOperations"]
        config["region"] = params["region"]
        save_config(config)

        # 更新detector
        detector = CellDetector(
            hsv_range=config["hsv_range"],
            size_filter=config["size_filter"],
            circularity=config["circularity"],
            overlap_sensitivity=config["overlap_sensitivity"],
            morph_operations=config["morph_operations"]
        )

        # 获取屏幕区域
        region = (config["region"]["x"], config["region"]["y"],
                  config["region"]["width"], config["region"]["height"])

        # 点击细胞
        cell_count, click_count = detector.process_and_click(region, config["cell_color"])

        return jsonify({"success": True, "cell_count": cell_count, "click_count": click_count})
    except Exception as e:
        print(f"开始点击时出错：{e}")
        return jsonify({"success": False, "error": str(e)})

# 静态文件服务
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
