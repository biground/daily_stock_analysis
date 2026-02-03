# -*- coding: utf-8 -*-
"""
===================================
模拟盘 WebUI 页面模板
===================================

提供模拟盘相关的 HTML 页面：
1. 仪表盘页面
2. 交易记录页面
3. AI 准确度分析页面
"""

PORTFOLIO_CSS = """
:root {
    --primary: #3b82f6;
    --primary-dark: #2563eb;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --bg: #0f172a;
    --bg-card: #1e293b;
    --bg-card-hover: #334155;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --border: #334155;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
}

.navbar {
    background: var(--bg-card);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
}

.navbar h1 {
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-links {
    display: flex;
    gap: 1rem;
}

.nav-links a {
    color: var(--text-muted);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    transition: all 0.2s;
}

.nav-links a:hover, .nav-links a.active {
    background: var(--primary);
    color: white;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.grid {
    display: grid;
    gap: 1.5rem;
}

.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }

@media (max-width: 1200px) { .grid-4 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .grid-4, .grid-3, .grid-2 { grid-template-columns: 1fr; } }

.card {
    background: var(--bg-card);
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid var(--border);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 0.875rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.stat-change {
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.stat-change.positive { color: var(--success); }
.stat-change.negative { color: var(--danger); }

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

th {
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.875rem;
}

tr:hover {
    background: var(--bg-card-hover);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
.badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
.badge-warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
.badge-primary { background: rgba(59, 130, 246, 0.2); color: var(--primary); }

.chart-container {
    height: 300px;
    position: relative;
}

.progress-bar {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
}

.accuracy-ring {
    width: 150px;
    height: 150px;
    margin: 0 auto;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-muted);
}

.refresh-btn {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
}

.refresh-btn:hover {
    background: var(--primary-dark);
}
"""

PORTFOLIO_JS = """
// 格式化数字
function formatNumber(num, decimals = 2) {
    return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

// 格式化货币
function formatCurrency(num) {
    return '¥' + formatNumber(num);
}

// 格式化百分比
function formatPercent(num) {
    const sign = num >= 0 ? '+' : '';
    return sign + formatNumber(num) + '%';
}

// 获取颜色类
function getColorClass(value) {
    return value >= 0 ? 'positive' : 'negative';
}

// 刷新数据
async function refreshData() {
    try {
        const response = await fetch('/api/portfolio/dashboard');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('刷新失败:', error);
    }
}

// 更新仪表盘
function updateDashboard(data) {
    const summary = data.summary;
    
    // 更新统计卡片
    document.getElementById('total-assets').textContent = formatCurrency(summary.total_assets);
    document.getElementById('daily-pnl').textContent = formatCurrency(summary.daily_profit_loss);
    document.getElementById('total-return').textContent = formatPercent(summary.total_return_pct);
    document.getElementById('position-ratio').textContent = formatNumber(summary.position_ratio) + '%';
    
    // 更新持仓表格
    updatePositionsTable(data.positions);
    
    // 更新收益图表
    updateReturnsChart(data.daily_returns);
}

// 更新持仓表格
function updatePositionsTable(positions) {
    const tbody = document.getElementById('positions-tbody');
    if (!tbody) return;
    
    if (positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">暂无持仓</td></tr>';
        return;
    }
    
    tbody.innerHTML = positions.map(pos => `
        <tr>
            <td><strong>${pos.name}</strong><br><span style="color: var(--text-muted)">${pos.code}</span></td>
            <td>${pos.shares}</td>
            <td>¥${formatNumber(pos.cost_price, 3)}</td>
            <td>¥${formatNumber(pos.current_price, 3)}</td>
            <td>¥${formatNumber(pos.market_value)}</td>
            <td class="${getColorClass(pos.profit_loss)}">${formatCurrency(pos.profit_loss)}</td>
            <td><span class="badge ${pos.profit_loss >= 0 ? 'badge-success' : 'badge-danger'}">${formatPercent(pos.profit_loss_pct)}</span></td>
        </tr>
    `).join('');
}

// 简单的柱状图
function updateReturnsChart(returns) {
    const container = document.getElementById('returns-chart');
    if (!container || returns.length === 0) return;
    
    const maxAbs = Math.max(...returns.map(r => Math.abs(r.daily_profit_loss)), 1);
    
    container.innerHTML = `
        <div style="display: flex; align-items: flex-end; justify-content: space-around; height: 100%; padding: 1rem;">
            ${returns.map(r => {
                const height = Math.abs(r.daily_profit_loss) / maxAbs * 80;
                const color = r.daily_profit_loss >= 0 ? 'var(--success)' : 'var(--danger)';
                return `
                    <div style="text-align: center; flex: 1;">
                        <div style="height: ${height}%; min-height: 4px; background: ${color}; border-radius: 4px 4px 0 0; margin: 0 4px;"></div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem;">${r.date.slice(5)}</div>
                        <div style="font-size: 0.75rem; color: ${color};">${formatCurrency(r.daily_profit_loss)}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// 页面加载完成后刷新数据
document.addEventListener('DOMContentLoaded', refreshData);

// 每60秒自动刷新
setInterval(refreshData, 60000);
"""


