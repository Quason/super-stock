import csv
import sqlite3
from datetime import datetime
from os.path import join, split
from glob import glob
from tqdm import tqdm


def create_stock_table(db_path):
    """创建股票数据表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率,Date
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_data (
        code TEXT,               -- 股票代码
        name TEXT,               -- 股票名称
        date DATE,               -- 日期
        open REAL,               -- 开盘价
        close REAL,              -- 收盘价
        high REAL,               -- 最高价
        low REAL,                -- 最低价
        volume INTEGER,          -- 成交量
        amount REAL,             -- 成交额
        amplitude REAL,          -- 振幅
        change_percent REAL,     -- 涨跌幅
        change_amount REAL,      -- 涨跌额
        turnover_rate REAL,      -- 换手率
        PRIMARY KEY (code, date) -- 联合主键
    )
    ''')
    
    conn.commit()
    conn.close()


def import_csv_to_sqlite(csv_file, db_path, code, name):
    """将CSV数据导入SQLite数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # 转换日期格式为SQLite兼容的格式 (假设CSV中的日期格式为YYYY-MM-DD)
            date_str = row['日期']
            
            try:
                # 尝试解析日期，确保格式正确
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y-%m-%d')
                
                cursor.execute('''
                INSERT OR REPLACE INTO stock_data (
                    code, name, date, open, close, high, low, volume, amount, 
                    amplitude, change_percent, change_amount, turnover_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    code,
                    name,
                    formatted_date,
                    float(row['开盘']),
                    float(row['收盘']),
                    float(row['最高']),
                    float(row['最低']),
                    int(float(row['成交量'])),
                    float(row['成交额']),
                    float(row['振幅']),
                    float(row['涨跌幅']),
                    float(row['涨跌额']),
                    float(row['换手率'])
                ))
                
            except ValueError as e:
                print(f"跳过无效数据行 (日期: {date_str}): {e}")
                continue
    
    conn.commit()
    conn.close()
    print(f"数据已成功导入到 {db_path}")


if __name__ == "__main__":
    # 配置参数
    csv_path = r'D:\codes\super-stock\data\all'
    sqlite_db_path = r"C:\Apps\sqlite\dbs\stocks.db"
    # create_stock_table(sqlite_db_path)

    fns = glob(join(csv_path, '*.csv'))
    for csv_file_path in tqdm(fns):
        code, name = split(csv_file_path)[-1].replace('.csv', '').split('_')
        import_csv_to_sqlite(csv_file_path, sqlite_db_path, code, name)
