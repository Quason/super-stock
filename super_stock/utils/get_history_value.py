import akshare as ak
import pandas as pd
import os
import time


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
        return df
    except Exception as e:
        print(f"获取{name}数据失败: {e}")
        return None


def main(stocks_fn, output_dir):
    # 列名为：编号,证券代码,证券简称,上市日期
    stocks_df = pd.read_csv(stocks_fn, dtype={'证券代码': str})
    os.makedirs(output_dir, exist_ok=True)
    for index, row in stocks_df.iterrows():
        code = row["证券代码"]
        name = row["证券简称"]
        file_path = os.path.join(output_dir, f"{code}_{name}.csv")
        if os.path.exists(file_path):
            continue
        # 补充.SZ 或 .SH 后缀
        if code.startswith("6"):
            full_code = f"{code}.SH"
        else:
            full_code = f"{code}.SZ"
        try:
            print(f"正在获取：{full_code} - {name}")
            df = get_a_share_index(code, name, '19900101', '20241231')
            df = df.sort_index().dropna(how='all')
            df.to_csv(file_path, encoding="utf-8-sig", index=False)
            time.sleep(1)  # 防止请求过快被封

        except Exception as e:
            print(f"失败：{full_code} - {name}，原因：{e}")


if __name__ == '__main__':
    stocks_fn = r"D:\codes\super-stock\data\all_stocks_codes.csv"
    output_dir = r"D:\codes\super-stock\data\all"
    main(stocks_fn, output_dir)