def render_portfolio_dashboard(data: dict) -> str:
    """渲染仪表盘页面"""
    summary = data.get("summary", {})
    positions = data.get("positions", [])
    daily_returns = data.get("daily_returns", [])
    trade_stats = data.get("trade_stats", {})
    risk_params = data.get("risk_params", {})
    
    # 持仓表格
    positions_rows = ""
    if positions:
        for pos in positions:
            pnl_class = "positive" if pos["profit_loss"] >= 0 else "negative"
            badge_class = "badge-success" if pos["profit_loss"] >= 0 else "badge-danger"
            positions_rows += f"""
            <tr>
                <td><strong>{pos['name']}</strong><br><span style="color: var(--text-muted)">{pos['code']}</span></td>
                <td>{pos['shares']:,}</td>
                <td>¥{pos['cost_price']:.3f}</td>
                <td>¥{pos['current_price']:.3f}</td>
                <td>¥{pos['market_value']:,.2f}</td>
                <td class="{pnl_class}">¥{pos['profit_loss']:+,.2f}</td>
                <td><span class="badge {badge_class}">{pos['profit_loss_pct']:+.2f}%</span></td>
            </tr>
            """
    else:
        positions_rows = '<tr><td colspan="7" class="empty-state">暂无持仓</td></tr>'
    
    # 收益图表
    chart_bars = ""
    if daily_returns:
        max_abs = max(abs(r["daily_profit_loss"]) for r in daily_returns) or 1
        for r in daily_returns:
            height = abs(r["daily_profit_loss"]) / max_abs * 80
            color = "var(--success)" if r["daily_profit_loss"] >= 0 else "var(--danger)"
            chart_bars += f"""
            <div style="text-align: center; flex: 1;">
                <div style="height: {height}%; min-height: 4px; background: {color}; border-radius: 4px 4px 0 0; margin: 0 4px;"></div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem;">{r['date'][5:]}</div>
                <div style="font-size: 0.75rem; color: {color};">¥{r['daily_profit_loss']:+,.0f}</div>
            </div>
            """
    
    daily_pnl_class = "positive" if summary.get("daily_profit_loss", 0) >= 0 else "negative"
    total_return_class = "positive" if summary.get("total_return_pct", 0) >= 0 else "negative"
    
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模拟盘仪表盘</title>
    <style>{PORTFOLIO_CSS}</style>
