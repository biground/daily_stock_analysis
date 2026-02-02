# -*- coding: utf-8 -*-
"""
===================================
AI 操作建议分析模块
===================================

职责：
1. 结合持仓信息和分析结果生成操作建议
2. 提供加仓、调仓、减仓、止盈止损等建议
3. 调用 AI 进行综合分析

⚠️ 免责声明：
本模块仅供模拟盘参考，不构成任何投资建议。
股市有风险，投资需谨慎。作者不对使用本模块产生的任何损失负责。
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.analyzer import AnalysisResult, GeminiAnalyzer
from src.portfolio import PortfolioManager, get_portfolio_manager, Position, DISCLAIMER
from src.config import get_config

logger = logging.getLogger(__name__)


# ============================================================
# AI 操作建议 Prompt
# ============================================================

OPERATION_ADVICE_PROMPT = """
你是一位专业的股票投资顾问，请根据以下信息为模拟盘用户提供今日操作建议。

## 当前持仓情况

{portfolio_info}

## 个股分析结果

{analysis_results}

## 风险预警

{risk_alerts}

## 风控参数

- 止损线：{stop_loss_pct}%
- 止盈线：{take_profit_pct}%
- 单股最大仓位：{max_single_position_pct}%
- 最大总仓位：{max_total_position_pct}%
- 当前总仓位：{current_position_ratio:.1f}%
- 可用现金：¥{available_cash:,.2f}

## 请提供以下建议

请根据以上信息，提供今日操作建议，包括：

1. **整体仓位建议**：是否需要调整总仓位？
2. **个股操作建议**：
   - 对于已持有的股票：是否加仓、减仓、止盈、止损？
   - 对于未持有但在分析列表中的股票：是否建议建仓？
3. **具体操作计划**：
   - 建议操作的股票代码和名称
   - 操作类型（买入/卖出/加仓/减仓）
   - 建议数量或金额
   - 目标价位
4. **风险提示**：当前需要注意的风险点

请用简洁明了的中文回答，使用 Markdown 格式，重点突出操作建议。

⚠️ 注意：这是模拟盘分析，仅供参考，不构成投资建议。
"""


class OperationAdvisor:
    """
    AI 操作建议分析器
    
    职责：
    1. 整合持仓信息和分析结果
    2. 调用 AI 生成操作建议
    3. 格式化输出建议报告
    """
    
    def __init__(self, analyzer: Optional[GeminiAnalyzer] = None):
        """
        初始化操作建议分析器
        
        Args:
            analyzer: AI 分析器（可选，默认创建新实例）
        """
        self.config = get_config()
        self.portfolio_manager = get_portfolio_manager()
        self.analyzer = analyzer or GeminiAnalyzer()
    
    def _format_portfolio_info(self) -> str:
        """格式化持仓信息"""
        p = self.portfolio_manager.portfolio
        
        if not p.positions:
            return "当前无持仓（空仓状态）"
        
        lines = [
            f"- 初始资金：¥{p.initial_capital:,.2f}",
            f"- 可用现金：¥{p.available_cash:,.2f}",
            f"- 持仓市值：¥{p.total_market_value:,.2f}",
            f"- 总资产：¥{p.total_assets:,.2f}",
            f"- 总收益率：{p.total_return_pct:+.2f}%",
            f"- 当前仓位：{p.position_ratio:.1f}%",
            "",
            "### 持仓明细",
            "",
        ]
        
        for pos in p.positions.values():
            emoji = "🟢" if pos.profit_loss >= 0 else "🔴"
            lines.append(
                f"- {emoji} **{pos.name}({pos.code})**：{pos.shares}股 | "
                f"成本¥{pos.cost_price:.2f} | 现价¥{pos.current_price:.2f} | "
                f"盈亏{pos.profit_loss_pct:+.2f}%"
            )
        
        return "\n".join(lines)
    
    def _format_analysis_results(self, results: List[AnalysisResult]) -> str:
        """格式化分析结果"""
        if not results:
            return "无分析结果"
        
        lines = []
        for r in sorted(results, key=lambda x: x.sentiment_score, reverse=True):
            emoji = "🟢" if r.operation_advice in ['买入', '加仓', '强烈买入'] else (
                "🔴" if r.operation_advice in ['卖出', '减仓', '强烈卖出'] else "🟡"
            )
            
            # 检查是否持有
            has_pos = self.portfolio_manager.has_position(r.code)
            pos_tag = "[已持有]" if has_pos else "[未持有]"
            
            lines.append(
                f"- {emoji} **{r.name}({r.code})** {pos_tag}：{r.operation_advice} | "
                f"评分{r.sentiment_score} | {r.trend_prediction}"
            )
            
            # 核心结论
            core = r.get_core_conclusion()
            if core:
                lines.append(f"  - 核心结论：{core[:100]}...")
            
            # 狙击点位
            points = r.get_sniper_points()
            if points:
                points_str = " | ".join([f"{k}:¥{v}" for k, v in points.items()])
                lines.append(f"  - 狙击点位：{points_str}")
        
        return "\n".join(lines)
    
    def _format_risk_alerts(self) -> str:
        """格式化风险预警"""
        alerts = self.portfolio_manager.check_risk_alerts()
        
        if not alerts:
            return "当前无风险预警"
        
        lines = []
        for alert in alerts:
            lines.append(f"- {alert['message']} → {alert['action']}")
        
        return "\n".join(lines)
    
    def generate_operation_advice(
        self,
        results: List[AnalysisResult],
        use_ai: bool = True
    ) -> str:
        """
        生成操作建议
        
        Args:
            results: 个股分析结果列表
            use_ai: 是否使用 AI 生成建议
            
        Returns:
            操作建议文本（Markdown 格式）
        """
        p = self.portfolio_manager.portfolio
        
        # 准备 Prompt
        prompt = OPERATION_ADVICE_PROMPT.format(
            portfolio_info=self._format_portfolio_info(),
            analysis_results=self._format_analysis_results(results),
            risk_alerts=self._format_risk_alerts(),
            stop_loss_pct=p.stop_loss_pct,
            take_profit_pct=p.take_profit_pct,
            max_single_position_pct=p.max_single_position_pct,
            max_total_position_pct=p.max_total_position_pct,
            current_position_ratio=p.position_ratio,
            available_cash=p.available_cash,
        )
        
        if use_ai and self.analyzer:
            try:
                logger.info("正在调用 AI 生成操作建议...")
                
                # 调用 AI
                response = self.analyzer.generate_content(prompt)
                
                if response:
                    logger.info("AI 操作建议生成成功")
                    return self._wrap_advice(response)
                else:
                    logger.warning("AI 返回空响应，使用规则引擎生成建议")
                    return self._generate_rule_based_advice(results)
                    
            except Exception as e:
                logger.error(f"AI 生成操作建议失败: {e}")
                return self._generate_rule_based_advice(results)
        else:
            return self._generate_rule_based_advice(results)
    
    def _wrap_advice(self, advice: str) -> str:
        """包装 AI 建议，添加免责声明"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
