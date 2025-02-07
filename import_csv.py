import pandas as pd
import os
from app import create_app, db
from app.models import StockFund, MixedFund, BondFund, IndexFund, EnhancedFund
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_column_mappings(fund_type):
    """根据基金类型获取列映射关系"""
    if fund_type == EnhancedFund:
        # 确保列名与CSV文件完全一致
        enhanced_mappings = {
            '代码': 'code',
            '简称': 'name', 
            '单位净值': 'unit_net_value',
            '累计净值': 'acc_net_value',
            '日增长率': 'daily_growth',
            '近1周': 'w1_growth',
            '近1月': 'm1_growth', 
            '近3月': 'm3_growth',
            '近6月': 'm6_growth',
            '近1年': 'y1_growth',
            '近2年': 'y2_growth', 
            '近3年': 'y3_growth',
            '今年来': 'ytd_growth',
            '成立来': 'since_launch'
        }
        return enhanced_mappings
    
    # 基础映射
    base_mappings = {
        '代码': 'code',
        '简称': 'name',
        '基金经理': 'manager',
        '基金公司': 'company',
        '资产规模': 'scale',
        '评级评分': 'rating_score',
        '涨幅评分': 'growth_score',
        '业绩评分': 'performance_score',
        '综合评分': 'total_score',
        '上海证券评级': 'shanghai_rating',
        '招商证券评级': 'merchant_rating',
        '济安金信评级': 'jian_rating',
        '晨星评级': 'morning_star_rating',
        '近3月涨幅': 'm3_growth',
        '近6月涨幅': 'm6_growth',
        '近1年涨幅': 'y1_growth',
        '近3年涨幅': 'y3_growth',
        '近5年涨幅': 'y5_growth',
        '选证能力': 'selection_ability',
        '收益率': 'return_rate'
    }

    # 根据基金类型添加特有字段
    if fund_type in [StockFund, MixedFund]:
        base_mappings.update({
            '择时能力': 'timing',
            '抗风险': 'risk_resistance',
            '稳定性': 'stability'
        })
    elif fund_type == BondFund:
        base_mappings.update({
            '抗风险': 'risk_resistance',
            '稳定性': 'stability',
            '管理规模': 'management_scale'
        })
    elif fund_type == IndexFund:
        base_mappings.update({
            '跟踪误差': 'tracking_error',
            '超额收益': 'excess_return',
            '管理规模': 'management_scale'
        })

    return base_mappings

def process_value(value, field):
    """处理不同类型字段的值"""
    if pd.isna(value) or value == '' or value == '--':
        return None

    try:
        if field == 'scale':
            # 直接返回原始字符串值，包含单位
            return str(value) if value else None
            
        # 处理净值字段
        if field in ['unit_net_value', 'acc_net_value']:
            return float(value) if value else None
            
        # 处理增长率字段
        if field in ['daily_growth', 'w1_growth', 'm1_growth', 'm3_growth', 
                    'm6_growth', 'y1_growth', 'y2_growth', 'y3_growth',
                    'ytd_growth', 'since_launch']:
            if isinstance(value, str) and '%' in value:
                return float(value.strip('%'))
            return float(value) if value else None
            
        # 处理其他数值字段
        if field in ['selection_ability', 'return_rate', 'risk_resistance', 
                    'stability', 'management_scale', 'tracking_error', 
                    'excess_return', 'timing']:
            return float(value) if value else None
            
        # 保留原始值
        return value
        
    except (ValueError, TypeError) as e:
        logging.warning(f"处理字段 {field} 的值 {value} 时出错: {str(e)}")
        return None

def import_csv_to_db():
    """导入CSV文件到数据库"""
    app = create_app()
    
    with app.app_context():
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            if not os.path.exists(data_dir):
                logging.error(f"数据目录不存在: {data_dir}")
                return False

            file_mappings = {
                '股票型.csv': StockFund,
                '混合型.csv': MixedFund,
                '债券型.csv': BondFund,
                '指数型.csv': IndexFund,
                '指数增强型.csv': EnhancedFund  # 添加指数增强型数据文件映射
            }

            # 清空现有数据
            logging.info("清空现有数据...")
            for model in file_mappings.values():
                model.query.delete()
            db.session.commit()
            
            total_imported = 0
            
            for filename, model in file_mappings.items():
                file_path = os.path.join(data_dir, filename)
                if not os.path.exists(file_path):
                    logging.warning(f"文件不存在: {filename}")
                    continue

                logging.info(f"正在处理: {filename}")
                try:
                    # 读取CSV文件
                    df = pd.read_csv(file_path, encoding='utf-8')
                    logging.info(f"CSV列名: {df.columns.tolist()}")  # 添加日志输出
                    
                    # 获取列映射
                    column_map = get_column_mappings(model)
                    logging.info(f"映射关系: {column_map}")  # 添加日志输出
                    
                    # 检查列是否存在
                    available_columns = {}
                    for csv_col, db_col in column_map.items():
                        if csv_col in df.columns:
                            available_columns[csv_col] = db_col
                        else:
                            logging.warning(f"列 '{csv_col}' 在CSV中不存在")
                            
                    if not available_columns:
                        logging.error(f"没有找到可用的列映射关系")
                        continue
                        
                    # 重命名列
                    df = df.rename(columns=available_columns)
                    
                    # 数据预处理
                    for idx, row in df.iterrows():
                        try:
                            fund_data = {}
                            for db_col in available_columns.values():
                                if hasattr(model, db_col):
                                    value = row.get(db_col)
                                    processed_value = process_value(value, db_col)
                                    if processed_value is not None:
                                        fund_data[db_col] = processed_value
                            
                            if 'code' in fund_data:
                                fund = model(**fund_data)
                                db.session.add(fund)
                                total_imported += 1
                                if idx % 100 == 0:  # 每100条记录输出一次日志
                                    logging.info(f"已处理 {idx} 条记录")
                            else:
                                logging.warning(f"第 {idx} 行缺少代码字段")
                                
                        except Exception as e:
                            logging.error(f"处理记录失败 (行 {idx}): {str(e)}")
                            continue
                            
                    db.session.commit()
                    logging.info(f"成功导入 {filename}, 导入数量: {total_imported}")
                    
                except Exception as e:
                    logging.error(f"处理文件 {filename} 时出错: {str(e)}")
                    db.session.rollback()
                    continue

            logging.info(f"数据导入完成，共导入 {total_imported} 条记录")
            return True

        except Exception as e:
            logging.error(f"导入过程中发生错误: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if import_csv_to_db():
        print("数据导入成功")
    else:
        print("数据导入失败")