</head>
<body>
    <nav class="navbar">
        <h1>📊 模拟盘管理系统</h1>
        <div class="nav-links">
            <a href="/portfolio" class="active">仪表盘</a>
            <a href="/portfolio/trades">交易记录</a>
            <a href="/portfolio/accuracy">AI准确度</a>
            <a href="/">返回主页</a>
        </div>
    </nav>
    
    <div class="container">
        <!-- 统计卡片 -->
        <div class="grid grid-4" style="margin-bottom: 1.5rem;">
            <div class="card">
                <div class="card-title">💰 总资产</div>
                <div class="stat-value" id="total-assets">¥{summary.get('total_assets', 0):,.2f}</div>
                <div class="stat-change">初始资金: ¥{summary.get('initial_capital', 0):,.2f}</div>
            </div>
            <div class="card">
                <div class="card-title">📈 今日盈亏</div>
                <div class="stat-value {daily_pnl_class}" id="daily-pnl">¥{summary.get('daily_profit_loss', 0):+,.2f}</div>
                <div class="stat-change {daily_pnl_class}">{summary.get('daily_return_pct', 0):+.2f}%</div>
            </div>
            <div class="card">
                <div class="card-title">📊 累计收益</div>
                <div class="stat-value {total_return_class}" id="total-return">{summary.get('total_return_pct', 0):+.2f}%</div>
                <div class="stat-change {total_return_class}">¥{summary.get('total_profit_loss', 0):+,.2f}</div>
            </div>
            <div class="card">
                <div class="card-title">⚖️ 仓位比例</div>
                <div class="stat-value" id="position-ratio">{summary.get('position_ratio', 0):.1f}%</div>
                <div class="progress-bar" style="margin-top: 0.5rem;">
                    <div class="progress-bar-fill" style="width: {min(summary.get('position_ratio', 0), 100)}%; background: var(--primary);"></div>
                </div>
            </div>
        </div>
        
        <div class="grid grid-2">
            <!-- 持仓明细 -->
            <div class="card">
                <div class="card-header">
                    <h3 class="section-title">📋 持仓明细</h3>
                    <span class="badge badge-primary">{summary.get('position_count', 0)} 只</span>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>股票</th>
                                <th>持仓</th>
                                <th>成本</th>
                                <th>现价</th>
                                <th>市值</th>
                                <th>盈亏</th>
                                <th>收益率</th>
                            </tr>
                        </thead>
                        <tbody id="positions-tbody">
                            {positions_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 收益趋势 -->
            <div class="card">
                <div class="card-header">
                    <h3 class="section-title">📈 收益趋势</h3>
                    <span class="badge badge-primary">最近7天</span>
                </div>
                <div class="chart-container" id="returns-chart" style="display: flex; align-items: flex-end; justify-content: space-around;">
                    {chart_bars if chart_bars else '<div class="empty-state">暂无数据</div>'}
                </div>
            </div>
        </div>
        
        <!-- 风控参数 -->
        <div class="card" style="margin-top: 1.5rem;">
            <h3 class="section-title">⚙️ 风控参数</h3>
            <div class="grid grid-4">
                <div>
                    <div class="card-title">止损线</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--danger);">-{risk_params.get('stop_loss_pct', 8)}%</div>
                </div>
                <div>
                    <div class="card-title">止盈线</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--success);">+{risk_params.get('take_profit_pct', 20)}%</div>
                </div>
                <div>
                    <div class="card-title">单股最大仓位</div>
                    <div style="font-size: 1.5rem; font-weight: 600;">{risk_params.get('max_single_position_pct', 30)}%</div>
                </div>
                <div>
                    <div class="card-title">最大总仓位</div>
                    <div style="font-size: 1.5rem; font-weight: 600;">{risk_params.get('max_total_position_pct', 80)}%</div>
                </div>
            </div>
        </div>
        
        <!-- 交易统计 -->
        <div class="card" style="margin-top: 1.5rem;">
            <h3 class="section-title">📝 交易统计</h3>
            <div class="grid grid-3">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700;">{trade_stats.get('total', 0)}</div>
                    <div class="card-title">总交易次数</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--success);">{trade_stats.get('buy', 0)}</div>
                    <div class="card-title">买入/加仓</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">{trade_stats.get('sell', 0)}</div>
                    <div class="card-title">卖出/减仓</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>{PORTFOLIO_JS}</script>