> 📅 生成时间：{now}

{advice}

---

{DISCLAIMER}
"""
    
    def _generate_rule_based_advice(self, results: List[AnalysisResult]) -> str:
        """
        基于规则生成操作建议（AI 不可用时的备选方案）
        """
        p = self.portfolio_manager.portfolio
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            f"> 📅 生成时间：{now}",
            "> ⚠️ AI 服务不可用，以下为规则引擎生成的建议",
            "",
            "### 📊 整体仓位建议",
            "",
        ]
        
        # 仓位建议
        if p.position_ratio >= p.max_total_position_pct:
            lines.append(f"- ⚠️ 当前仓位 {p.position_ratio:.1f}% 已达上限，**不建议继续加仓**")
        elif p.position_ratio < 30:
            lines.append(f"- 💡 当前仓位 {p.position_ratio:.1f}% 较低，可考虑适当加仓")
        else:
            lines.append(f"- ✅ 当前仓位 {p.position_ratio:.1f}% 适中")
        
        lines.extend(["", "### 📈 个股操作建议", ""])
        
        # 风险预警处理
        alerts = self.portfolio_manager.check_risk_alerts()
        for alert in alerts:
            if alert['type'] == 'stop_loss':
                lines.append(f"- 🔴 **{alert['name']}({alert['code']})**：已触及止损线，建议止损卖出")
            elif alert['type'] == 'take_profit':
                lines.append(f"- 🟢 **{alert['name']}({alert['code']})**：已达止盈目标，建议分批止盈")
        
        # 分析结果建议
        for r in results:
            has_pos = self.portfolio_manager.has_position(r.code)
            
            if has_pos:
                pos = self.portfolio_manager.get_position(r.code)
                if r.operation_advice in ['卖出', '减仓', '强烈卖出']:
                    lines.append(f"- 🔴 **{r.name}({r.code})**：建议减仓或卖出（当前盈亏 {pos.profit_loss_pct:+.2f}%）")
                elif r.operation_advice in ['买入', '加仓', '强烈买入']:
                    if p.position_ratio < p.max_total_position_pct:
                        lines.append(f"- 🟢 **{r.name}({r.code})**：可考虑加仓（当前盈亏 {pos.profit_loss_pct:+.2f}%）")
                else:
                    lines.append(f"- 🟡 **{r.name}({r.code})**：建议持有观望（当前盈亏 {pos.profit_loss_pct:+.2f}%）")
            else:
                if r.operation_advice in ['买入', '强烈买入'] and p.position_ratio < p.max_total_position_pct:
                    lines.append(f"- 🟢 **{r.name}({r.code})**：可考虑建仓（评分 {r.sentiment_score}）")
                elif r.operation_advice == '观望':
                    lines.append(f"- 🟡 **{r.name}({r.code})**：暂不建议建仓，继续观望")
        
        lines.extend([
            "",
            "### ⚠️ 风险提示",
            "",
            "- 以上建议仅供参考，请结合自身情况谨慎决策",
            "- 注意控制仓位，分散投资",
            "- 严格执行止损纪律",
            "",
            "---",
            "",
            DISCLAIMER,
        ])
        
        return "\n".join(lines)
    
    def get_quick_summary(self, results: List[AnalysisResult]) -> str:
        """
        生成快速摘要（用于控制台输出）
        """
        p = self.portfolio_manager.portfolio
        alerts = self.portfolio_manager.check_risk_alerts()
        
        lines = [
            "",
            "=" * 50,
            "📊 模拟盘快速摘要",
            "=" * 50,
            f"总资产: ¥{p.total_assets:,.2f} | 收益率: {p.total_return_pct:+.2f}%",
            f"仓位: {p.position_ratio:.1f}% | 持仓: {len(p.positions)} 只",
        ]
        
        if alerts:
            lines.append("")
            lines.append("⚠️ 风险预警:")
            for alert in alerts[:3]:  # 最多显示3条
                lines.append(f"  - {alert['message']}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


# ============================================================
# 便捷函数
# ============================================================

def generate_daily_operation_advice(
    results: List[AnalysisResult],
    analyzer: Optional[GeminiAnalyzer] = None
) -> str:
    """
    便捷函数：生成每日操作建议
    
    Args:
        results: 个股分析结果列表
        analyzer: AI 分析器（可选）
        
    Returns:
        操作建议文本
    """
    advisor = OperationAdvisor(analyzer=analyzer)
    return advisor.generate_operation_advice(results)
