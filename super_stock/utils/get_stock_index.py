import yfinance as yf
import akshare as ak
import pandas as pd
from os.path import join


INDEX_CODE = {
    'HS300': '000300',
    'ZZ500': '000905',
    'SP500': '^GSPC',
    'NASDAQ': '^IXIC'
}


def get_a_share_index(symbol, name, date0, date1):
    """获取A股指数数据"""
    try:
        df = ak.index_zh_a_hist(
            symbol=symbol, 
            period="daily", 
            start_date=date0.replace('-', ''), 
            end_date=date1.replace('-', '')
        )
        df['Date'] = pd.to_datetime(df['日期'])
        return df.set_index('Date')['收盘'].rename(name)
    except Exception as e:
        print(f"获取{name}数据失败: {e}")
        return None
    

def get_us_index(ticker, name, date0, date1):
    """获取美股指数数据"""
    try:
        nasdaq = yf.Ticker(ticker)
        data = nasdaq.history(start=date0, end=date1)
        return data['Close'].rename(name)
    except Exception as e:
        print(f"获取{name}数据失败: {e}")
        return None


def main(index_name, date0, date1, dst_fn):
    if index_name in ['HS300', 'ZZ500']:
        index_data = get_a_share_index(INDEX_CODE[index_name], index_name, date0, date1)
    elif index_name in ['SP500', 'NASDAQ']:
        index_data = get_us_index(INDEX_CODE[index_name], index_name, date0, date1)
    # 处理缺失值并排序
    index_data = index_data.sort_index().dropna(how='all')
    # 保存结果
    index_data.to_csv(dst_fn, encoding="utf-8-sig")


if __name__ == '__main__':
    dst_dir = 'D:\codes\super-stock\data'
    indexes = ['SP500', 'NASDAQ']
    for index_name in indexes:
        print(f'{index_name}...')
        main(
            index_name=index_name,
            date0='2008-01-01',
            date1='2024-12-31',
            dst_fn=join(dst_dir, f'{index_name}.csv')
        )
