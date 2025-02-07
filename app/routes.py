from flask import Blueprint, jsonify, request, render_template, current_app
from app.models import StockFund, MixedFund, BondFund, IndexFund, EnhancedFund
from app import db
import traceback

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/funds')
def get_funds():
    try:
        def format_fund_dict(fund):
            data = fund.to_dict()
            
            # 格式化基金代码
            data['code'] = str(data['code']).zfill(6)
            
            # 格式化数值字段
            for key, value in data.items():
                if value is None:
                    continue
                    
                if key.endswith('_score') and value is not None:
                    try:
                        data[key] = float(value)
                    except:
                        data[key] = None
                        
                elif '_growth' in key and value is not None:
                    try:
                        if isinstance(value, str) and '%' in value:
                            data[key] = float(value.strip('%'))
                        else:
                            data[key] = float(value)
                    except:
                        data[key] = None
                        
                elif key == 'scale':
                    # 保持原始格式
                    data[key] = str(value)
                    
            return data

        funds = {
            'stock': [format_fund_dict(fund) for fund in StockFund.query.all()],
            'mixed': [format_fund_dict(fund) for fund in MixedFund.query.all()],
            'bond': [format_fund_dict(fund) for fund in BondFund.query.all()],
            'index': [format_fund_dict(fund) for fund in IndexFund.query.all()]
        }
        
        return jsonify(funds)
    except Exception as e:
        current_app.logger.error(f"Error in get_funds: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': '数据加载失败，请稍后重试'}), 500

@main.route('/api/enhanced-funds')
def get_enhanced_funds():
    try:
        # 获取所有指数增强型基金数据
        funds = EnhancedFund.query.all()
        
        # 将数据转换为字典格式
        fund_list = []
        for fund in funds:
            fund_dict = fund.to_dict()
            # 确保数值格式正确
            if fund_dict['unit_net_value']:
                fund_dict['unit_net_value'] = float(fund_dict['unit_net_value'])
            if fund_dict['accumulate_value']:
                fund_dict['accumulate_value'] = float(fund_dict['accumulate_value'])
            fund_list.append(fund_dict)
            
        return jsonify({
            'funds': fund_list,
            'success': True
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching enhanced funds: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@main.route('/api/hot-funds')
def get_hot_funds():
    try:
        # 获取每种类型的热门基金（按综合评分排序）
        hot_funds = {
            'stock': [fund.to_dict() for fund in StockFund.query.order_by(StockFund.total_score.desc()).limit(5).all()],
            'mixed': [fund.to_dict() for fund in MixedFund.query.order_by(MixedFund.total_score.desc()).limit(5).all()],
            'bond': [fund.to_dict() for fund in BondFund.query.order_by(BondFund.total_score.desc()).limit(5).all()],
            'index': [fund.to_dict() for fund in IndexFund.query.order_by(IndexFund.total_score.desc()).limit(5).all()]
        }
        return jsonify(hot_funds)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/search')
def search_funds():
    try:
        query = request.args.get('q', '')
        fund_type = request.args.get('type', 'all')
        
        if fund_type == 'all':
            results = []
            for Model in [StockFund, MixedFund, BondFund, IndexFund]:
                funds = Model.query.filter(
                    (Model.code.contains(query)) |
                    (Model.name.contains(query))
                ).all()
                results.extend([fund.to_dict() for fund in funds])
            return jsonify({'funds': results})
        else:
            Model = {
                'stock': StockFund,
                'mixed': MixedFund,
                'bond': BondFund,
                'index': IndexFund
            }.get(fund_type)
            
            if not Model:
                return jsonify({'error': '无效的基金类型'}), 400
                
            funds = Model.query.filter(
                (Model.code.contains(query)) |
                (Model.name.contains(query))
            ).all()
            return jsonify({'funds': [fund.to_dict() for fund in funds]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/update-params', methods=['POST'])
def update_params():
    try:
        data = request.get_json()
        # 这里可以添加参数验证和保存逻辑
        # 例如保存到数据库或配置文件
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500