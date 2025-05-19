'''策略2: KDJ金叉周择机买入, 顶背离周择机卖出
'''
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度（避免换行）
pd.set_option('display.max_colwidth', None)  # 显示完整单元格内容


def calculate_kdj(data, n=9, m1=3, m2=3):
    """
    计算KDJ指标
    参数:
        data: DataFrame包含周线数据
        n: KDJ的周期，默认为9
        m1: K值的平滑周期，默认为3
        m2: D值的平滑周期，默认为3
    """
    low_list = data['最低'].rolling(n).min()
    high_list = data['最高'].rolling(n).max()
    rsv = (data['收盘'] - low_list) / (high_list - low_list) * 100
    
    data['K'] = rsv.ewm(alpha=1/m1).mean()  # K值
    data['D'] = data['K'].ewm(alpha=1/m2).mean()  # D值
    data['J'] = 3 * data['K'] - 2 * data['D']  # J值
    
    return data


def convert_to_weekly(daily_df):
    """
    转换为周线数据，处理长假无交易的情况
    返回的周线数据只包含实际有交易的周
    """
    # 添加周标识列
    daily_df = daily_df.copy()
    daily_df['year_week'] = daily_df['日期'].dt.strftime('%Y-%U')
    
    # 按周分组，只保留有交易的周
    weekly_data = []
    for week_id, group in daily_df.groupby('year_week'):
        if len(group) > 0:  # 确保该周有交易数据
            weekly_data.append({
                '日期': group['日期'].iloc[-1],  # 使用该周最后交易日作为周线日期
                '开盘': group['开盘'].iloc[0],
                '收盘': group['收盘'].iloc[-1],
                '最高': group['最高'].max(),
                '最低': group['最低'].min(),
                '成交量': group['成交量'].sum(),
                '成交额': group['成交额'].sum(),
                '交易天数': len(group)  # 记录该周实际交易天数
            })
    
    weekly_df = pd.DataFrame(weekly_data)
    weekly_df = weekly_df.sort_values('日期')
    weekly_df.set_index('日期', inplace=True)
    return weekly_df


def main(csv_fn, start_date=None, end_date=None):
    df = pd.read_csv(csv_fn, parse_dates=['日期', 'Date'])
    df = df.sort_values('日期')

    if start_date and end_date:
        mask = (df['日期'] >= start_date) & (df['日期'] <= end_date)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    weekly_df = convert_to_weekly(filtered_df)

    # 计算周线KDJ
    weekly_df = calculate_kdj(weekly_df)

    # 绘制KDJ图表
    plt.figure(figsize=(14, 10))

    # 子图1: 价格走势
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(weekly_df.index, weekly_df['收盘'], label='收盘价', color='blue')
    plt.title('股票周线走势及KDJ指标')
    plt.ylabel('价格')
    plt.legend()
    plt.grid(True)

    # 设置x轴日期格式
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 子图2: KDJ指标
    ax2 = plt.subplot(2, 1, 2)
    plt.plot(weekly_df.index, weekly_df['K'], label='K值', color='blue')
    plt.plot(weekly_df.index, weekly_df['D'], label='D值', color='orange')
    plt.plot(weekly_df.index, weekly_df['J'], label='J值', color='purple')

    # 添加超买超卖线
    plt.axhline(y=80, color='red', linestyle='--', linewidth=1, label='超买线(80)')
    plt.axhline(y=20, color='green', linestyle='--', linewidth=1, label='超卖线(20)')

    plt.ylabel('KDJ值')
    plt.legend()
    plt.grid(True)

    # 设置x轴日期格式
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 自动调整日期标签
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    csv_fn = r'D:\codes\super-stock\data\all\601600_中国铝业.csv'
    main(
        csv_fn,
        start_date='2021-12-01',
        end_date='2024-12-31'
    )
