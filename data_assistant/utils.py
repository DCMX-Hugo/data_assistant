#通用工具函数
import os
import re
import platform
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO
import base64


def set_chinese_font():
    """配置中文字体支持"""
    system = platform.system()
    if system == 'Windows':
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'Arial Unicode MS']
    elif system == 'Darwin':  # macOS
        plt.rcParams['font.sans-serif'] = ['Heiti SC', 'STHeiti', 'PingFang SC', 'Arial Unicode MS']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'AR PL UMing CN',
                                           'Arial Unicode MS']

    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def fig_to_base64(fig):
    """将matplotlib图表转换为base64编码图像"""
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64


def standardize_column_names(df):
    """标准化列名"""
    return [re.sub(r'[^a-zA-Z0-9_]', '_', col).strip().lower() for col in df.columns]


def ensure_dir_exists(directory):
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)
    return directory