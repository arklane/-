import csv
import time
import random
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import os
from datetime import datetime  # 添加此导入
from app import create_app, db
from app.models import StockFund, MixedFund, BondFund, IndexFund, EnhancedFund
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取JSON配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    WEIGHTS = json.load(f)

# 从配置文件获取权重
pjpfqz = WEIGHTS["评级评分权重"]
yjpfqz = WEIGHTS["业绩评分权重"]
zfpfqz = WEIGHTS["涨幅评分权重"]

def convert_rating(rating_text):
    if '暂无评级' in rating_text:
        return 3
    return rating_text.count('★')

def fetch_fund_data(playwright, url):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')
    
    # 等待页面加载完成
    page.wait_for_timeout(5000)
    
    # 获取页面中的所有数据
    page_content = page.content()
    
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # 提取基金数据
    funds = []
    rows = soup.select('tr')
    for row in rows:
        code = row.select_one('td.dm a')
        name = row.select_one('td.jc a')
        shanghai_rating = row.select_one('td.shzq')
        citi_rating = row.select_one('td.zszq')
        jian_rating = row.select_one('td.jazq')
        morningstar_rating = row.select_one('td.cxzq')
        manager = row.select_one('td.jjjl a:nth-of-type(2)')  # 确保选择正确的基金经理链接
        company = row.select_one('td.jjgs a')
        
        if code and name and morningstar_rating and citi_rating and jian_rating and shanghai_rating and manager and company:
            funds.append({
                'code': code.get_text(strip=True),
                'name': name.get_text(strip=True),
                'manager': manager.get_text(strip=True),
                'company': company.get_text(strip=True),
                'shanghai_rating': convert_rating(shanghai_rating.get_text(strip=True)),
                'citi_rating': convert_rating(citi_rating.get_text(strip=True)),
                'jian_rating': convert_rating(jian_rating.get_text(strip=True)),
                'morningstar_rating': convert_rating(morningstar_rating.get_text(strip=True))
            })
    
    browser.close()
    return funds

def get_fund_performance(fund_code):
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jdzf&code={fund_code}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    performance_data = {}
    periods = ['近3月', '近6月', '近1年', '近2年', '近3年', '近5年']

    # 查找包含数据的div
    data_div = soup.find('div', {'class': 'jdzfnew'})
    if data_div:
        ul_elements = data_div.find_all('ul')
        for ul in ul_elements:
            title_element = ul.find('li', {'class': 'title'})
            if title_element:
                title = title_element.text.strip()
                if title in periods:
                    performance_element = ul.find_all('li')[1]
                    quartile_element = ul.find('p', {'class': 'sifen'})
                    performance = performance_element.text.strip() if performance_element else 'N/A'
                    quartile = quartile_element.text.strip() if quartile_element else 'N/A'
                    performance_data[title] = {
                        'growth': performance,
                        'quartile': quartile
                    }

    return performance_data

def fetch_additional_data(playwright, fund_code, max_retries=3):
    additional_data = {}
    data_complete = True  # 添加数据完整性标志

    retries = 0
    while retries < max_retries:
        try:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 获取基本信息页面的资产规模
            basic_info_url = f"https://fundf10.eastmoney.com/{fund_code}.html"
            page.goto(basic_info_url, timeout=90000, wait_until='networkidle')
            page.wait_for_timeout(5000)
            basic_info_content = page.content()
            basic_info_soup = BeautifulSoup(basic_info_content, 'html.parser')
            
            # 提取资产规模
            bs_gl_div = basic_info_soup.find('div', {'class': 'bs_gl'})
            if bs_gl_div:
                labels = bs_gl_div.find_all('label')
                for label in labels:
                    if '资产规模' in label.text:
                        scale_text = label.find('span').text.strip()
                        scale_match = re.match(r'([\d.]+)亿元', scale_text)
                        if scale_match:
                            additional_data['资产规模'] = f"{scale_match.group(1)}亿元"
                        break
            
            # 获取评分数据
            tsdata_url = f"https://fundf10.eastmoney.com/tsdata_{fund_code}.html"
            page.goto(tsdata_url, timeout=90000, wait_until='networkidle')
            page.wait_for_timeout(5000)
            tsdata_content = page.content()
            tsdata_soup = BeautifulSoup(tsdata_content, 'html.parser')
            
         # 修改：提取和处理Scores数据
            script_tags = tsdata_soup.find_all('script', type='text/javascript')
            scores_found = False
            scores_name_found = False
            
            for script in script_tags:
                script_content = script.string if script.string else ''
                if script_content:
                    scores_match = re.search(r'var\s+Scores\s*=\s*(\[.*?\])', script_content, re.DOTALL)
                    scores_name_match = re.search(r'var\s+ScoresName\s*=\s*(\[.*?\])', script_content, re.DOTALL)
                    
                    if scores_match and scores_name_match:
                        try:
                            scores_str = scores_match.group(1).replace("'", '"')
                            scores_name_str = scores_name_match.group(1).replace("'", '"')
                            additional_data['Scores'] = json.loads(scores_str)
                            additional_data['ScoresName'] = json.loads(scores_name_str)
                            scores_found = True
                            scores_name_found = True
                        except json.JSONDecodeError:
                            print(f"基金代码 {fund_code}: 数据解析失败")
                            data_complete = False
                            break
            
            if not scores_found or not scores_name_found:
                print(f"基金代码 {fund_code}: 未找到完整的评分数据")
                data_complete = False
            
            # 获取业绩数据
            performance_data = get_fund_performance(fund_code)
            additional_data.update(performance_data)
            
            break
            
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            retries += 1
            print(f"加载页面失败: {e}，重试 {retries}/{max_retries}")
            time.sleep(random.uniform(1, 3))
        finally:
            if 'page' in locals():
                page.close()
            if 'browser' in locals():
                browser.close()
    
    return additional_data if data_complete else None

