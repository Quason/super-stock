''' 策略1
    每个月10号计算历史3年的指标均值和当前值进行对比:
        相差在 ±4% 之内, 进行1000元定投;
        当前值相比均值下跌超过 4%, 进行2000元定投;
        当前值相比均值上涨超过 4%, 不进行操作。
'''
import pandas as pd
import numpy as np
import math
from os.path import join, split


def main(df, index_name, diff_thresh=0.04, unit_share=1000, date_step=36):
    '''
        src_fn: 指数存档文件
        diff_thresh: 变化反应阈值(默认4%)
        unit_share: 定投单位金额(默认1000)
        date_step: 回朔时间(默认3年)
    '''
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').set_index('Date')
    # 生成每月10号的数据点（自动对齐最近的有效交易日）
    monthly_data = df.resample('MS').first().shift(9, freq='D').dropna()  # 每月10号
    monthly_data = df.reindex(monthly_data.index, method='ffill')  # 用前向填充获取有效数据

    # 初始化投资记录
    total_investment = 0  # 累计投入本金
    total_shares = 0      # 累计持有份额
    trade_log = []        # 交易记录

    # 策略执行
    for current_date in monthly_data.index[2:]:
        # 获取当前价格和历史数据
        current_price = monthly_data.loc[current_date, index_name]
        start_date = current_date - pd.DateOffset(months=date_step)
        hist_prices = monthly_data.loc[start_date:current_date - pd.DateOffset(days=1), index_name]
        
        # 计算均值和涨跌幅
        mean_price = hist_prices.mean()
        pct_diff = (current_price - mean_price) / mean_price
        
        # 执行交易逻辑
        if pct_diff < -diff_thresh:
            investment = unit_share * math.ceil(pct_diff / diff_thresh)
        elif abs(pct_diff) <= diff_thresh:
            investment = unit_share
        else:
            investment = 0
        
        # 记录交易
        if investment > 0:
            shares = investment / current_price
            total_shares += shares
            total_investment += investment
            trade_log.append({
                'date': current_date,
                'action': f'定投{investment}元',
                'price': current_price,
                'shares': shares
            })

    # 计算最终收益（以最后一个交易日收盘价计算）
    final_price = df[index_name].iloc[-1]
    total_assets = total_shares * final_price
    total_return = total_assets - total_investment

    # 输出结果
    print(f"策略执行期间共定投 {len(trade_log)} 次")
    print(f"累计投入本金: {total_investment:.2f} 元")
    print(f"最终持有份额: {total_shares:.2f}")
    print(f"最终资产价值: {total_assets:.2f} 元")
    print(f"绝对收益: {total_return:.2f} 元")
    print(f"收益率: {total_return/total_investment*100:.2f}%")

    # 可选：保存交易记录
    # pd.DataFrame(trade_log).to_csv('交易记录.csv', index=False)


if __name__ == '__main__':
    src_fn = r'D:\codes\super-stock\data\HS300.csv'

    index_name = split(src_fn)[-1].split('.')[0]
    df = pd.read_csv(src_fn)

    main(df, index_name, diff_thresh=0.04, unit_share=1000, date_step=12)
    
