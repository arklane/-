let allFunds = {
    '股票型': [],
    '混合型': [],
    '债券型': [],
    '指数型': []
};
let indexEnhancedFunds = [];

// 修改加载JSON数据函数
async function loadFundData() {
    try {
        // 首先加载主要基金数据
        const response = await fetch('/api/funds');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // 初始化基金数据
        allFunds = {
            '股票型': data.stock || [],
            '混合型': data.mixed || [],
            '债券型': data.bond || [],
            '指数型': data.index || []
        };

        // 检查数据是否为空
        const hasData = Object.values(allFunds).some(arr => arr.length > 0);
        if (!hasData) {
            throw new Error('没有找到任何基金数据');
        }

        // 更新页面显示
        showHotFunds();
        createFundTable();

        // 尝试加载指数增强型基金数据
        try {
            const enhancedResponse = await fetch('/api/enhanced-funds');
            if (!enhancedResponse.ok) {
                throw new Error('服务器响应错误');
            }
            const enhancedData = await enhancedResponse.json();
            
            if (enhancedData.error) {
                console.warn('指数增强型基金数据加载警告:', enhancedData.error);
                indexEnhancedFunds = [];
            } else {
                indexEnhancedFunds = enhancedData.funds || [];
            }
        } catch (enhancedError) {
            console.warn('指数增强型基金数据加载失败:', enhancedError);
            indexEnhancedFunds = [];
        }

        createIndexEnhancedTable();
        await loadParams();
        
        console.log('数据加载成功');
    } catch (error) {
        console.error('数据加载失败:', error);
        showError(error.message);
    }
}

// 修改显示热门基金函数
function showHotFunds() {
    const container = document.getElementById('hot-funds-list');
    container.innerHTML = '';

    Object.entries(allFunds).forEach(([type, funds]) => {
        if (!funds || !Array.isArray(funds)) return;

        const topFunds = funds
            .filter(fund => fund && typeof fund.total_score === 'number')
            .sort((a, b) => (b.total_score || 0) - (a.total_score || 0))
            .slice(0, 5);

        if (topFunds.length === 0) return;

        const typeSection = document.createElement('div');
        typeSection.innerHTML = `<h3>${type}基金 TOP 5</h3>`;

        topFunds.forEach(fund => {
            if (!fund) return;
            
            // 预处理函数
            const formatGrowth = (value) => value ? value + '%' : '暂无数据';
            const formatScore = (value) => value ? Number(value).toFixed(1) : '暂无数据';
            
            // 基础信息部分
            let baseInfo = `
                <div class="fund-info">
                    <h4>基本信息</h4>
                    <p><strong>基金代码:</strong> ${String(fund.code).padStart(6, '0')}</p>
                    <p><strong>基金名称:</strong> ${fund.name || '暂无数据'}</p>
                    <p><strong>基金经理:</strong> ${fund.manager || '暂无数据'}</p>
                    <p><strong>基金公司:</strong> ${fund.company || '暂无数据'}</p>
                    <p><strong>资产规模:</strong> ${fund.scale || '暂无数据'}</p>
                </div>

                <div class="rating-info">
                    <h4>评级信息</h4>
                    <p><strong>评级评分:</strong> ${formatScore(fund.rating_score)}</p>
                    <p><strong>涨幅评分:</strong> ${formatScore(fund.growth_score)}</p>
                    <p><strong>业绩评分:</strong> ${formatScore(fund.performance_score)}</p>
                    <p><strong>综合评分:</strong> ${formatScore(fund.total_score)}</p>
                </div>

                <div class="growth-info">
                    <h4>涨幅数据</h4>
                    <p><strong>近3月涨幅:</strong> ${formatGrowth(fund.m3_growth)}</p>
                    <p><strong>近6月涨幅:</strong> ${formatGrowth(fund.m6_growth)}</p>
                    <p><strong>近1年涨幅:</strong> ${formatGrowth(fund.y1_growth)}</p>
                    <p><strong>近2年涨幅:</strong> ${formatGrowth(fund.y2_growth)}</p>
                    <p><strong>近3年涨幅:</strong> ${formatGrowth(fund.y3_growth)}</p>
                    <p><strong>近5年涨幅:</strong> ${formatGrowth(fund.y5_growth)}</p>
                </div>`;

            // 根据基金类型添加特定信息
            let specificInfo = '';
            if (type === '指数型') {
                specificInfo = `
                    <div class="specific-info">
                        <h4>指数特性</h4>
                        <p><strong>选证能力:</strong> ${formatScore(fund.stock_selection)}</p>
                        <p><strong>收益率:</strong> ${formatScore(fund.return_rate)}</p>
                        <p><strong>跟踪误差:</strong> ${formatScore(fund.tracking_error)}</p>
                        <p><strong>超额收益:</strong> ${formatScore(fund.excess_return)}</p>
                        <p><strong>管理规模:</strong> ${fund.management_scale || '暂无数据'}</p>
                    </div>`;
            } else if (type === '债券型') {
                specificInfo = `
                    <div class="specific-info">
                        <h4>债券特性</h4>
                        <p><strong>选证能力:</strong> ${formatScore(fund.selection_ability)}</p>
                        <p><strong>收益率:</strong> ${formatScore(fund.return_rate)}</p>
                        <p><strong>抗风险:</strong> ${formatScore(fund.risk_resistance)}</p>
                        <p><strong>稳定性:</strong> ${formatScore(fund.stability)}</p>
                        <p><strong>管理规模:</strong> ${formatScore(fund.management_scale)}</p>
                    </div>`;
            } else if (type === '股票型' || type === '混合型') {
                specificInfo = `
                    <div class="specific-info">
                        <h4>投资能力</h4>
                        <p><strong>选证能力:</strong> ${formatScore(fund.selection_ability)}</p>
                        <p><strong>收益率:</strong> ${formatScore(fund.return_rate)}</p>
                        <p><strong>抗风险:</strong> ${formatScore(fund.risk_resistance)}</p>
                        <p><strong>稳定性:</strong> ${formatScore(fund.stability)}</p>
                        <p><strong>择时能力:</strong> ${formatScore(fund.timing)}</p>
                    </div>`;
            }

            const fundCard = document.createElement('div');
            fundCard.className = 'fund-card';
            fundCard.innerHTML = baseInfo + specificInfo;
            
            typeSection.appendChild(fundCard);
        });

        container.appendChild(typeSection);
    });
}