def calculate_scores(fund, fund_type):
    # 计算评级评分 (pjpf)
    pjpf = (fund['shanghai_rating']*0.8 + fund['citi_rating']*0.8 + fund['jian_rating']*0.8 + fund['morningstar_rating']*1.6) / 20 * 100
    
    # 计算涨幅评分 (zfpf) 2-5年占30%，1年占30%，6个月占20%，3个月占20%.
    # 2年、3年、5年数据平均,四舍五入,优秀30分，良好24分，否则为0分.
    # 1年数据,优秀30分，良好24分，否则为0分.
    # 6个月、3个月数据,优秀20分，良好16分，一般为12分，不佳为0分.
    zfpf = 0
    quartile_scores = {'优秀': 20, '良好': 16, '一般': 12, '不佳': 0}
    long_term_quartile_scores = {'优秀': 30, '良好': 24, '一般': 0, '不佳': 0}
    periods = ['近3月', '近6月', '近1年', '近2年', '近3年', '近5年']
    
    # 近3月、近6月涨幅评分
    for period in ['近3月', '近6月']:
        if period in fund:
            zfpf += quartile_scores.get(fund[period]['quartile'], 0)
    
    # 近1年涨幅评分
    if '近1年' in fund:
        zfpf += long_term_quartile_scores.get(fund['近1年']['quartile'], 0)
    
    # 近2年、近3年、近5年涨幅评分
    long_term_scores = []
    for period in ['近2年', '近3年', '近5年']:
        if (period in fund and 
            not pd.isna(fund[period]['quartile']) and 
            fund[period]['quartile'] not in ['N/A', '---', '']):  # 检查是否为空值或特殊字符
            long_term_scores.append(long_term_quartile_scores.get(fund[period]['quartile'], 0))
    
    if long_term_scores:
        zfpf += round(sum(long_term_scores) / len(long_term_scores))
    
    # 计算业绩评分 (yjpf)
    yjpf = 0
    if 'Scores' in fund and 'ScoresName' in fund:
        scores_dict = dict(zip(fund['ScoresName'], fund['Scores']))
        if fund_type in ["股票型", "混合型"]:
            yjpf = (scores_dict.get('选证能力', 0) * 0.1 +
                    scores_dict.get('收益率', 0) * 0.1 +
                    scores_dict.get('抗风险', 0) * 0.6 +
                    scores_dict.get('稳定性', 0) * 0.1 +
                    scores_dict.get('择时能力', 0) * 0.1)
        elif fund_type == "债券型":
            yjpf = (scores_dict.get('选证能力', 0) * 0.1 +
                    scores_dict.get('收益率', 0) * 0.1 +
                    scores_dict.get('抗风险', 0) * 0.6 +
                    scores_dict.get('稳定性', 0) * 0.1 +
                    scores_dict.get('管理规模', 0) * 0.1)
        elif fund_type == "指数型":
            yjpf = (scores_dict.get('选证能力', 0) +
                    scores_dict.get('收益率', 0) +
                    scores_dict.get('跟踪误差', 0) +
                    scores_dict.get('超额收益', 0) +
                    scores_dict.get('管理规模', 0)) * 0.2
    
    return pjpf, zfpf, yjpf

