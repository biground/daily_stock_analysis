# -*- coding: utf-8 -*-
"""
===================================
模拟盘 WebUI API
===================================

提供模拟盘相关的 API 接口：
1. 仪表盘数据
2. 交易记录
3. AI 准确度分析
4. 收益统计
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PortfolioAPI:
    """模拟盘 API 服务"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
    
    def _load_json(self, filename: str) -> Dict:
        """加载 JSON 文件"""
        filepath = self.data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载 {filename} 失败: {e}")
        return {}
    
    def get_portfolio(self) -> Dict[str, Any]:
        """获取当前持仓"""
        return self._load_json("portfolio.json")
    
    def get_trades(self) -> List[Dict]:
        """获取交易记录"""
        data = self._load_json("trades.json")
        return data.get("trades", [])
    
    def get_snapshots(self) -> Dict[str, Dict]:
        """获取每日快照"""
        data = self._load_json("daily_snapshots.json")
        return data.get("snapshots", {})
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        portfolio = self.get_portfolio()
        snapshots = self.get_snapshots()
        trades = self.get_trades()
        
        # 计算基础数据
        positions = portfolio.get("positions", {})
        initial_capital = portfolio.get("initial_capital", 0)
        available_cash = portfolio.get("available_cash", 0)
        
        # 计算持仓市值和盈亏
        total_market_value = 0
        total_cost = 0
        position_list = []
        
        for code, pos in positions.items():
            shares = pos.get("shares", 0)
            cost_price = pos.get("cost_price", 0)
            current_price = pos.get("current_price", cost_price)
            
            market_value = shares * current_price
            cost_amount = shares * cost_price
            profit_loss = market_value - cost_amount
            profit_loss_pct = (profit_loss / cost_amount * 100) if cost_amount > 0 else 0
            
            total_market_value += market_value
            total_cost += cost_amount
            
            position_list.append({
                "code": code,
                "name": pos.get("name", ""),
                "shares": shares,
                "cost_price": cost_price,
                "current_price": current_price,
                "market_value": market_value,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
            })
        
        total_assets = available_cash + total_market_value
        total_profit_loss = total_market_value - total_cost
        total_return_pct = ((total_assets - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0
        position_ratio = (total_market_value / total_assets * 100) if total_assets > 0 else 0
        
        # 计算今日盈亏
        today = datetime.now().strftime('%Y-%m-%d')
        today_snapshot = snapshots.get(today, {})
        daily_profit_loss = today_snapshot.get("daily_profit_loss", 0)
        daily_return_pct = today_snapshot.get("daily_return_pct", 0)
        
        # 获取最近7天收益趋势
        sorted_dates = sorted(snapshots.keys(), reverse=True)[:7]
        daily_returns = []
        for date in reversed(sorted_dates):
            snap = snapshots[date]
            daily_returns.append({
                "date": date,
                "total_assets": snap.get("total_assets", 0),
                "daily_profit_loss": snap.get("daily_profit_loss", 0),
                "daily_return_pct": snap.get("daily_return_pct", 0),
            })
        
        # 统计交易数据
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t.get("action") in ["buy", "add"]])
        sell_trades = len([t for t in trades if t.get("action") in ["sell", "reduce"]])
        
        return {
            "summary": {
                "initial_capital": initial_capital,
                "total_assets": total_assets,
                "available_cash": available_cash,
                "total_market_value": total_market_value,
                "total_profit_loss": total_profit_loss,
                "total_return_pct": total_return_pct,
                "position_ratio": position_ratio,
                "daily_profit_loss": daily_profit_loss,
                "daily_return_pct": daily_return_pct,
                "position_count": len(positions),
            },
            "positions": position_list,
            "daily_returns": daily_returns,
            "trade_stats": {
                "total": total_trades,
                "buy": buy_trades,
                "sell": sell_trades,
            },
            "risk_params": {
                "stop_loss_pct": portfolio.get("stop_loss_pct", 8),
                "take_profit_pct": portfolio.get("take_profit_pct", 20),
                "max_single_position_pct": portfolio.get("max_single_position_pct", 30),
                "max_total_position_pct": portfolio.get("max_total_position_pct", 80),
            }
        }
    
    def get_ai_accuracy(self) -> Dict[str, Any]:
        """
        分析 AI 建议准确度
        
        逻辑：
        1. 读取每日分析报告中的 AI 建议
        2. 对比第二天的实际涨跌
        3. 如果建议买入/加仓且第二天涨了，算准确
        4. 如果建议卖出/减仓且第二天跌了，算准确
        """
        reports_dir = Path("./reports")
        snapshots = self.get_snapshots()
        
        # 分析结果
        accuracy_records = []
        total_predictions = 0
        correct_predictions = 0
        
        # 按日期排序快照
        sorted_dates = sorted(snapshots.keys())
        
        for i, date in enumerate(sorted_dates[:-1]):  # 排除最后一天（没有第二天数据）
            current_snap = snapshots[date]
            next_date = sorted_dates[i + 1]
            next_snap = snapshots[next_date]
            
            # 计算第二天的涨跌
            current_assets = current_snap.get("total_assets", 0)
            next_assets = next_snap.get("total_assets", 0)
            
            if current_assets > 0:
                next_day_return = (next_assets - current_assets) / current_assets * 100
                is_up = next_day_return > 0
                
                # 简化逻辑：假设每天都有 AI 建议
                # 实际应该从报告中读取，这里用持仓变化推断
                positions_today = current_snap.get("positions_snapshot", {})
                positions_next = next_snap.get("positions_snapshot", {})
                
                # 检查是否有持仓（有持仓说明 AI 建议持有/买入）
                had_position = len(positions_today) > 0
                
                if had_position:
                    total_predictions += 1
                    # 持有时，涨了算准确
                    is_correct = is_up
                    if is_correct:
                        correct_predictions += 1
                    
                    accuracy_records.append({
                        "date": date,
                        "next_date": next_date,
                        "prediction": "持有" if had_position else "空仓",
                        "next_day_return": next_day_return,
                        "is_correct": is_correct,
                        "total_assets": current_assets,
                    })
        
        accuracy_rate = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # 按月统计
        monthly_stats = {}
        for record in accuracy_records:
            month = record["date"][:7]  # YYYY-MM
            if month not in monthly_stats:
                monthly_stats[month] = {"total": 0, "correct": 0}
            monthly_stats[month]["total"] += 1
            if record["is_correct"]:
                monthly_stats[month]["correct"] += 1
        
        monthly_accuracy = []
        for month, stats in sorted(monthly_stats.items()):
            rate = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            monthly_accuracy.append({
                "month": month,
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": rate,
            })
        
        return {
            "summary": {
                "total_predictions": total_predictions,
                "correct_predictions": correct_predictions,
                "accuracy_rate": accuracy_rate,
            },
            "records": accuracy_records[-30:],  # 最近30条
            "monthly_accuracy": monthly_accuracy,
        }
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """获取交易历史"""
        trades = self.get_trades()
        return trades[-limit:][::-1]  # 最新的在前面


# 单例
_portfolio_api: Optional[PortfolioAPI] = None


def get_portfolio_api() -> PortfolioAPI:
    global _portfolio_api
    if _portfolio_api is None:
        _portfolio_api = PortfolioAPI()
    return _portfolio_api
