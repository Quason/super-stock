import yfinance as yf
import akshare as ak
import pandas as pd
from os.path import join
from datetime import datetime
from dateutil.relativedelta import relativedelta  


INDEX_CODE = {
    'HS300': '000300',
    'ZZ500': '000905',
    'SP500': '^GSPC',
    'NASDAQ': '^IXIC',
    'HSI': '^HSI'
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


def main(index_name, date0, date1):
    if index_name in ['HS300', 'ZZ500']:
        index_data = get_a_share_index(INDEX_CODE[index_name], index_name, date0, date1)
    elif index_name in ['SP500', 'NASDAQ', 'HSI']:
        index_data = get_us_index(INDEX_CODE[index_name], index_name, date0, date1)
    else:
        index_data = get_a_share_index(index_name, index_name, date0, date1)
    index_data = index_data.sort_index().dropna(how='all')   
    new =  index_data.iloc[-1]
    hist_mean =  index_data.mean()
    return new, hist_mean


if __name__ == '__main__':
    index_name = '600036'
    roll_back = 6

    current_date = datetime.now()
    xmonths_ago = current_date - relativedelta(months=roll_back)
    new, hist_mean = main(
        index_name=index_name,
        date0=datetime.strftime(xmonths_ago, '%Y-%m-%d'),
        date1=datetime.strftime(current_date, '%Y-%m-%d')
    )
    print(f'相比历史{roll_back}个月均线涨跌幅:{(new - hist_mean) / hist_mean * 100:.2f}%')
