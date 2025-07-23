#数据加载模块
import pandas as pd
import os
from datetime import datetime

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.file_info = {}
        self.issues = []

    def load_data(self):
        try:
            file_ext = os.path.splitext(self.file_path)[1].lower()

            if file_ext == '.csv':
                self.df = pd.read_csv(self.file_path, encoding='utf-8', engine='python')
            elif file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path, engine='openpyxl')
            else:
                raise ValueError("不支持的文件格式。请提供CSV或Excel文件。")

            # 记录文件信息
            self.file_info = {
                'filename': os.path.basename(self.file_path),
                'file_type': "CSV" if file_ext == '.csv' else "Excel",
                'load_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'original_shape': self.df.shape,
                'columns': list(self.df.columns),
                'data_types': self.df.dtypes.astype(str).to_dict()
            }

            print(f"成功加载数据: {self.df.shape[0]} 行, {self.df.shape[1]} 列")
            return True

        except Exception as e:
            self.issues.append(f"数据加载失败: {str(e)}")
            print(f"错误: {str(e)}")
            return False