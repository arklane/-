from app import db
from flask import current_app

class FundBase(db.Model):
    __abstract__ = True
    
    # 基本信息
    code = db.Column(db.String(20), primary_key=True)  # 代码
    name = db.Column(db.String(100))  # 简称
    manager = db.Column(db.String(50))  # 基金经理
    company = db.Column(db.String(100))  # 基金公司
    scale = db.Column(db.String(50))  # 资产规模，使用String类型以保留完整格式
    
    # 评级信息
    rating_score = db.Column(db.Float)  # 评级评分
    growth_score = db.Column(db.Float)  # 涨幅评分
    performance_score = db.Column(db.Float)  # 业绩评分
    total_score = db.Column(db.Float)  # 综合评分
    shanghai_rating = db.Column(db.String(10))  # 上海证券评级
    merchant_rating = db.Column(db.String(10))  # 招商证券评级
    jian_rating = db.Column(db.String(10))  # 济安金信评级
    morning_star_rating = db.Column(db.String(10))  # 晨星评级
    
    # 历史涨幅
    m3_growth = db.Column(db.String(20))  # 近3月涨幅
    m3_quartile = db.Column(db.String(20))  # 近3月四分位
    m6_growth = db.Column(db.String(20))  # 近6月涨幅
    m6_quartile = db.Column(db.String(20))  # 近6月四分位
    y1_growth = db.Column(db.String(20))  # 近1年涨幅
    y1_quartile = db.Column(db.String(20))  # 近1年四分位
    y2_growth = db.Column(db.String(20))  # 近2年涨幅
    y2_quartile = db.Column(db.String(20))  # 近2年四分位
    y3_growth = db.Column(db.String(20))  # 近3年涨幅
    y3_quartile = db.Column(db.String(20))  # 近3年四分位
    y5_growth = db.Column(db.String(20))  # 近5年涨幅
    y5_quartile = db.Column(db.String(20))  # 近5年四分位

    # 基础能力指标
    stock_selection = db.Column(db.Float)  # 选证能力
    return_rate = db.Column(db.Float)  # 收益率
    risk_resistance = db.Column(db.Float)  # 抗风险
    stability = db.Column(db.Float)  # 稳定性
    management_scale = db.Column(db.Float)  # 管理规模

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StockFund(FundBase):
    __tablename__ = 'stock_funds'
    
    # 特有指标
    selection_ability = db.Column(db.Float)
    timing = db.Column(db.Float)  # 确保有择时能力字段
    management_ability = db.Column(db.Float)

class BondFund(FundBase):
    __tablename__ = 'bond_funds'
    
    # 特有指标
    selection_ability = db.Column(db.Float)
    timing = db.Column(db.Float)
    management_scale = db.Column(db.Float)  # 确保有管理规模字段

class MixedFund(FundBase):
    __tablename__ = 'mixed_funds'
    
    # 特有指标
    selection_ability = db.Column(db.Float)  # CSV中的"选证能力"
    timing = db.Column(db.Float)  # CSV中的"择时能力"

class IndexFund(FundBase):
    __tablename__ = 'index_funds'
    
    # 特有指标
    selection_ability = db.Column(db.Float)  # 确保有选证能力字段
    timing = db.Column(db.Float)  # CSV中的"择时能力"
    tracking_error = db.Column(db.Float)  # 确保有跟踪误差字段
    excess_return = db.Column(db.Float)  # 确保有超额收益字段
    management_scale = db.Column(db.Float)  # 确保有管理规模字段

class EnhancedFund(db.Model):
    __tablename__ = 'enhanced_funds'
    
    # 主键和基本信息
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100))
    
    # 净值信息
    unit_net_value = db.Column(db.Float)
    accumulate_value = db.Column(db.Float)
    daily_growth = db.Column(db.String(20))
    
    # 不同时间段涨幅
    week_growth = db.Column(db.String(20))
    month_growth = db.Column(db.String(20))
    m3_growth = db.Column(db.String(20))
    m6_growth = db.Column(db.String(20))
    y1_growth = db.Column(db.String(20))
    y2_growth = db.Column(db.String(20))
    y3_growth = db.Column(db.String(20))
    ytd_growth = db.Column(db.String(20))
    since_launch = db.Column(db.String(20))

    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'unit_net_value': self.unit_net_value,
            'accumulate_value': self.accumulate_value,
            'daily_growth': self.daily_growth,
            'week_growth': self.week_growth,
            'month_growth': self.month_growth,
            'm3_growth': self.m3_growth,
            'm6_growth': self.m6_growth,
            'y1_growth': self.y1_growth,
            'y2_growth': self.y2_growth,
            'y3_growth': self.y3_growth,
            'ytd_growth': self.ytd_growth,
            'since_launch': self.since_launch
        }