</body>
</html>
"""


def render_trades_page(trades: list) -> str:
    """渲染交易记录页面"""
    trades_rows = ""
    if trades:
        for t in trades:
            action_map = {"buy": ("🟢", "买入"), "sell": ("🔴", "卖出"), "add": ("🟢", "加仓"), "reduce": ("🔴", "减仓")}
            emoji, action_text = action_map.get(t.get("action", ""), ("⚪", t.get("action", "")))
            badge_class = "badge-success" if t.get("action") in ["buy", "add"] else "badge-danger"
            
            trades_rows += f"""
            <tr>
                <td>{t.get('date', '')}<br><span style="color: var(--text-muted)">{t.get('time', '')}</span></td>
                <td><span class="badge {badge_class}">{emoji} {action_text}</span></td>
                <td><strong>{t.get('name', '')}</strong><br><span style="color: var(--text-muted)">{t.get('code', '')}</span></td>
                <td>{t.get('shares', 0):,}</td>
                <td>¥{t.get('price', 0):.3f}</td>
                <td>¥{t.get('amount', 0):,.2f}</td>
                <td>¥{t.get('commission', 0):.2f}</td>
                <td>{t.get('reason', '') or '-'}</td>
            </tr>
            """
    else:
        trades_rows = '<tr><td colspan="8" class="empty-state">暂无交易记录</td></tr>'
    
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易记录</title>
    <style>{PORTFOLIO_CSS}</style>
</head>
<body>
    <nav class="navbar">
        <h1>📊 模拟盘管理系统</h1>
        <div class="nav-links">
            <a href="/portfolio">仪表盘</a>
            <a href="/portfolio/trades" class="active">交易记录</a>
            <a href="/portfolio/accuracy">AI准确度</a>
            <a href="/">返回主页</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h3 class="section-title">📝 交易记录</h3>
                <span class="badge badge-primary">{len(trades)} 条</span>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>操作</th>
                            <th>股票</th>
                            <th>数量</th>
                            <th>价格</th>
                            <th>金额</th>
                            <th>佣金</th>
                            <th>理由</th>
                        </tr>
                    </thead>
                    <tbody>
                        {trades_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""


def render_accuracy_page(data: dict) -> str:
    """渲染 AI 准确度分析页面"""
    summary = data.get("summary", {})
    records = data.get("records", [])
    monthly = data.get("monthly_accuracy", [])
    
    accuracy_rate = summary.get("accuracy_rate", 0)
    accuracy_color = "var(--success)" if accuracy_rate >= 50 else "var(--danger)"
    
    # 月度统计
    monthly_rows = ""
    for m in monthly:
        rate = m.get("accuracy", 0)
        badge_class = "badge-success" if rate >= 50 else "badge-danger"
        monthly_rows += f"""
        <tr>
            <td>{m.get('month', '')}</td>
            <td>{m.get('total', 0)}</td>
            <td>{m.get('correct', 0)}</td>
            <td><span class="badge {badge_class}">{rate:.1f}%</span></td>
        </tr>
        """
    
    # 详细记录
    records_rows = ""
    for r in records[-20:]:
        is_correct = r.get("is_correct", False)
        badge_class = "badge-success" if is_correct else "badge-danger"
        result_text = "✅ 正确" if is_correct else "❌ 错误"
        return_class = "positive" if r.get("next_day_return", 0) >= 0 else "negative"
        
        records_rows += f"""
        <tr>
            <td>{r.get('date', '')}</td>
            <td>{r.get('prediction', '')}</td>
            <td class="{return_class}">{r.get('next_day_return', 0):+.2f}%</td>
            <td><span class="badge {badge_class}">{result_text}</span></td>
        </tr>
        """
    
    if not records_rows:
        records_rows = '<tr><td colspan="4" class="empty-state">暂无预测记录，请先运行几天分析</td></tr>'
    
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 准确度分析</title>
    <style>{PORTFOLIO_CSS}</style>
</head>
<body>
    <nav class="navbar">
        <h1>📊 模拟盘管理系统</h1>
        <div class="nav-links">
            <a href="/portfolio">仪表盘</a>
            <a href="/portfolio/trades">交易记录</a>
            <a href="/portfolio/accuracy" class="active">AI准确度</a>
            <a href="/">返回主页</a>
        </div>
    </nav>
    
    <div class="container">
        <!-- 准确度概览 -->
        <div class="grid grid-3" style="margin-bottom: 1.5rem;">
            <div class="card" style="text-align: center;">
                <div class="card-title">🎯 总体准确率</div>
                <div style="font-size: 3rem; font-weight: 700; color: {accuracy_color};">{accuracy_rate:.1f}%</div>
                <div class="progress-bar" style="margin-top: 1rem;">
                    <div class="progress-bar-fill" style="width: {accuracy_rate}%; background: {accuracy_color};"></div>
                </div>
            </div>
            <div class="card" style="text-align: center;">
                <div class="card-title">📊 预测次数</div>
                <div style="font-size: 3rem; font-weight: 700;">{summary.get('total_predictions', 0)}</div>
                <div style="color: var(--text-muted);">总预测</div>
            </div>
            <div class="card" style="text-align: center;">
                <div class="card-title">✅ 正确次数</div>
                <div style="font-size: 3rem; font-weight: 700; color: var(--success);">{summary.get('correct_predictions', 0)}</div>
                <div style="color: var(--text-muted);">预测正确</div>
            </div>
        </div>
        
        <div class="grid grid-2">
            <!-- 月度统计 -->
            <div class="card">
                <h3 class="section-title">📅 月度统计</h3>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>月份</th>
                                <th>预测次数</th>
                                <th>正确次数</th>
                                <th>准确率</th>
                            </tr>
                        </thead>
                        <tbody>
                            {monthly_rows if monthly_rows else '<tr><td colspan="4" class="empty-state">暂无数据</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 详细记录 -->
            <div class="card">
                <h3 class="section-title">📝 预测详情（最近20条）</h3>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>日期</th>
                                <th>预测</th>
                                <th>次日涨跌</th>
                                <th>结果</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- 说明 -->
        <div class="card" style="margin-top: 1.5rem;">
            <h3 class="section-title">ℹ️ 准确度计算说明</h3>
            <ul style="color: var(--text-muted); line-height: 1.8;">
                <li><strong>预测逻辑</strong>：如果当日有持仓，视为 AI 建议"持有"</li>
                <li><strong>正确判定</strong>：持有时，第二天上涨则判定为正确</li>
                <li><strong>数据来源</strong>：基于每日账户快照计算</li>
                <li><strong>注意</strong>：准确度仅供参考，不代表实际投资收益</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
