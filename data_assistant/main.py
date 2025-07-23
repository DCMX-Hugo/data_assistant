import argparse
from .loader import DataLoader
from .cleaner import DataCleaner
from .analyzer import DataAnalyzer
from .visualizer import DataVisualizer
from .reporter import ReportGenerator
from .utils import set_chinese_font, ensure_dir_exists


def main():
    """
    命令行接口
    """
    parser = argparse.ArgumentParser(description='数据处理小助手 - CSV/Excel文件分析工具')
    parser.add_argument('file', type=str, help='数据文件路径 (CSV 或 Excel)')
    parser.add_argument('-o', '--output', type=str, help='输出目录', default='reports')
    args = parser.parse_args()

    # 设置中文字体
    set_chinese_font()

    # 确保输出目录存在
    output_dir = ensure_dir_exists(args.output)

    # 1. 加载数据
    loader = DataLoader(args.file)
    if not loader.load_data():
        print("数据加载失败，程序终止。")
        return

    # 2. 清洗数据
    cleaner = DataCleaner(loader.df)
    cleaned_df = cleaner.clean_data()

    # 3. 分析数据
    analyzer = DataAnalyzer(cleaned_df)
    analyzer.analyze_data()

    # 4. 创建可视化
    visualizer = DataVisualizer(cleaned_df)
    visualizer.create_visualizations()

    # 5. 生成报告
    report_data = {
        'file_info': loader.file_info,
        'cleaning': cleaner.cleaning,
        'analysis': analyzer.analysis,
        'visualizations': visualizer.visualizations,
        'issues': loader.issues + cleaner.issues + analyzer.issues + visualizer.issues
    }

    report_generator = ReportGenerator(output_dir)
    report_path = report_generator.generate_report(report_data)

    if report_path:
        print(f"\n✅ 数据处理完成！报告已保存至: {report_path}")
    else:
        print("\n❌ 数据处理失败，请检查错误信息")


if __name__ == "__main__":
    main()