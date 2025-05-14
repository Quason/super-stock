"""
A股智能选股框架 v1.0
功能：支持自定义时间窗口内按涨跌幅/流通市值的多条件排序
架构：分层设计（数据层/服务层/展示层）
"""
import sqlite3
import pandas as pd
from datetime import datetime
import time

pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度（避免换行）
pd.set_option('display.max_colwidth', None)  # 显示完整单元格内容


class DataManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_price_data(self, start_date, end_date):
        """获取指定时间段的行情数据"""
        query = f'''SELECT code, name, date, close 
                   FROM stock_data 
                   WHERE date BETWEEN '{start_date}' AND '{end_date}'
                   ORDER BY code, date'''
        return pd.read_sql(query, self.conn)
    
    def get_float_shares(self):
        """获取股票流通股本"""
        return pd.read_sql("SELECT code, name FROM stock_basic", self.conn)


# ==================== 服务层 ====================
class StockSelector:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def calculate_returns(self, df):
        """计算个股区间涨跌幅"""
        grouped = df.groupby('name')['close']
        start_prices = grouped.first().rename('start_price')
        end_prices = grouped.last().rename('end_price')
        result = ((end_prices - start_prices) / start_prices * 100)
        return result.to_frame('pct_change').reset_index()
    
    def calculate_market_val(self, close_series, float_shares):
        """计算流通市值（亿元）"""
        return (close_series * float_shares).rename('market_val')
    
    def select_stocks(self, start_date, end_date, sort_conditions):
        """
        核心选股逻辑
        :param sort_conditions: 排序条件列表 例: [('pct_chg', False), ('market_val', True)]
        """
        # 获取基础数据
        price_data = self.dm.get_price_data(start_date, end_date)
        
        # 计算指标
        returns = self.calculate_returns(price_data)  # 区间涨幅
        merged = returns
        
        # 执行多条件排序
        merged = merged.sort_values(by=['pct_change'], ascending=False)
        return merged.rename(columns={'pct_change': '涨跌幅(%)'})


# ==================== 展示层/API层 ====================
def cli_interface(start, end, choice, db_path):
    """命令行交互界面"""
    dm = DataManager(db_path)
    selector = StockSelector(dm)

    conditions = []
    if choice == '1':
        conditions.append(('pct_chg', False))
    elif choice == '2':
        conditions.append(('market_val', True))
    elif choice == '3':
        conditions.append(('market_val', False))
    
    # 执行查询
    result = selector.select_stocks(start, end, conditions)
    print("\n排序结果：")
    print(result.head(100))


if __name__ == '__main__':
    cli_interface(
        start='2024-01-01',
        end='2024-12-31',
        choice='1',
        db_path=r"C:\Apps\sqlite\dbs\stocks.db"
    )