def filter_funds(funds, fund_type):
    filtered_funds = []
    for fund in funds:
        if fund_type == "指数型":
            total_rating = fund['citi_rating'] + fund['jian_rating'] + fund['morningstar_rating']
            if total_rating >= 13 or fund['morningstar_rating'] == 5:
                filtered_funds.append(fund)
        else:
            total_rating = fund['shanghai_rating'] + fund['citi_rating'] + fund['jian_rating'] + fund['morningstar_rating']
            if total_rating >= 16 or fund['morningstar_rating'] == 5:
                filtered_funds.append(fund)
    return filtered_funds

def process_value(value, field):
    """处理不同类型字段的值"""
    if pd.isna(value) or value == '' or value == '--' or value == 'N/A':
        return None
        
    try:
        # 处理资产规模
        if field == 'scale' and isinstance(value, str):
            if '亿' in value:
                return value
            return None
            
        # 处理评级和评分字段
        if field in ['shanghai_rating', 'merchant_rating', 'jian_rating', 
                    'morning_star_rating', 'rating_score', 'growth_score', 
                    'performance_score', 'total_score']:
            return float(value) if value else None
            
        # 处理增长率字段
        if '%' in str(value):
            return float(value.strip('%'))
            
        # 处理其他数值字段
        return float(value) if value else None
        
    except (ValueError, TypeError) as e:
        logging.warning(f"处理字段 {field} 的值 {value} 时出错: {str(e)}")
        return None

def write_fund_to_db(fund, fund_type, pjpf=None, zfpf=None, yjpf=None, zhpf=None):
    """将基金数据写入数据库"""
    try:
        # 根据基金类型选择对应的模型
        model_map = {
            "股票型": StockFund,
            "混合型": MixedFund,
            "债券型": BondFund,
            "指数型": IndexFund,
            "指数增强型": EnhancedFund
        }
        
        model = model_map.get(fund_type)
        if not model:
            logging.error(f"未知的基金类型: {fund_type}")
            return False
            
        # 构建基础数据字典
        fund_data = {
            'code': fund['code'],
            'name': fund['name']
        }
        
        # 添加评级和评分数据
        if all(x is not None for x in [pjpf, zfpf, yjpf, zhpf]):
            fund_data.update({
                'rating_score': pjpf,
                'growth_score': zfpf,
                'performance_score': yjpf,
                'total_score': zhpf
            })
            
        # 处理常规字段
        field_mappings = {
            'manager': 'manager',
            'company': 'company',
            'scale': 'scale',
            'shanghai_rating': 'shanghai_rating',
            'merchant_rating': 'citi_rating',
            'jian_rating': 'jian_rating',
            'morning_star_rating': 'morningstar_rating'
        }
        
        for db_field, fund_field in field_mappings.items():
            if fund_field in fund:
                fund_data[db_field] = process_value(fund[fund_field], db_field)
                
        # 处理业绩数据
        for period in ['近3月', '近6月', '近1年', '近2年', '近3年', '近5年']:
            if period in fund:
                period_map = {
                    '近3月': 'm3_growth',
                    '近6月': 'm6_growth',
                    '近1年': 'y1_growth',
                    '近2年': 'y2_growth',
                    '近3年': 'y3_growth',
                    '近5年': 'y5_growth'
                }
                if period in period_map:
                    fund_data[period_map[period]] = process_value(fund[period]['growth'], period_map[period])
                    
        # 添加其他特定字段
        if fund_type in ["股票型", "混合型"]:
            extra_fields = {
                'timing': fund.get('择时能力'),
                'risk_resistance': fund.get('抗风险'),
                'stability': fund.get('稳定性')
            }
        elif fund_type == "债券型":
            extra_fields = {
                'risk_resistance': fund.get('抗风险'),
                'stability': fund.get('稳定性'),
                'management_scale': fund.get('管理规模')
            }
        elif fund_type == "指数型":
            extra_fields = {
                'tracking_error': fund.get('跟踪误差'),
                'excess_return': fund.get('超额收益'),
                'management_scale': fund.get('管理规模')
            }
        else:  # 指数增强型
            extra_fields = {}
            
        fund_data.update({k: process_value(v, k) for k, v in extra_fields.items() if v is not None})
        
        # 检查是否存在该基金
        existing_fund = model.query.filter_by(code=fund['code']).first()
        if existing_fund:
            for key, value in fund_data.items():
                setattr(existing_fund, key, value)
        else:
            new_fund = model(**fund_data)
            db.session.add(new_fund)
            
        return True
        
    except Exception as e:
        logging.error(f"写入数据库失败: {str(e)}")
        db.session.rollback()
        return False

