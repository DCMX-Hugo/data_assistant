#数据清洗模块
import pandas as pd
import numpy as np
from .utils import standardize_column_names

class DataCleaner:
    def __init__(self, df):
        self.df = df                                        #存储传入的 DataFrame，这是需要清洗的数据
        self.cleaning = {'steps': [], 'rows_removed': 0}    #一个字典，用于记录清洗过程中的信息，包括执行的步骤（steps）和移除的行数（rows_removed）
        self.issues = []                                    #一个列表，用于记录清洗过程中遇到的问题

    def clean_data(self):
        """
        这是执行数据清洗的主要方法。
        :return:
        """
        #首先检查传入的 DataFrame 是否为空或未加载，如果是，则将问题记录到 issues 列表中，并返回原始的 DataFrame，因为没有数据可以清洗
        if self.df is None or self.df.empty:
            self.issues.append("清洗失败: 数据未加载或为空")
            return self.df
        #记录原始 DataFrame 的行数，这将在后续步骤中用于计算移除的行数
        original_count = len(self.df)

        try:
            # 1. 处理列名
            self.df.columns = standardize_column_names(self.df)
            self.cleaning['steps'].append("标准化列名")#将 "标准化列名" 这一步骤记录到 cleaning 字典的 steps 列表中

            # 2. 删除完全空值的行
            self.df.dropna(how='all', inplace=True)
            '''
            使用 dropna 方法删除 DataFrame 中完全为空值的行（即所有列都是空值的行），
            how='all' 参数表示只有当一行的所有列都是空值时才删除该行，
            inplace=True 表示直接在原 DataFrame 上进行修改。
            '''
            self.cleaning['steps'].append("删除完全空值的行")
            # 3. 删除重复行
            duplicates = self.df.duplicated().sum()
            '''
            duplicated() 方法返回一个布尔 Series，表示每行是否重复，
            sum() 方法计算重复行的数量。
            '''
            if duplicates > 0:
                self.df.drop_duplicates(inplace=True)
                self.cleaning['steps'].append(f"删除 {duplicates} 个重复行")

            # 4. 处理缺失值
            missing_report = {}#初始化一个空字典 missing_report 用于记录缺失值处理信息。
            for col in self.df.columns:
                missing_count = self.df[col].isnull().sum()
                if missing_count > 0:
                    # 数值列用中位数填充
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        '''
                        如果该列是数值类型（使用 pd.api.types.is_numeric_dtype 检查），
                        则计算该列的中位数（median_val），并使用中位数填充缺失值（fillna 方法）
                        '''
                        median_val = self.df[col].median()
                        self.df[col].fillna(median_val, inplace=True)
                        missing_report[col] = f"填充中位数: {median_val:.2f} ({missing_count} 个缺失值)"
                    # 分类列用众数填充
                    else:
                        '''
                        如果该列不是数值类型（即分类列），则计算该列的众数（mode_val），并使用众数填充缺失值
                        '''
                        mode_val = self.df[col].mode()[0]
                        self.df[col].fillna(mode_val, inplace=True)
                        missing_report[col] = f"填充众数: '{mode_val}' ({missing_count} 个缺失值)"
            '''
            如果 missing_report 字典不为空（即存在缺失值并已处理），
            则将 "处理缺失值" 这一步骤记录到 steps 列表中，
            并将 missing_report 字典添加到 cleaning 字典中，以便后续查看缺失值处理的详细信息
            '''
            if missing_report:
                self.cleaning['steps'].append("处理缺失值")
                self.cleaning['missing_report'] = missing_report

            # 5. 处理异常值 (使用IQR方法)
            numeric_cols = self.df.select_dtypes(include=np.number).columns
            #获取 DataFrame 中所有数值类型的列（numeric_cols），使用 select_dtypes 方法并指定 include=np.number 参数来选择数值列
            outlier_report = {}#初始化一个空字典 outlier_report 用于记录异常值处理信息

            for col in numeric_cols:
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                '''
                根据 IQR 方法计算异常值的下界（lower_bound）和上界（upper_bound），
                公式分别为 q1 - 1.5 * iqr 和 q3 + 1.5 * iqr
                '''
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]

                if not outliers.empty:
                    # 用边界值替换异常值
                    self.df[col] = np.where(self.df[col] < lower_bound, lower_bound,
                                            np.where(self.df[col] > upper_bound, upper_bound, self.df[col]))
                    # 将该列的异常值处理信息（包括上下界和异常值数量）记录到 outlier_report 字典中
                    outlier_report[col] = {
                        'lower_bound': lower_bound,
                        'upper_bound': upper_bound,
                        'outliers_count': len(outliers)
                    }

            if outlier_report:
                self.cleaning['steps'].append("处理异常值")
                self.cleaning['outlier_report'] = outlier_report

            # 6. 数据类型转换
            for col in self.df.columns:
                # 尝试转换为日期类型
                if 'date' in col or 'time' in col:
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        self.cleaning['steps'].append(f"转换 '{col}' 列为日期类型")
                    except:
                        pass

            # 记录清洗结果
            self.cleaning['rows_removed'] = original_count - len(self.df)
            self.cleaning['final_shape'] = self.df.shape
            print(f"数据清洗完成。移除 {self.cleaning['rows_removed']} 行。当前形状: {self.df.shape}")

        except Exception as e:
            self.issues.append(f"清洗过程中出错: {str(e)}")
            print(f"清洗错误: {str(e)}")

        return self.df