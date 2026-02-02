# -*- coding: utf-8 -*-
"""
===================================
模拟盘交易工具
===================================

使用方法：
    python trade.py buy 515080 招商中证红利ETF 1000 1.55 "回调加仓"
    python trade.py sell 159707 光伏ETF 4500 0.629 "止损卖出"
    python trade.py add 515080 招商中证红利ETF 500 1.54 "补仓"
    python trade.py reduce 515080 招商中证红利ETF 1000 1.60 "部分止盈"
    python trade.py list                    # 查看持仓
    python trade.py trades                  # 查看交易记录
    python trade.py report                  # 查看收益报告
    python trade.py snapshot                # 记录今日快照
"""

import sys
import argparse
from src.portfolio import get_portfolio_manager, reset_portfolio_manager


def main():
    parser = argparse.ArgumentParser(description="模拟盘交易工具")
    subparsers = parser.add_subparsers(dest="command", help="操作类型")
    
    # 买入命令
    buy_parser = subparsers.add_parser("buy", help="买入股票")
    buy_parser.add_argument("code", help="股票代码")
    buy_parser.add_argument("name", help="股票名称")
    buy_parser.add_argument("shares", type=int, help="股数")
    buy_parser.add_argument("price", type=float, help="价格")
    buy_parser.add_argument("reason", nargs="?", default="", help="交易理由")
    
    # 卖出命令
    sell_parser = subparsers.add_parser("sell", help="卖出股票（清仓）")
    sell_parser.add_argument("code", help="股票代码")
    sell_parser.add_argument("name", help="股票名称")
    sell_parser.add_argument("shares", type=int, help="股数")
    sell_parser.add_argument("price", type=float, help="价格")
    sell_parser.add_argument("reason", nargs="?", default="", help="交易理由")
    
    # 加仓命令
    add_parser = subparsers.add_parser("add", help="加仓")
    add_parser.add_argument("code", help="股票代码")
    add_parser.add_argument("name", help="股票名称")
    add_parser.add_argument("shares", type=int, help="股数")
    add_parser.add_argument("price", type=float, help="价格")
    add_parser.add_argument("reason", nargs="?", default="", help="交易理由")
    
    # 减仓命令
    reduce_parser = subparsers.add_parser("reduce", help="减仓")
    reduce_parser.add_argument("code", help="股票代码")
    reduce_parser.add_argument("name", help="股票名称")
    reduce_parser.add_argument("shares", type=int, help="股数")
    reduce_parser.add_argument("price", type=float, help="价格")
    reduce_parser.add_argument("reason", nargs="?", default="", help="交易理由")
    
    # 查看持仓
    subparsers.add_parser("list", help="查看当前持仓")
    
    # 查看交易记录
    trades_parser = subparsers.add_parser("trades", help="查看交易记录")
    trades_parser.add_argument("-n", "--num", type=int, default=10, help="显示条数")
    
    # 查看收益报告
    report_parser = subparsers.add_parser("report", help="查看收益报告")
    report_parser.add_argument("-d", "--days", type=int, default=7, help="统计天数")
    
    # 记录快照
    subparsers.add_parser("snapshot", help="记录今日快照")
    
    # 更新价格
    price_parser = subparsers.add_parser("price", help="更新股票价格")
    price_parser.add_argument("code", help="股票代码")
    price_parser.add_argument("current_price", type=float, help="当前价格")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pm = get_portfolio_manager()
    
    # 执行命令
    if args.command in ["buy", "sell", "add", "reduce"]:
        trade = pm.record_trade(
            code=args.code,
            name=args.name,
            action=args.command,
            shares=args.shares,
            price=args.price,
            reason=args.reason
        )
        
        action_text = {"buy": "买入", "sell": "卖出", "add": "加仓", "reduce": "减仓"}[args.command]
        print(f"\n✅ 交易成功!")
        print(f"   操作: {action_text}")
        print(f"   股票: {args.name}({args.code})")
        print(f"   数量: {args.shares} 股")
        print(f"   价格: ¥{args.price:.3f}")
        print(f"   金额: ¥{trade.amount:,.2f}")
        print(f"   佣金: ¥{trade.commission:.2f}")
        if trade.stamp_duty > 0:
            print(f"   印花税: ¥{trade.stamp_duty:.2f}")
        print(f"   理由: {args.reason or '无'}")
        print(f"\n💰 可用现金: ¥{pm.portfolio.available_cash:,.2f}")
        
    elif args.command == "list":
        p = pm.portfolio
        print("\n" + "=" * 50)
        print("📊 当前持仓")
        print("=" * 50)
        print(f"总资产: ¥{p.total_assets:,.2f}")
        print(f"可用现金: ¥{p.available_cash:,.2f}")
        print(f"持仓市值: ¥{p.total_market_value:,.2f}")
        print(f"总盈亏: ¥{p.total_profit_loss:+,.2f} ({p.total_profit_loss_pct:+.2f}%)")
        print(f"仓位比例: {p.position_ratio:.1f}%")
        print("-" * 50)
        
        if p.positions:
            print(f"{'代码':<10} {'名称':<15} {'持仓':<8} {'成本':<10} {'现价':<10} {'盈亏':<12}")
            print("-" * 50)
            for pos in p.positions.values():
                pnl_str = f"¥{pos.profit_loss:+,.2f} ({pos.profit_loss_pct:+.2f}%)"
                print(f"{pos.code:<10} {pos.name:<15} {pos.shares:<8} ¥{pos.cost_price:<9.3f} ¥{pos.current_price:<9.3f} {pnl_str}")
        else:
            print("暂无持仓")
        print()
        
    elif args.command == "trades":
        trades = pm.load_trades()[-args.num:]
        print("\n" + "=" * 60)
        print(f"📝 最近 {len(trades)} 条交易记录")
        print("=" * 60)
        
        if trades:
            for t in trades:
                action_text = {"buy": "🟢买入", "sell": "🔴卖出", "add": "🟢加仓", "reduce": "🔴减仓"}.get(t.action, t.action)
                print(f"{t.date} {t.time} | {action_text} {t.name}({t.code}) {t.shares}股 @ ¥{t.price:.3f} = ¥{t.amount:,.2f}")
                if t.reason:
                    print(f"           理由: {t.reason}")
        else:
            print("暂无交易记录")
        print()
        
    elif args.command == "report":
        print(pm.generate_performance_report(days=args.days))
        
    elif args.command == "snapshot":
        snapshot = pm.take_daily_snapshot()
        print(f"\n✅ 今日快照已记录")
        print(f"   日期: {snapshot.date}")
        print(f"   总资产: ¥{snapshot.total_assets:,.2f}")
        print(f"   当日盈亏: ¥{snapshot.daily_profit_loss:+,.2f} ({snapshot.daily_return_pct:+.2f}%)")
        print(f"   累计收益: {snapshot.total_return_pct:+.2f}%")
        print()
        
    elif args.command == "price":
        if args.code in pm.portfolio.positions:
            pm.portfolio.positions[args.code].current_price = args.current_price
            pm.save_config()
            pos = pm.portfolio.positions[args.code]
            print(f"\n✅ 价格已更新: {pos.name}({args.code}) -> ¥{args.current_price:.3f}")
            print(f"   盈亏: ¥{pos.profit_loss:+,.2f} ({pos.profit_loss_pct:+.2f}%)")
        else:
            print(f"\n❌ 持仓不存在: {args.code}")


if __name__ == "__main__":
    main()
