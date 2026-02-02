# -*- coding: utf-8 -*-
"""
===================================
本地报告保存模块
===================================

职责：
1. 将分析报告保存为本地 Markdown 文件
2. 按日期组织文件结构
3. 生成包含仓位信息和操作建议的完整报告

⚠️ 免责声明：
本模块仅供模拟盘参考，不构成任何投资建议。
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.analyzer import AnalysisResult
from src.portfolio import PortfolioManager, get_portfolio_manager, DISCLAIMER

logger = logging.getLogger(__name__)


class ReportSaver:
    """
    本地报告保存器
    
    职责：
    1. 生成完整的 Markdown 分析报告
    2. 保存到本地文件夹
    3. 按日期命名文件
    """
    
    DEFAULT_REPORTS_DIR = "./reports"
    
    def __init__(self, reports_dir: Optional[str] = None):
        """
        初始化报告保存器
        
        Args:
            reports_dir: 报告保存目录（可选）
        """
        self.reports_dir = Path(reports_dir or self.DEFAULT_REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.portfolio_manager = get_portfolio_manager()
    
    def generate_full_report(
        self,
        results: List[AnalysisResult],
        market_report: str = "",
        operation_advice: str = "",
        report_date: Optional[str] = None
    ) -> str:
        """
        生成完整的分析报告（Markdown 格式）
        
        Args:
            results: 个股分析结果列表
            market_report: 大盘复盘内容
            operation_advice: AI 操作建议
            report_date: 报告日期
            
        Returns:
            完整的 Markdown 报告内容
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        report_time = datetime.now().strftime('%H:%M:%S')
        
        lines = [
            f"# 📊 {report_date} 股票智能分析报告",
            "",
            f"> 生成时间：{report_date} {report_time}",
            "",
            DISCLAIMER,
            "",
        ]
        
        # 1. 仓位概览
        lines.append(self.portfolio_manager.generate_portfolio_report())
        lines.append("")
        
        # 2. 风险预警
        alerts = self.portfolio_manager.check_risk_alerts()
        if alerts:
            lines.extend([
                "## 🚨 风险预警",
                "",
            ])
            for alert in alerts:
                lines.append(f"- {alert['message']} → **{alert['action']}**")
            lines.extend(["", "---", ""])
        
        # 3. AI 操作建议（如果有）
        if operation_advice:
            lines.extend([
                "## 🤖 AI 今日操作建议",
                "",
                operation_advice,
                "",
                "---",
                "",
            ])
        
        # 4. 大盘复盘（如果有）
        if market_report:
            lines.extend([
                "## 📈 大盘复盘",
                "",
                market_report,
                "",
                "---",
                "",
            ])
        
        # 5. 个股分析
        if results:
            lines.extend(self._generate_stock_analysis_section(results))
        
        # 6. 页脚
        lines.extend([
            "",
            "---",
            "",
            f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            DISCLAIMER,
        ])
        
        return "\n".join(lines)
    
    def _generate_stock_analysis_section(self, results: List[AnalysisResult]) -> List[str]:
        """生成个股分析部分"""
        lines = [
            "## 📈 个股分析",
            "",
        ]
        
        # 按评分排序
        sorted_results = sorted(results, key=lambda x: x.sentiment_score, reverse=True)
        
        # 统计信息
        buy_count = sum(1 for r in results if r.operation_advice in ['买入', '加仓', '强烈买入'])
        sell_count = sum(1 for r in results if r.operation_advice in ['卖出', '减仓', '强烈卖出'])
        hold_count = sum(1 for r in results if r.operation_advice in ['持有', '观望'])
        avg_score = sum(r.sentiment_score for r in results) / len(results) if results else 0
        
        lines.extend([
            "### 📊 操作建议汇总",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 🟢 建议买入/加仓 | **{buy_count}** 只 |",
            f"| 🟡 建议持有/观望 | **{hold_count}** 只 |",
            f"| 🔴 建议减仓/卖出 | **{sell_count}** 只 |",
            f"| 📈 平均评分 | **{avg_score:.1f}** 分 |",
            "",
            "---",
            "",
        ])
        
        # 逐个股票分析
        for result in sorted_results:
            # 检查是否持有该股票
            has_position = self.portfolio_manager.has_position(result.code)
            position = self.portfolio_manager.get_position(result.code)
            
            emoji = self._get_advice_emoji(result.operation_advice)
            
            lines.extend([
                f"### {emoji} {result.name} ({result.code})",
                "",
            ])
            
            # 持仓信息（如果有）
            if position:
                lines.extend([
                    f"**💼 持仓信息**：{position.shares} 股 | 成本 ¥{position.cost_price:.2f} | "
                    f"盈亏 {position.profit_loss_pct:+.2f}%",
                    "",
                ])
            
            lines.extend([
                f"**操作建议**：{result.operation_advice} | "
                f"**评分**：{result.sentiment_score} | "
                f"**趋势**：{result.trend_prediction}",
                "",
            ])
            
            # 核心结论
            core_conclusion = result.get_core_conclusion()
            if core_conclusion:
                lines.extend([
                    f"**📌 核心结论**：{core_conclusion}",
                    "",
                ])
            
            # 狙击点位
            sniper_points = result.get_sniper_points()
            if sniper_points:
                points_str = " | ".join([f"{k}: ¥{v}" for k, v in sniper_points.items()])
                lines.extend([
                    f"**🎯 狙击点位**：{points_str}",
                    "",
                ])
            
            # 检查清单
            checklist = result.get_checklist()
            if checklist:
                lines.append("**✅ 检查清单**：")
                for item in checklist:
                    lines.append(f"  - {item}")
                lines.append("")
            
            # 技术分析
            if result.technical_analysis:
                lines.extend([
                    f"**📊 技术分析**：{result.technical_analysis}",
                    "",
                ])
            
            # 风险提示
            if result.risk_warning:
                lines.extend([
                    f"**⚠️ 风险提示**：{result.risk_warning}",
                    "",
                ])
            
            lines.append("---")
            lines.append("")
        
        return lines
    
    def _get_advice_emoji(self, advice: str) -> str:
        """根据操作建议返回对应的 emoji"""
        if advice in ['买入', '加仓', '强烈买入']:
            return "🟢"
        elif advice in ['卖出', '减仓', '强烈卖出']:
            return "🔴"
        else:
            return "🟡"
    
    def save_report(
        self,
        results: List[AnalysisResult],
        market_report: str = "",
        operation_advice: str = "",
        report_date: Optional[str] = None,
        filename_prefix: str = "analysis"
    ) -> str:
        """
        保存报告到本地文件
        
        Args:
            results: 个股分析结果列表
            market_report: 大盘复盘内容
            operation_advice: AI 操作建议
            report_date: 报告日期
            filename_prefix: 文件名前缀
            
        Returns:
            保存的文件路径
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        # 生成报告内容
        content = self.generate_full_report(
            results=results,
            market_report=market_report,
            operation_advice=operation_advice,
            report_date=report_date
        )
        
        # 生成文件名：analysis_2026-02-02_223000.md
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{filename_prefix}_{report_date}_{timestamp}.md"
        filepath = self.reports_dir / filename
        
        # 保存文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"报告已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            raise
    
    def save_daily_summary(
        self,
        results: List[AnalysisResult],
        market_report: str = "",
        operation_advice: str = ""
    ) -> str:
        """
        保存每日汇总报告（覆盖当天的汇总文件）
        
        Args:
            results: 个股分析结果列表
            market_report: 大盘复盘内容
            operation_advice: AI 操作建议
            
        Returns:
            保存的文件路径
        """
        report_date = datetime.now().strftime('%Y-%m-%d')
        
        # 生成报告内容
        content = self.generate_full_report(
            results=results,
            market_report=market_report,
            operation_advice=operation_advice,
            report_date=report_date
        )
        
        # 每日汇总文件名：daily_2026-02-02.md
        filename = f"daily_{report_date}.md"
        filepath = self.reports_dir / filename
        
        # 保存文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"每日汇总报告已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"保存每日汇总报告失败: {e}")
            raise
    
    def list_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出最近的报告文件
        
        Args:
            limit: 返回数量限制
            
        Returns:
            报告文件信息列表
        """
        reports = []
        
        for filepath in sorted(self.reports_dir.glob("*.md"), reverse=True)[:limit]:
            stat = filepath.stat()
            reports.append({
                "filename": filepath.name,
                "path": str(filepath),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return reports


# ============================================================
# 便捷函数
# ============================================================

_report_saver: Optional[ReportSaver] = None


def get_report_saver(reports_dir: Optional[str] = None) -> ReportSaver:
    """获取报告保存器单例"""
    global _report_saver
    if _report_saver is None:
        _report_saver = ReportSaver(reports_dir)
    return _report_saver


def save_analysis_report(
    results: List[AnalysisResult],
    market_report: str = "",
    operation_advice: str = ""
) -> str:
    """
    便捷函数：保存分析报告
    
    Returns:
        保存的文件路径
    """
    saver = get_report_saver()
    return saver.save_daily_summary(
        results=results,
        market_report=market_report,
        operation_advice=operation_advice
    )
