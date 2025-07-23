#报告生成模块
import os
import jinja2
from datetime import datetime
from .utils import ensure_dir_exists

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = ensure_dir_exists(output_dir)

    def generate_report(self, report_data, report_name=None):
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"data_report_{timestamp}.html"

        report_path = os.path.join(self.output_dir, report_name)

        # 设置Jinja2环境
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(''))
        template = env.get_template('report_template.html') if os.path.exists('report_template.html') else None

        # 如果模板不存在，使用内置模板
        if not template:
            template = env.from_string("""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>数据分析报告 - {{ report_data.file_info.filename }}</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
                    h1, h2, h3 { color: #2c3e50; }
                    h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                    h2 { border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }
                    .section { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin-bottom: 30px; }
                    .info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
                    .info-card { background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; border-radius: 4px; }
                    .visualization { margin: 20px 0; text-align: center; }
                    .visualization img { max-width: 100%; border: 1px solid #eee; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f8f9fa; font-weight: 600; }
                    tr:hover { background-color: #f1f7fd; }
                    .issue { background: #fff3cd; padding: 15px; border-radius: 4px; border-left: 4px solid #ffc107; margin: 10px 0; }
                    .success { color: #28a745; }
                    .warning { color: #ffc107; }
                    .danger { color: #dc3545; }
                </style>
            </head>
            <body>
                <h1>数据分析报告</h1>
                <p>生成时间: {{ report_data.file_info.load_time }}</p>

                <div class="section">
                    <h2>文件信息</h2>
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>文件详情</h3>
                            <p><strong>文件名:</strong> {{ report_data.file_info.filename }}</p>
                            <p><strong>文件类型:</strong> {{ report_data.file_info.file_type }}</p>
                            <p><strong>原始大小:</strong> {{ report_data.file_info.original_shape[0] }} 行 × {{ report_data.file_info.original_shape[1] }} 列</p>
                        </div>

                        <div class="info-card">
                            <h3>清洗结果</h3>
                            <p><strong>移除行数:</strong> {{ report_data.cleaning.rows_removed }}</p>
                            <p><strong>最终大小:</strong> {{ report_data.cleaning.final_shape[0] }} 行 × {{ report_data.cleaning.final_shape[1] }} 列</p>
                        </div>
                    </div>
                </div>

                {% if report_data.issues %}
                <div class="section">
                    <h2>问题与警告</h2>
                    {% for issue in report_data.issues %}
                    <div class="issue">{{ issue }}</div>
                    {% endfor %}
                </div>
                {% endif %}

                <div class="section">
                    <h2>数据清洗步骤</h2>
                    <ul>
                        {% for step in report_data.cleaning.steps %}
                        <li>{{ step }}</li>
                        {% endfor %}
                    </ul>

                    {% if 'missing_report' in report_data.cleaning %}
                    <h3>缺失值处理</h3>
                    <table>
                        <tr>
                            <th>列名</th>
                            <th>处理方式</th>
                        </tr>
                        {% for col, desc in report_data.cleaning.missing_report.items() %}
                        <tr>
                            <td>{{ col }}</td>
                            <td>{{ desc }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}

                    {% if 'outlier_report' in report_data.cleaning %}
                    <h3>异常值处理</h3>
                    <table>
                        <tr>
                            <th>列名</th>
                            <th>下界</th>
                            <th>上界</th>
                            <th>处理异常值数量</th>
                        </tr>
                        {% for col, info in report_data.cleaning.outlier_report.items() %}
                        <tr>
                            <td>{{ col }}</td>
                            <td>{{ info.lower_bound | round(2) }}</td>
                            <td>{{ info.upper_bound | round(2) }}</td>
                            <td>{{ info.outliers_count }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                </div>

                <div class="section">
                    <h2>数据可视化</h2>
                    {% for vis in report_data.visualizations %}
                    <div class="visualization">
                        <h3>{{ vis.title }}</h3>
                        <img src="data:image/png;base64,{{ vis.image }}" alt="{{ vis.title }}">
                    </div>
                    {% endfor %}
                </div>

                <div class="section">
                    <h2>数据分析摘要</h2>

                    <h3>数值变量统计</h3>
                    <table>
                        <tr>
                            <th>变量</th>
                            <th>平均值</th>
                            <th>标准差</th>
                            <th>最小值</th>
                            <th>25%分位数</th>
                            <th>中位数</th>
                            <th>75%分位数</th>
                            <th>最大值</th>
                        </tr>
                        {% for col, stats in report_data.analysis.summary.items() %}
                        {% if col in ['count', 'unique', 'top', 'freq'] %}{% else %}
                        <tr>
                            <td>{{ col }}</td>
                            <td>{{ stats.get('mean', '') | round(2) }}</td>
                            <td>{{ stats.get('std', '') | round(2) }}</td>
                            <td>{{ stats.get('min', '') | round(2) }}</td>
                            <td>{{ stats.get('25%', '') | round(2) }}</td>
                            <td>{{ stats.get('50%', '') | round(2) }}</td>
                            <td>{{ stats.get('75%', '') | round(2) }}</td>
                            <td>{{ stats.get('max', '') | round(2) }}</td>
                        </tr>
                        {% endif %}
                        {% endfor %}
                    </table>

                    {% if 'categorical' in report_data.analysis %}
                    <h3>分类变量分析</h3>
                    {% for col, info in report_data.analysis.categorical.items() %}
                    <h4>{{ col }} ({{ info.unique_count }} 个唯一值)</h4>
                    <table>
                        <tr>
                            <th>值</th>
                            <th>计数</th>
                        </tr>
                        {% for value, count in info.top_values.items() %}
                        <tr>
                            <td>{{ value }}</td>
                            <td>{{ count }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endfor %}
                    {% endif %}

                    {% if 'time_series' in report_data.analysis %}
                    <h3>时间序列信息</h3>
                    {% for col, info in report_data.analysis.time_series.items() %}
                    <p><strong>{{ col }}:</strong> 从 {{ info.min_date }} 到 {{ info.max_date }} (时长: {{ info.duration }})</p>
                    {% endfor %}
                    {% endif %}
                </div>

                <div class="section">
                    <h2>总结</h2>
                    <p>数据分析完成于 {{ report_data.file_info.load_time }}。报告包含 {{ report_data.visualizations | length }} 个可视化图表。</p>
                    <p class="success">✓ 数据处理成功完成</p>
                </div>
            </body>
            </html>
            """)

        # 渲染报告
        html_output = template.render(report_data=report_data)

        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"报告已生成: {report_path}")
        return report_path