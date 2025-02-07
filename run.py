from app import create_app, db
from app.models import StockFund, MixedFund, BondFund, IndexFund, EnhancedFund  # 添加EnhancedFund
import pandas as pd
import os

app = create_app()

def init_db():
    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        csv_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # 修改 csv_files 映射，添加指数增强型基金
        csv_files = {
            'stock': ('股票型.csv', StockFund),
            'mixed': ('混合型.csv', MixedFund),
            'bond': ('债券型.csv', BondFund),
            'index': ('指数型.csv', IndexFund),
            'enhanced': ('指数增强型.csv', EnhancedFund)  # 添加指数增强型
        }
        
        imported_codes = set()  # 跟踪已导入的代码
        
        # 新增指数增强型基金的列映射
        enhanced_column_map = {
            '代码': 'code',
            '简称': 'name',
            '单位净值': 'unit_net_value',
            '累计净值': 'accumulate_value',
            '日增长率': 'daily_growth',  # 确保这里的映射正确
            '近1周': 'week_growth',
            '近1月': 'month_growth',
            '近3月': 'm3_growth',
            '近6月': 'm6_growth',
            '近1年': 'y1_growth',
            '近2年': 'y2_growth',
            '近3年': 'y3_growth',
            '今年来': 'ytd_growth',
            '成立来': 'since_launch'
        }
        
        # 更新列映射关系
        column_map = {
            '代码': 'code',
            '简称': 'name',
            '基金经理': 'manager',
            '基金公司': 'company',
            '规模': 'scale',
            '资产规模': 'scale',
            '管理规模': 'management_scale',  # 添加管理规模映射
            '评级评分': 'rating_score',
            '涨幅评分': 'growth_score',
            '业绩评分': 'performance_score',
            '综合评分': 'total_score',
            '上海证券评级': 'shanghai_rating',
            '招商证券评级': 'merchant_rating',
            '济安金信评级': 'jian_rating',
            '晨星评级': 'morning_star_rating',
            '近3月涨幅': 'm3_growth',
            '近3月四分位': 'm3_quartile',
            '近6月涨幅': 'm6_growth',
            '近6月四分位': 'm6_quartile',
            '近1年涨幅': 'y1_growth',
            '近1年四分位': 'y1_quartile',
            '近2年涨幅': 'y2_growth',
            '近2年四分位': 'y2_quartile',
            '近3年涨幅': 'y3_growth',
            '近3年四分位': 'y3_quartile',
            '近5年涨幅': 'y5_growth',
            '近5年四分位': 'y5_quartile',
            '选证能力': 'selection_ability',
            '收益率': 'return_rate',
            '抗风险': 'risk_resistance',
            '稳定性': 'stability',
            '管理能力': 'management_ability',
            '择时能力': 'timing',  # 添加择时能力映射
            '跟踪误差': 'tracking_error',  # 添加跟踪误差映射
            '超额收益': 'excess_return'  # 添加超额收益映射
        }
        
        column_map.update(enhanced_column_map)
        
        for file_type, (filename, model) in csv_files.items():
            file_path = os.path.join(csv_dir, filename)
            try:
                if not os.path.exists(file_path):
                    print(f"Warning: {filename} not found in {csv_dir}")
                    continue
                    
                df = pd.read_csv(file_path, encoding='utf-8')
                print(f"Columns in {filename}: {df.columns.tolist()}")  # 添加调试信息
                
                # 重命名列
                rename_cols = {k: v for k, v in column_map.items() if k in df.columns}
                df = df.rename(columns=rename_cols)
                
                # 数据预处理
                df = df.where(pd.notnull(df), None)
                df = df.drop_duplicates(subset=['code'])
                
                for _, row in df.iterrows():
                    if row['code'] not in imported_codes:
                        data = {k: v for k, v in row.to_dict().items() 
                               if hasattr(model, k) and pd.notna(v)}
                        
                        # 特殊处理数值型字段，扩展处理字段列表
                        numeric_fields = [
                            'rating_score', 'growth_score', 'performance_score', 
                            'total_score', 'selection_ability', 'return_rate',
                            'risk_resistance', 'stability', 'management_ability',
                            'timing', 'tracking_error', 'excess_return', 
                            'management_scale'  # 添加管理规模
                        ]
                        
                        for field in numeric_fields:
                            if field in data and isinstance(data[field], str):
                                try:
                                    data[field] = float(data[field])
                                except:
                                    data[field] = None
                        
                        # 特殊处理资产规模数据
                        if 'scale' in data:
                            # 保持原始格式，包括单位
                            data['scale'] = str(data['scale'])
                            print(f"Processing scale for fund {data['code']}: {data['scale']}")  # 添加调试信息
                                    
                        fund = model(**data)
                        db.session.add(fund)
                        imported_codes.add(row['code'])
                        
                print(f"Successfully imported {filename}")
                    
            except Exception as e:
                print(f"Error importing {filename}: {str(e)}")
                db.session.rollback()
                continue
                
        try:
            db.session.commit()
            print("Database initialization completed")
        except Exception as e:
            print(f"Error committing to database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    try:
        init_db()
        # 修改运行参数，确保外部可访问
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=False  # 生产环境设置为False
        )
    except Exception as e:
        print(f"Application error: {str(e)}")