def process_funds(playwright, fund_type, url):
    """修改后的process_funds函数，改为写入数据库"""
    app = create_app()
    with app.app_context():
        funds = fetch_fund_data(playwright, url)
        filtered_funds = filter_funds(funds, fund_type)
        
        success_count = 0
        for fund in filtered_funds:
            retries = 0
            while retries < 3:
                try:
                    additional_data = fetch_additional_data(playwright, fund['code'])
                    if additional_data is None:
                        logging.warning(f"跳过基金 {fund['code']}")
                        break
                    
                    fund.update(additional_data)
                    pjpf, zfpf, yjpf = calculate_scores(fund, fund_type)
                    zhpf = pjpf * pjpfqz + yjpf * yjpfqz + zfpf * zfpfqz
                    
                    if write_fund_to_db(fund, fund_type, pjpf, zfpf, yjpf, zhpf):
                        success_count += 1
                        if success_count % 10 == 0:
                            db.session.commit()
                            logging.info(f"已成功处理 {success_count} 条记录")
                    
                    time.sleep(random.uniform(1, 3))
                    break
                    
                except Exception as e:
                    retries += 1
                    logging.error(f"处理基金 {fund['code']} 失败: {e}")
                    if retries == 3:
                        time.sleep(1800)
                        retries = 0
                        
        db.session.commit()
        logging.info(f"{fund_type}基金处理完成，共写入 {success_count} 条记录")

def format_percentage(value):
    """格式化百分比数据"""
    if value and value != '--':
        return f"{value}%"
    return value

def get_fund_data():
    """获取指数增强型基金数据"""
    url = "https://fund.eastmoney.com/data/rankhandler.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://fund.eastmoney.com/data/fundranking.html'
    }
    
    all_data = []
    page = 1
    
    try:
        while True:
            params = {
                'op': 'ph',
                'dt': 'kf',
                'ft': 'zs',
                'rs': '',
                'gs': '0',
                'sc': '1nzf',
                'st': 'desc',
                'sd': '2024-01-25',
                'ed': '2025-01-25',
                'qdii': '001|052',
                'tabSubtype': ',,001,052,,',
                'pi': str(page),
                'pn': '50',
                'dx': '1',
                'v': '0.3610194670329303'
            }
            
            # 继续使用原有的数据处理逻辑
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            pattern = r'var rankData = {datas:(\[.*?\]),allRecords:'
            match = re.search(pattern, response.text, re.DOTALL)
            if not match:
                break
                
            try:
                data_list = json.loads(match.group(1))
            except json.JSONDecodeError:
                break
                
            if not data_list:
                break
                
            processed_data = []
            for item in data_list:
                fields = item.split(',')
                if len(fields) >= 15:
                    percentage_fields = [fields[i] for i in [6,7,8,9,10,11,12,13,14,15]]
                    formatted_fields = [format_percentage(field) for field in percentage_fields]
                    
                    processed_data.append([
                        fields[0],
                        fields[1],
                        fields[4],
                        fields[5],
                        *formatted_fields
                    ])
            
            if not processed_data:
                break
                
            all_data.extend(processed_data)
            print(f"成功处理第{page}页，获取{len(processed_data)}条数据")
            page += 1
            
            # 为了避免频繁请求，添加适当延时
            time.sleep(random.uniform(1, 3))
        
        if not all_data:
            return None
            
        columns = ['基金代码', '基金简称', '单位净值', '累计净值',
                  '日增长率', '近1周', '近1月', '近3月', '近6月',
                  '近1年', '近2年', '近3年', '今年来', '成立来']
        
        return pd.DataFrame(all_data, columns=columns)
            
    except Exception as e:
        print(f"获取数据出错: {str(e)}")
        return None

def main():
    """修改后的主函数"""
    try:
        print("\n=== 开始获取基金数据 ===")
        with sync_playwright() as playwright:
            urls = {
                "混合型": "https://fund.eastmoney.com/data/fundrating.html#fthh",
                "股票型": "https://fund.eastmoney.com/data/fundrating.html#ftgp",
                "债券型": "https://fund.eastmoney.com/data/fundrating.html#ftzq",
                "指数型": "https://fund.eastmoney.com/data/fundrating.html#ftzs",
            }
            
            for fund_type, url in urls.items():
                print(f"\n处理{fund_type}基金...")
                process_funds(playwright, fund_type, url)
                
        # 处理指数增强型基金
        print("\n=== 开始获取指数增强型基金数据 ===")
        app = create_app()
        with app.app_context():
            fund_data = get_fund_data()
            if fund_data is not None and not fund_data.empty:
                success_count = 0
                for _, row in fund_data.iterrows():
                    fund = row.to_dict()
                    if write_fund_to_db(fund, "指数增强型"):
                        success_count += 1
                        if success_count % 50 == 0:
                            db.session.commit()
                            
                db.session.commit()
                print(f"指数增强型基金数据写入完成，共写入 {success_count} 条记录")
            else:
                print("未能获取到指数增强型基金数据或数据为空")

    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()