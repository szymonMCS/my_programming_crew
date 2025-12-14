import gradio as gr
from decimal import Decimal
import pandas as pd
from app_state import app_state
from utils.helpers import format_monetary


def create_portfolio_component():
    """Create the portfolio summary component with charts."""

    with gr.Column():
        gr.Markdown("## Portfolio Summary")

        refresh_btn = gr.Button("Refresh Portfolio", variant="primary")

        with gr.Row():
            with gr.Column():
                summary_output = gr.Markdown()

            with gr.Column():
                pnl_output = gr.Markdown()

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Holdings Breakdown")
                holdings_table = gr.Dataframe(
                    headers=["Symbol", "Quantity", "Avg Cost", "Current Price", "Total Value", "Gain/Loss"],
                    datatype=["str", "number", "str", "str", "str", "str"],
                    row_count=10
                )

            with gr.Column():
                gr.Markdown("### Portfolio Allocation")
                allocation_chart = gr.Plot()

        with gr.Row():
            gr.Markdown("### Profit/Loss Chart")
            pnl_chart = gr.Plot()

    def refresh_portfolio():
        try:
            if not app_state.current_account:
                return "Please login first", "", None, None, None

            account = app_state.current_account
            holdings = app_state.get_holdings()
            valuator = app_state.get_portfolio_valuator()
            pnl_calc = app_state.get_profit_loss_calculator()

            if not valuator or not pnl_calc:
                return "Error calculating portfolio", "", None, None, None

            # Calculate portfolio values
            cash_value = valuator.calculate_cash_value()
            holdings_value = valuator.calculate_holding_value()
            total_value = valuator.calculate_total_value()
            total_pnl = pnl_calc.calculate_total_pnl()
            net_deposits = pnl_calc.calculate_cumulative_net_deposits()

            # Create summary
            summary_md = f"""
### Account Summary

**Cash Balance:** {format_monetary(cash_value)}
**Holdings Value:** {format_monetary(holdings_value)}
**Total Portfolio Value:** {format_monetary(total_value)}

**Net Deposits:** {format_monetary(net_deposits)}
**Total Deposits:** {format_monetary(account.total_deposits)}
**Total Withdrawals:** {format_monetary(account.total_withdrawals)}
"""

            # Create P&L summary
            pnl_percentage = (total_pnl / net_deposits * 100) if net_deposits > 0 else Decimal('0')
            pnl_color = "green" if total_pnl >= 0 else "red"

            pnl_md = f"""
### Profit/Loss

<span style="color: {pnl_color}; font-size: 24px; font-weight: bold;">
{format_monetary(total_pnl)} ({pnl_percentage:.2f}%)
</span>

{'🟢 Gain' if total_pnl >= 0 else '🔴 Loss'}
"""

            # Create holdings table
            holdings_data = []
            for holding in holdings:
                if holding.quantity > 0:
                    current_price = app_state.price_service.get_price(holding.symbol)
                    total_value_holding = Decimal(holding.quantity) * current_price
                    cost_basis = Decimal(holding.quantity) * holding.avg_cost_basis
                    gain_loss = total_value_holding - cost_basis

                    holdings_data.append([
                        holding.symbol,
                        holding.quantity,
                        format_monetary(holding.avg_cost_basis),
                        format_monetary(current_price),
                        format_monetary(total_value_holding),
                        format_monetary(gain_loss)
                    ])

            # Create allocation pie chart
            allocation_fig = None
            if holdings_data or cash_value > 0:
                import plotly.graph_objects as go

                labels = ["Cash"]
                values = [float(cash_value)]

                for holding in holdings:
                    if holding.quantity > 0:
                        current_price = app_state.price_service.get_price(holding.symbol)
                        total_value_holding = Decimal(holding.quantity) * current_price
                        labels.append(holding.symbol)
                        values.append(float(total_value_holding))

                allocation_fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    textinfo='label+percent',
                    textposition='auto'
                )])

                allocation_fig.update_layout(
                    title="Portfolio Allocation",
                    showlegend=True,
                    height=400
                )

            # Create P&L bar chart
            pnl_fig = None
            if holdings_data:
                import plotly.graph_objects as go

                symbols = []
                pnl_values = []

                for holding in holdings:
                    if holding.quantity > 0:
                        current_price = app_state.price_service.get_price(holding.symbol)
                        total_value_holding = Decimal(holding.quantity) * current_price
                        cost_basis = Decimal(holding.quantity) * holding.avg_cost_basis
                        gain_loss = total_value_holding - cost_basis

                        symbols.append(holding.symbol)
                        pnl_values.append(float(gain_loss))

                colors = ['green' if v >= 0 else 'red' for v in pnl_values]

                pnl_fig = go.Figure(data=[go.Bar(
                    x=symbols,
                    y=pnl_values,
                    marker_color=colors,
                    text=[format_monetary(Decimal(str(v))) for v in pnl_values],
                    textposition='auto'
                )])

                pnl_fig.update_layout(
                    title="Unrealized Gain/Loss by Stock",
                    xaxis_title="Symbol",
                    yaxis_title="Gain/Loss ($)",
                    showlegend=False,
                    height=400
                )

            return summary_md, pnl_md, holdings_data, allocation_fig, pnl_fig

        except Exception as e:
            return f"Error refreshing portfolio: {str(e)}", "", None, None, None

    # Connect event handlers
    refresh_btn.click(
        fn=refresh_portfolio,
        inputs=[],
        outputs=[summary_output, pnl_output, holdings_table, allocation_chart, pnl_chart]
    )

    # Return the refresh function for external use
    return refresh_portfolio
