import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
from tqdm import tqdm


def get_all_stocks():
    """获取沪深两市全部A股列表"""
    # 上证
    sh = ak.stock_info_sh_name_code(symbol="主板A股")  # 证券代码, 证券简称, 公司全称, 上市日期
    float_data = []
    for code in tqdm(sh['证券代码'], desc="正在采集数据"):
        try:
            profile = ak.stock_individual_info_em(symbol=code)
            profile_dict = dict(zip(profile['item'], profile['value']))            
            float_data.append({
                '证券代码': code,
                '证券简称': sh.loc[sh['证券代码']==code, '证券简称'].values[0],
                '上市日期': sh.loc[sh['证券代码']==code, '上市日期'].values[0],
                '流通股本': float(profile_dict.get('流通股'))
            })
            time.sleep(0.5)
        except Exception as e:
            print(f"\n获取 {code} 数据失败: {str(e)[:50]}...")
            continue
    sh = pd.DataFrame(float_data)
    
    # 深证
    sz = ak.stock_info_sz_name_code(symbol="A股列表")  # 板块, A股代码, A股简称, A股上市日期, A股总股本, A股流通股本, 所属行业
    sz['A股流通股本'] = sz['A股流通股本'].str.replace(',', '').astype(float)
    sz = sz[['A股代码', 'A股简称', 'A股上市日期', 'A股流通股本']].rename(columns={
        'A股代码': '证券代码',
        'A股简称': '证券简称',
        'A股上市日期': '上市日期',
        'A股流通股本': '流通股本'
    })

    return pd.concat([sh, sz])[['证券代码', '证券简称', '上市日期', '流通股本']]


def get_listing_date(stock_code):
    """获取上市日期"""
    try:
        if stock_code.startswith('6'):
            info = ak.stock_individual_info_em(symbol=f"sh{stock_code}")
        else:
            info = ak.stock_individual_info_em(symbol=f"sz{stock_code}")
        date_str = info.loc[info['item'] == '上市日期', 'value'].iloc[0]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except Exception as e:
        print(f"获取{stock_code}上市日期失败：{e}")
        return None


def get_historical_price(stock_code, target_date):
    """获取指定日期历史价格（前复权）"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                              start_date=target_date.strftime("%Y%m%d"),
                              end_date=(target_date + timedelta(days=3)).strftime("%Y%m%d"),
                              adjust="hfq")
        return df.iloc[0]['收盘'] if not df.empty else None
    except Exception as e:
        print(f"获取{stock_code}历史数据失败：{e}")
        return None


def get_current_price(stock_code):
    """获取实时最新价格"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df[df['代码'] == stock_code]['最新价'].values[0]
    except Exception as e:
        print(f"获取{stock_code}实时价格失败：{e}")
        return None


if __name__ == "__main__":
    all_stocks = get_all_stocks()
    all_stocks.to_csv('./data/all_stocks_codes.csv', encoding="utf-8-sig")
    exit(0)

    result = []
    
    ten_years_ago = datetime.now() - timedelta(days=365*10)
    
    for idx, row in all_stocks.iterrows():
        code = row['代码']
        name = row['证券简称']
        print(f"正在处理 {name}({code})...")
        
        # 获取上市日期
        listing_date = get_listing_date(code)
        if not listing_date:
            continue
        
        # 确定基准日期
        if listing_date <= ten_years_ago:
            base_date = ten_years_ago
        else:
            base_date = listing_date
        
        # 获取基准价格
        base_price = get_historical_price(code, base_date)
        if not base_price:
            continue
        
        # 获取当前价格
        current_price = get_current_price(code)
        if not current_price:
            continue
        
        result.append({
            '股票名': name,
            '股票代码': code,
            '基准价格': round(base_price, 2),
            '当前价格': round(current_price, 2)
        })
        
        time.sleep(1)  # 防止请求过于频繁
    
    # 保存结果
    pd.DataFrame(result).to_csv("stock_price_comparison.csv", index=False)
    print("数据已保存至 stock_price_comparison.csv")
