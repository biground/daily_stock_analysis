# -*- coding: utf-8 -*-
"""
===================================
模拟盘仓位管理模块
===================================

职责：
1. 管理模拟盘持仓配置
2. 计算持仓收益
3. 生成仓位报告
4. 支持 JSON 配置文件持久化

⚠️ 免责声明：
本模块仅供模拟盘参考，不构成任何投资建议。
股市有风险，投资需谨慎。作者不对使用本模块产生的任何损失负责。
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# ============================================================
# 免责声明
# ============================================================

DISCLAIMER = """
⚠️ **免责声明**

本系统仅供模拟盘参考，不构成任何投资建议。
- 所有分析结果仅基于历史数据和 AI 模型推断
- 股市有风险，投资需谨慎
- 作者不对使用本系统产生的任何损失负责
- 请在做出投资决策前咨询专业投资顾问

---
"""


# ============================================================
# 数据结构
# ============================================================

@dataclass
class Position:
    """
    单只股票持仓信息
    """
    code: str                          # 股票代码
    name: str = ""                     # 股票名称
    shares: int = 0                    # 持仓股数
    cost_price: float = 0.0            # 成本价（买入均价）
    current_price: float = 0.0         # 当前价格（运行时更新）
    buy_date: str = ""                 # 首次买入日期
    last_update: str = ""              # 最后更新时间
    notes: str = ""                    # 备注
    
    # 计算属性
    @property
    def cost_amount(self) -> float:
        """成本金额"""
        return self.shares * self.cost_price
    
    @property
    def market_value(self) -> float:
        """当前市值"""
        return self.shares * self.current_price
    
    @property
    def profit_loss(self) -> float:
        """盈亏金额"""
        return self.market_value - self.cost_amount
    
    @property
    def profit_loss_pct(self) -> float:
        """盈亏比例（%）"""
        if self.cost_amount == 0:
            return 0.0
        return (self.profit_loss / self.cost_amount) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""
        return {
            "code": self.code,
            "name": self.name,
            "shares": self.shares,
            "cost_price": self.cost_price,
            "current_price": self.current_price,
            "buy_date": self.buy_date,
            "last_update": self.last_update,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """从字典创建"""
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            shares=data.get("shares", 0),
            cost_price=data.get("cost_price", 0.0),
            current_price=data.get("current_price", 0.0),
            buy_date=data.get("buy_date", ""),
            last_update=data.get("last_update", ""),
            notes=data.get("notes", ""),
        )


@dataclass
class PortfolioConfig:
    """
    模拟盘配置
    """
    # 账户信息
    initial_capital: float = 100000.0      # 初始资金（元）
    available_cash: float = 100000.0       # 可用现金（元）
    
    # 风控参数
    max_single_position_pct: float = 30.0  # 单只股票最大仓位比例（%）
    stop_loss_pct: float = 8.0             # 止损线（%）
    take_profit_pct: float = 20.0          # 止盈线（%）
    max_total_position_pct: float = 80.0   # 最大总仓位比例（%）
    
    # 交易参数
    commission_rate: float = 0.0003        # 佣金费率（万三）
    stamp_duty_rate: float = 0.001         # 印花税率（千一，卖出时收取）
    min_commission: float = 5.0            # 最低佣金（元）
    
    # 持仓列表
    positions: Dict[str, Position] = field(default_factory=dict)
    
    # 元数据
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def total_cost(self) -> float:
        """总成本"""
        return sum(p.cost_amount for p in self.positions.values())
    
    @property
    def total_market_value(self) -> float:
        """总市值"""
        return sum(p.market_value for p in self.positions.values())
    
    @property
    def total_profit_loss(self) -> float:
        """总盈亏"""
        return self.total_market_value - self.total_cost
    
    @property
    def total_profit_loss_pct(self) -> float:
        """总盈亏比例（%）"""
        if self.total_cost == 0:
            return 0.0
        return (self.total_profit_loss / self.total_cost) * 100
    
    @property
    def total_assets(self) -> float:
        """总资产 = 可用现金 + 持仓市值"""
        return self.available_cash + self.total_market_value
    
    @property
    def total_return_pct(self) -> float:
        """总收益率（相对初始资金）"""
        if self.initial_capital == 0:
            return 0.0
        return ((self.total_assets - self.initial_capital) / self.initial_capital) * 100
    
    @property
    def position_ratio(self) -> float:
        """当前仓位比例（%）"""
        if self.total_assets == 0:
            return 0.0
        return (self.total_market_value / self.total_assets) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "initial_capital": self.initial_capital,
            "available_cash": self.available_cash,
            "max_single_position_pct": self.max_single_position_pct,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "max_total_position_pct": self.max_total_position_pct,
            "commission_rate": self.commission_rate,
            "stamp_duty_rate": self.stamp_duty_rate,
            "min_commission": self.min_commission,
            "positions": {code: pos.to_dict() for code, pos in self.positions.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PortfolioConfig':
        """从字典创建"""
        positions = {}
        for code, pos_data in data.get("positions", {}).items():
            positions[code] = Position.from_dict(pos_data)
        
        return cls(
            initial_capital=data.get("initial_capital", 100000.0),
            available_cash=data.get("available_cash", 100000.0),
            max_single_position_pct=data.get("max_single_position_pct", 30.0),
            stop_loss_pct=data.get("stop_loss_pct", 8.0),
            take_profit_pct=data.get("take_profit_pct", 20.0),
            max_total_position_pct=data.get("max_total_position_pct", 80.0),
            commission_rate=data.get("commission_rate", 0.0003),
            stamp_duty_rate=data.get("stamp_duty_rate", 0.001),
            min_commission=data.get("min_commission", 5.0),
            positions=positions,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


# ============================================================
# 仓位管理器
# ============================================================

class PortfolioManager:
    """
    模拟盘仓位管理器
    
    职责：
    1. 加载/保存仓位配置
    2. 更新持仓价格
    3. 生成仓位报告
    4. 计算操作建议
    """
    
    DEFAULT_CONFIG_PATH = "./data/portfolio.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化仓位管理器
        
        Args:
            config_path: 配置文件路径（可选）
        """
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        self.portfolio = self._load_config()
    
    def _load_config(self) -> PortfolioConfig:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"已加载仓位配置: {self.config_path}")
                return PortfolioConfig.from_dict(data)
            except Exception as e:
                logger.error(f"加载仓位配置失败: {e}")
        
        logger.info("使用默认仓位配置")
        return PortfolioConfig()
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.portfolio.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"仓位配置已保存: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存仓位配置失败: {e}")
            return False
    
    def add_position(
        self,
        code: str,
        name: str,
        shares: int,
        cost_price: float,
        notes: str = ""
    ) -> bool:
        """
        添加或更新持仓
        
        Args:
            code: 股票代码
            name: 股票名称
            shares: 股数
            cost_price: 成本价
            notes: 备注
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if code in self.portfolio.positions:
            # 更新现有持仓（加权平均成本）
            pos = self.portfolio.positions[code]
            total_cost = pos.cost_amount + (shares * cost_price)
            total_shares = pos.shares + shares
            if total_shares > 0:
                pos.cost_price = total_cost / total_shares
            pos.shares = total_shares
            pos.last_update = now
            if notes:
                pos.notes = notes
            logger.info(f"更新持仓: {code} {name}, 总股数: {total_shares}, 成本价: {pos.cost_price:.2f}")
        else:
            # 新增持仓
            self.portfolio.positions[code] = Position(
                code=code,
                name=name,
                shares=shares,
                cost_price=cost_price,
                buy_date=now.split()[0],
                last_update=now,
                notes=notes,
            )
            logger.info(f"新增持仓: {code} {name}, 股数: {shares}, 成本价: {cost_price:.2f}")
        
        return self.save_config()
    
    def reduce_position(self, code: str, shares: int, sell_price: float) -> bool:
        """
        减仓
        
        Args:
            code: 股票代码
            shares: 卖出股数
            sell_price: 卖出价格
        """
        if code not in self.portfolio.positions:
            logger.warning(f"持仓不存在: {code}")
            return False
        
        pos = self.portfolio.positions[code]
        if shares > pos.shares:
            logger.warning(f"卖出股数 {shares} 超过持仓 {pos.shares}")
            return False
        
        # 计算卖出收益
        sell_amount = shares * sell_price
        cost = shares * pos.cost_price
        profit = sell_amount - cost
        
        # 计算交易费用
        commission = max(sell_amount * self.portfolio.commission_rate, self.portfolio.min_commission)
        stamp_duty = sell_amount * self.portfolio.stamp_duty_rate
        net_profit = profit - commission - stamp_duty
        
        # 更新持仓
        pos.shares -= shares
        pos.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新可用现金
        self.portfolio.available_cash += (sell_amount - commission - stamp_duty)
        
        if pos.shares == 0:
            del self.portfolio.positions[code]
            logger.info(f"清仓: {code}, 净收益: {net_profit:.2f}")
        else:
            logger.info(f"减仓: {code}, 卖出 {shares} 股, 净收益: {net_profit:.2f}")
        
        return self.save_config()
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """
        批量更新持仓价格
        
        Args:
            prices: {股票代码: 当前价格}
        """
        for code, price in prices.items():
            if code in self.portfolio.positions:
                self.portfolio.positions[code].current_price = price
                self.portfolio.positions[code].last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.save_config()
    
    def get_position(self, code: str) -> Optional[Position]:
        """获取单只股票持仓"""
        return self.portfolio.positions.get(code)
    
    def has_position(self, code: str) -> bool:
        """检查是否持有某只股票"""
        return code in self.portfolio.positions
    
    def get_position_summary(self) -> Dict[str, Any]:
        """
        获取持仓汇总信息
        
        Returns:
            包含账户和持仓信息的字典
        """
        return {
            "initial_capital": self.portfolio.initial_capital,
            "available_cash": self.portfolio.available_cash,
            "total_market_value": self.portfolio.total_market_value,
            "total_assets": self.portfolio.total_assets,
            "total_cost": self.portfolio.total_cost,
            "total_profit_loss": self.portfolio.total_profit_loss,
            "total_profit_loss_pct": self.portfolio.total_profit_loss_pct,
            "total_return_pct": self.portfolio.total_return_pct,
            "position_ratio": self.portfolio.position_ratio,
            "position_count": len(self.portfolio.positions),
            "positions": [
                {
                    "code": pos.code,
                    "name": pos.name,
                    "shares": pos.shares,
                    "cost_price": pos.cost_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "profit_loss": pos.profit_loss,
                    "profit_loss_pct": pos.profit_loss_pct,
                }
                for pos in self.portfolio.positions.values()
            ],
            "risk_params": {
                "stop_loss_pct": self.portfolio.stop_loss_pct,
                "take_profit_pct": self.portfolio.take_profit_pct,
                "max_single_position_pct": self.portfolio.max_single_position_pct,
                "max_total_position_pct": self.portfolio.max_total_position_pct,
            },
        }
    
    def generate_portfolio_report(self) -> str:
        """
        生成仓位报告（Markdown 格式）
        
        Returns:
            Markdown 格式的仓位报告
        """
        p = self.portfolio
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            "## 💼 模拟盘持仓报告",
            "",
            f"> 更新时间：{now}",
            "",
            "### 📊 账户概览",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 初始资金 | ¥{p.initial_capital:,.2f} |",
            f"| 可用现金 | ¥{p.available_cash:,.2f} |",
            f"| 持仓市值 | ¥{p.total_market_value:,.2f} |",
            f"| 总资产 | ¥{p.total_assets:,.2f} |",
            f"| 总收益率 | {p.total_return_pct:+.2f}% |",
            f"| 当前仓位 | {p.position_ratio:.1f}% |",
            "",
        ]
        
        if p.positions:
            lines.extend([
                "### 📈 持仓明细",
                "",
                "| 股票 | 股数 | 成本价 | 现价 | 市值 | 盈亏 | 盈亏% |",
                "|------|------|--------|------|------|------|-------|",
            ])
            
            for pos in sorted(p.positions.values(), key=lambda x: x.profit_loss_pct, reverse=True):
                emoji = "🟢" if pos.profit_loss >= 0 else "🔴"
                lines.append(
                    f"| {emoji} {pos.name}({pos.code}) | {pos.shares} | "
                    f"¥{pos.cost_price:.2f} | ¥{pos.current_price:.2f} | "
                    f"¥{pos.market_value:,.2f} | ¥{pos.profit_loss:+,.2f} | "
                    f"{pos.profit_loss_pct:+.2f}% |"
                )
            
            lines.append("")
        else:
            lines.extend([
                "### 📈 持仓明细",
                "",
                "*当前无持仓*",
                "",
            ])
        
        lines.extend([
            "### ⚙️ 风控参数",
            "",
            f"- 止损线：**{p.stop_loss_pct}%**",
            f"- 止盈线：**{p.take_profit_pct}%**",
            f"- 单股最大仓位：**{p.max_single_position_pct}%**",
            f"- 最大总仓位：**{p.max_total_position_pct}%**",
            "",
        ])
        
        return "\n".join(lines)
    
    def check_risk_alerts(self) -> List[Dict[str, Any]]:
        """
        检查风险预警
        
        Returns:
            风险预警列表
        """
        alerts = []
        p = self.portfolio
        
        for pos in p.positions.values():
            # 止损预警
            if pos.profit_loss_pct <= -p.stop_loss_pct:
                alerts.append({
                    "type": "stop_loss",
                    "level": "danger",
                    "code": pos.code,
                    "name": pos.name,
                    "message": f"⚠️ {pos.name}({pos.code}) 已触及止损线！亏损 {pos.profit_loss_pct:.2f}%",
                    "action": "建议止损卖出",
                })
            # 止损接近预警
            elif pos.profit_loss_pct <= -(p.stop_loss_pct * 0.7):
                alerts.append({
                    "type": "stop_loss_warning",
                    "level": "warning",
                    "code": pos.code,
                    "name": pos.name,
                    "message": f"⚡ {pos.name}({pos.code}) 接近止损线，亏损 {pos.profit_loss_pct:.2f}%",
                    "action": "密切关注，准备止损",
                })
            
            # 止盈预警
            if pos.profit_loss_pct >= p.take_profit_pct:
                alerts.append({
                    "type": "take_profit",
                    "level": "success",
                    "code": pos.code,
                    "name": pos.name,
                    "message": f"🎉 {pos.name}({pos.code}) 已达止盈目标！盈利 {pos.profit_loss_pct:.2f}%",
                    "action": "建议分批止盈",
                })
            # 止盈接近预警
            elif pos.profit_loss_pct >= (p.take_profit_pct * 0.8):
                alerts.append({
                    "type": "take_profit_warning",
                    "level": "info",
                    "code": pos.code,
                    "name": pos.name,
                    "message": f"📈 {pos.name}({pos.code}) 接近止盈目标，盈利 {pos.profit_loss_pct:.2f}%",
                    "action": "考虑部分止盈",
                })
        
        # 总仓位预警
        if p.position_ratio >= p.max_total_position_pct:
            alerts.append({
                "type": "position_limit",
                "level": "warning",
                "code": "",
                "name": "总仓位",
                "message": f"⚠️ 总仓位 {p.position_ratio:.1f}% 已达上限 {p.max_total_position_pct}%",
                "action": "不建议继续加仓",
            })
        
        return alerts


# ============================================================
# 便捷函数
# ============================================================

_portfolio_manager: Optional[PortfolioManager] = None


def get_portfolio_manager(config_path: Optional[str] = None) -> PortfolioManager:
    """获取仓位管理器单例"""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager(config_path)
    return _portfolio_manager


def reset_portfolio_manager() -> None:
    """重置仓位管理器（主要用于测试）"""
    global _portfolio_manager
    _portfolio_manager = None