// 修改创建基金表格函数
function createFundTable() {
    const selectedType = document.getElementById('fund-type').value;
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const assetThreshold = parseFloat(document.getElementById('asset-threshold').value);
    const enableFilter = document.getElementById('enable-filter').checked;
    
    let displayFunds = [];
    if (selectedType === 'all') {
        Object.values(allFunds).forEach(funds => displayFunds.push(...funds));
    } else {
        displayFunds = allFunds[selectedType] || [];
    }

    // 添加综合评分排序
    displayFunds.sort((a, b) => (b.total_score || 0) - (a.total_score || 0));

    // 修改搜索和过滤逻辑
    displayFunds = displayFunds.filter(fund => {
        if (!fund || !fund.code || !fund.name) {
            return false;
        }
        
        const matchesSearch = fund.code.toString().toLowerCase().includes(searchTerm) || 
                            fund.name.toString().toLowerCase().includes(searchTerm);
        
        if (!enableFilter || isNaN(assetThreshold)) {
            return matchesSearch;
        }

        const assetSize = parseFloat(fund.scale || 0);
        return matchesSearch && !isNaN(assetSize) && assetSize > assetThreshold;
    });

    // 渲染表格
    const container = document.getElementById('fund-table');
    if (displayFunds.length === 0) {
        container.innerHTML = '<p>没有找到匹配的基金</p>';
        return;
    }

    // 使用固定的列名和显示标签
    const columns = [
        'code', 'name', 'manager', 'company', 'scale', 
        'rating_score', 'growth_score', 'performance_score', 'total_score',
        'shanghai_rating', 'merchant_rating', 'jian_rating', 'morning_star_rating',
        'm3_growth', 'm6_growth', 'y1_growth', 'y3_growth', 'y5_growth'
    ];
    
    const columnLabels = {
        code: '基金代码',
        name: '基金名称',
        manager: '基金经理',
        company: '基金公司',
        scale: '规模(亿元)',
        rating_score: '评级评分',
        growth_score: '涨幅评分',
        performance_score: '业绩评分',
        total_score: '综合评分',
        shanghai_rating: '上海证券评级',
        merchant_rating: '招商证券评级',
        jian_rating: '济安金信评级',
        morning_star_rating: '晨星评级',
        'm3_growth': '近3月涨幅(%)',
        'm6_growth': '近6月涨幅(%)',
        'y1_growth': '近1年涨幅(%)',
        'y3_growth': '近3年涨幅(%)',
        'y5_growth': '近5年涨幅(%)'
    };

    const table = `
        <table>
            <thead>
                <tr>${columns.map(col => `<th>${columnLabels[col]}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${displayFunds.map(fund => `
                    <tr>${columns.map(col => {
                        let value = fund[col];
                        // 特殊处理基金代码，确保显示前导零
                        if (col === 'code') {
                            value = String(value).padStart(6, '0');
                        }
                        // 处理百分比字段（除了涨幅评分）
                        else if (col.includes('growth') && !col.includes('growth_score')) {
                            value = value ? value + '%' : '';
                        }
                        // 处理评分字段
                        else if (col.includes('score')) {
                            value = value ? Number(value).toFixed(2) : '';
                        }
                        return `<td>${value || ''}</td>`;
                    }).join('')}</tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

// 计算各表格权重总和
function calculateWeightSum(tableId) {
    const inputs = document.querySelectorAll(`#${tableId} .weight-input`);
    let sum = 0;
    inputs.forEach(input => {
        sum += parseFloat(input.value) || 0;
    });
    return sum;
}

// 修改指数增强型基金表格创建函数
function createIndexEnhancedTable(searchTerm = '') {
    const container = document.getElementById('index-fund-table');
    
    if (!Array.isArray(indexEnhancedFunds) || indexEnhancedFunds.length === 0) {
        container.innerHTML = '<p>暂无指数增强型基金数据</p>';
        return;
    }
    
    let displayFunds = [...indexEnhancedFunds];
    
    // 搜索过滤
    if (searchTerm) {
        searchTerm = searchTerm.toLowerCase();
        displayFunds = displayFunds.filter(fund => {
            return fund.code?.toString().toLowerCase().includes(searchTerm) ||
                   fund.name?.toString().toLowerCase().includes(searchTerm);
        });
    }
    
    // 修改排序逻辑：按近1年涨幅排序
    displayFunds.sort((a, b) => {
        let aValue = a.y1_growth ? parseFloat(a.y1_growth.replace('%', '')) : -Infinity;
        let bValue = b.y1_growth ? parseFloat(b.y1_growth.replace('%', '')) : -Infinity;
        return bValue - aValue;
    });
    
    if (displayFunds.length === 0) {
        container.innerHTML = '<p>没有找到匹配的基金</p>';
        return;
    }

    const columns = [
        'code', 'name', 'unit_net_value', 'accumulate_value',
        'daily_growth',  // 修改这里，使用正确的属性名称
        'week_growth', 'month_growth',
        'm3_growth', 'm6_growth', 'y1_growth', 'y2_growth',
        'y3_growth', 'ytd_growth', 'since_launch'
    ];
    
    const columnLabels = {
        code: '基金代码',
        name: '基金名称',
        unit_net_value: '单位净值',
        accumulate_value: '累计净值',
        daily_growth: '日增长率(%)',  // 修改这里，使用正确的属性名称
        week_growth: '周涨幅(%)',
        month_growth: '月涨幅(%)',
        m3_growth: '近3月涨幅(%)',
        m6_growth: '近6月涨幅(%)',
        y1_growth: '近1年涨幅(%)',
        y2_growth: '近2年涨幅(%)',
        y3_growth: '近3年涨幅(%)',
        ytd_growth: '今年以来(%)',
        since_launch: '成立以来(%)'
    };

    const table = `
        <table>
            <thead>
                <tr>${columns.map(col => `<th>${columnLabels[col]}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${displayFunds.map(fund => `
                    <tr>${columns.map(col => {
                        let value = fund[col];
                        // 特殊处理基金代码，确保显示前导零
                        if (col === 'code') {
                            value = String(value).padStart(6, '0');
                        }
                        // 处理百分比字段，移除已有的百分号再添加
                        else if (col.includes('growth')) {
                            if (value) {
                                // 移除字符串中的所有百分号，然后添加一个新的百分号
                                value = value.replace(/%/g, '') + '%';
                            } else {
                                value = '';
                            }
                        }
                        // 处理净值字段，保留4位小数
                        else if (col === 'unit_net_value' || col === 'accumulate_value') {
                            value = value ? Number(value).toFixed(4) : '';
                        }
                        return `<td>${value || ''}</td>`;
                    }).join('')}</tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

// 更新表格权重总和显示
function updateWeightSum(tableId) {
    const sum = calculateWeightSum(tableId);
    const sumElement = document.getElementById(`${tableId}-sum`);
    if (sumElement) {
        sumElement.textContent = sum.toFixed(1);
    }

    validateWeights();
}

// 验证所有表格权重
function validateWeights() {
    const tables = [
        'total-score-table',
        'rating-score-table',
        'growth-score-table',
        'stock-perf-table',
        'bond-perf-table',
        'index-perf-table'
    ];

    const errorElement = document.getElementById('weight-error');
    const updateButton = document.getElementById('update-params');
    let hasError = false;

    tables.forEach(tableId => {
        const sum = calculateWeightSum(tableId);
        if (Math.abs(sum - 1) > 0.001) {
            hasError = true;
        }
    });

    errorElement.style.display = hasError ? 'block' : 'none';
    updateButton.disabled = hasError;
}

// 加载参数
async function loadParams() {
    try {
        const response = await fetch('config.json');
        const config = await response.json();
        
        // 根据配置文件设置各表格的默认值
        Object.entries(config).forEach(([key, value]) => {
            const input = document.getElementById(key);
            if (input) {
                input.value = value;
            }
        });

        // 初始化所有表格的权重总和
        const tables = [
            'total-score-table',
            'rating-score-table',
            'growth-score-table',
            'stock-perf-table',
            'bond-perf-table',
            'index-perf-table'
        ];
        
        tables.forEach(tableId => {
            updateWeightSum(tableId);
        });
    } catch (error) {
        console.error('加载参数失败:', error);
    }
}

// 修改更新参数函数
async function updateParams() {
    const weightData = {
        总评分: getTableWeights('total-score-table'),
        评级评分: getTableWeights('rating-score-table'),
        涨幅评分: getTableWeights('growth-score-table'),
        股票型业绩评分: getTableWeights('stock-perf-table'),
        债券型业绩评分: getTableWeights('bond-perf-table'),
        指数型业绩评分: getTableWeights('index-perf-table')
    };

    try {
        const response = await fetch('/api/update-params', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(weightData)
        });

        const result = await response.json();
        
        if (result.success) {
            alert('参数更新成功');
            await loadFundData(); // 重新加载数据
        } else {
            alert(result.error || '参数更新失败');
        }
    } catch (error) {
        console.error('更新参数失败:', error);
        alert('系统错误，请稍后重试');
    }
}

// 获取表格权重数据
function getTableWeights(tableId) {
    const weights = {};
    const inputs = document.querySelectorAll(`#${tableId} .weight-input`);
    inputs.forEach(input => {
        const label = input.closest('tr').querySelector('td:first-child').textContent;
        weights[label] = parseFloat(input.value) || 0;
    });
    return weights;
}

// 初始化事件监听
document.addEventListener('DOMContentLoaded', function() {
    // 基金搜索相关
    document.getElementById('search-input').addEventListener('input', createFundTable);
    document.getElementById('fund-type').addEventListener('change', createFundTable);
    document.getElementById('asset-threshold').addEventListener('input', createFundTable);
    document.getElementById('enable-filter').addEventListener('change', createFundTable);
    // 指数增强型基金搜索
    const indexSearchInput = document.getElementById('index-search-input');
    if (indexSearchInput) {
        indexSearchInput.addEventListener('input', function() {
            createIndexEnhancedTable(this.value);
        });
    }
    // 权重计算相关
    document.querySelectorAll('.weight-input').forEach(input => {
        input.addEventListener('input', function() {
            const tableId = this.closest('table').id;
            updateWeightSum(tableId);
        });
    });
});

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
    
    // 如果切换到指数增强型基金页面，重新加载表格
    if (sectionId === 'index-enhanced') {
        createIndexEnhancedTable();
    }
}

// 添加错误显示函数
function showError(message) {
    const errorMessage = document.createElement('div');
    errorMessage.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #fff;
        padding: 20px;
        border: 1px solid #ddd;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        z-index: 1000;
    `;
    errorMessage.innerHTML = `
        <h3>数据加载失败</h3>
        <p>原因: ${message}</p>
        <button onclick="location.reload()">重试</button>
    `;
    document.body.appendChild(errorMessage);
}

// 页面加载时初始化
window.onload = loadFundData;