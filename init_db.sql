-- 检查用户是否已存在
SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'finance_user' AND host = 'localhost') INTO @user_exists;

-- 根据结果创建用户和授权
SET @create_user = IF(@user_exists = 0,
    'CREATE USER "finance_user"@"localhost" IDENTIFIED BY "123456"',
    'ALTER USER "finance_user"@"localhost" IDENTIFIED BY "123456"');
PREPARE stmt FROM @create_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS finance_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授权
GRANT ALL PRIVILEGES ON finance_data.* TO 'finance_user'@'localhost';
FLUSH PRIVILEGES;

USE finance_data;

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS stock_funds;
DROP TABLE IF EXISTS mixed_funds;
DROP TABLE IF EXISTS bond_funds;
DROP TABLE IF EXISTS index_funds;
DROP TABLE IF EXISTS enhanced_funds;

-- 创建股票型基金表 (根据股票型.csv的表头)
CREATE TABLE stock_funds (
    code VARCHAR(20) PRIMARY KEY,        -- 代码
    name VARCHAR(100),                   -- 简称
    manager VARCHAR(50),                 -- 基金经理
    company VARCHAR(100),                -- 基金公司
    scale VARCHAR(50),                   -- 资产规模
    rating_score FLOAT,                  -- 评级评分
    growth_score FLOAT,                  -- 涨幅评分
    performance_score FLOAT,             -- 业绩评分
    total_score FLOAT,                   -- 综合评分
    shanghai_rating VARCHAR(10),         -- 上海证券评级
    merchant_rating VARCHAR(10),         -- 招商证券评级
    jian_rating VARCHAR(10),            -- 济安金信评级
    morning_star_rating VARCHAR(10),     -- 晨星评级
    m3_growth VARCHAR(20),              -- 近3月涨幅
    m3_quartile VARCHAR(20),            -- 近3月四分位
    m6_growth VARCHAR(20),              -- 近6月涨幅
    m6_quartile VARCHAR(20),            -- 近6月四分位
    y1_growth VARCHAR(20),              -- 近1年涨幅
    y1_quartile VARCHAR(20),            -- 近1年四分位
    y2_growth VARCHAR(20),              -- 近2年涨幅
    y2_quartile VARCHAR(20),            -- 近2年四分位
    y3_growth VARCHAR(20),              -- 近3年涨幅
    y3_quartile VARCHAR(20),            -- 近3年四分位
    y5_growth VARCHAR(20),              -- 近5年涨幅
    y5_quartile VARCHAR(20),            -- 近5年四分位
    selection_ability FLOAT,            -- 选证能力
    return_rate FLOAT,                  -- 收益率
    risk_resistance FLOAT,              -- 抗风险
    stability FLOAT,                    -- 稳定性
    management_ability FLOAT            -- 择时能力
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建混合型基金表 (根据混合型.csv的表头)
CREATE TABLE mixed_funds (
    code VARCHAR(20) PRIMARY KEY,        -- 代码
    name VARCHAR(100),                   -- 简称
    manager VARCHAR(50),                 -- 基金经理
    company VARCHAR(100),                -- 基金公司 
    scale VARCHAR(50),                   -- 资产规模
    rating_score FLOAT,                  -- 评级评分
    growth_score FLOAT,                  -- 涨幅评分  
    performance_score FLOAT,             -- 业绩评分
    total_score FLOAT,                   -- 综合评分
    shanghai_rating VARCHAR(10),         -- 上海证券评级
    merchant_rating VARCHAR(10),         -- 招商证券评级
    jian_rating VARCHAR(10),            -- 济安金信评级 
    morning_star_rating VARCHAR(10),     -- 晨星评级
    m3_growth VARCHAR(20),              -- 近3月涨幅
    m3_quartile VARCHAR(20),            -- 近3月四分位
    m6_growth VARCHAR(20),              -- 近6月涨幅 
    m6_quartile VARCHAR(20),            -- 近6月四分位
    y1_growth VARCHAR(20),              -- 近1年涨幅
    y1_quartile VARCHAR(20),            -- 近1年四分位
    y2_growth VARCHAR(20),              -- 近2年涨幅
    y2_quartile VARCHAR(20),            -- 近2年四分位
    y3_growth VARCHAR(20),              -- 近3年涨幅
    y3_quartile VARCHAR(20),            -- 近3年四分位
    y5_growth VARCHAR(20),              -- 近5年涨幅
    y5_quartile VARCHAR(20),            -- 近5年四分位
    selection_ability FLOAT,            -- 选证能力
    return_rate FLOAT,                  -- 收益率
    risk_resistance FLOAT,              -- 抗风险
    stability FLOAT,                    -- 稳定性
    management_ability FLOAT            -- 择时能力
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建债券型基金表 (根据债券型.csv的表头)
CREATE TABLE IF NOT EXISTS bond_funds (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    manager VARCHAR(50),
    company VARCHAR(100),
    scale VARCHAR(50),
    rating_score FLOAT,
    growth_score FLOAT,
    performance_score FLOAT,
    total_score FLOAT,
    shanghai_rating VARCHAR(10),
    merchant_rating VARCHAR(10),
    jian_rating VARCHAR(10),
    morning_star_rating VARCHAR(10),
    m3_growth VARCHAR(20),
    m3_quartile VARCHAR(20),
    m6_growth VARCHAR(20),
    m6_quartile VARCHAR(20),
    y1_growth VARCHAR(20), 
    y1_quartile VARCHAR(20),
    y2_growth VARCHAR(20),
    y2_quartile VARCHAR(20),
    y3_growth VARCHAR(20),
    y3_quartile VARCHAR(20),
    y5_growth VARCHAR(20),
    y5_quartile VARCHAR(20),
    stock_selection FLOAT,
    return_rate FLOAT,
    risk_resistance FLOAT,
    stability FLOAT,
    management_scale VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建指数型基金表 (根据指数型.csv的表头)
CREATE TABLE IF NOT EXISTS index_funds (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    manager VARCHAR(50),
    company VARCHAR(100),
    scale VARCHAR(50),
    rating_score FLOAT,
    growth_score FLOAT,
    performance_score FLOAT,
    total_score FLOAT,
    shanghai_rating VARCHAR(10),
    merchant_rating VARCHAR(10),
    jian_rating VARCHAR(10),
    morning_star_rating VARCHAR(10),
    m3_growth VARCHAR(20),
    m3_quartile VARCHAR(20),
    m6_growth VARCHAR(20),
    m6_quartile VARCHAR(20),
    y1_growth VARCHAR(20),
    y1_quartile VARCHAR(20),
    y2_growth VARCHAR(20),
    y2_quartile VARCHAR(20),
    y3_growth VARCHAR(20),
    y3_quartile VARCHAR(20),
    y5_growth VARCHAR(20),
    y5_quartile VARCHAR(20),
    stock_selection FLOAT,
    return_rate FLOAT,
    tracking_error FLOAT,
    excess_return FLOAT,
    management_scale VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建指数增强型基金表 (根据指数增强型.csv的表头) 
CREATE TABLE IF NOT EXISTS enhanced_funds (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    unit_net_value FLOAT,
    accumulate_value FLOAT,
    day_growth_rate VARCHAR(20),
    week_growth VARCHAR(20),
    month_growth VARCHAR(20),
    m3_growth VARCHAR(20),
    m6_growth VARCHAR(20),
    y1_growth VARCHAR(20),
    y2_growth VARCHAR(20),
    y3_growth VARCHAR(20),
    ytd_growth VARCHAR(20),
    found_growth VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
