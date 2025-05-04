import pandas as pd
import matplotlib.pyplot as plt


plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题


def stock_stat(file_path):
    data = pd.read_csv(file_path, dtype={'证券代码': str})
    # 提取年份和交易所分类
    data['上市年份'] = pd.to_datetime(data['上市日期']).dt.year
    data['交易所'] = data['证券代码'].apply(lambda x: 
        '上证' if str(x).startswith('60') else 
        ('深证' if str(x).startswith('00') else 
        ('创业板' if str(x).startswith('30') else '其他')))
    # 按年份和交易所统计公司数量
    result = data.groupby(['上市年份', '交易所']).size().unstack(fill_value=0)
    # 绘制分组柱状图
    colors = {'上证': 'red', '深证': 'blue', '创业板': 'green'}  # 自定义颜色
    ax = result.plot(kind='bar', 
                    color=[colors.get(col, 'gray') for col in result.columns],
                    figsize=(12, 6),
                    width=0.8)
    # 图表美化
    plt.title('各年份上市公司数量统计', fontsize=15)
    plt.xlabel('上市年份', fontsize=12)
    plt.ylabel('公司数量', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    # 调整图例位置
    ax.legend(title='交易所', bbox_to_anchor=(1.05, 1), loc='upper left')
    # 显示数值标签（可选）
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f"{int(p.get_height())}", 
                        (p.get_x() + p.get_width() / 2, p.get_height()), 
                        ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    stock_stat(r'D:\codes\super-stock\data\all_stocks_codes.csv')
