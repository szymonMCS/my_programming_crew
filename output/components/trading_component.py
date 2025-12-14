"""
Trading component for stock buying and selling interface.

This module provides the Gradio UI components for trading stocks,
refactored into smaller, maintainable functions.
"""

import gradio as gr
from decimal import Decimal
from typing import Tuple
from app_state import app_state
from utils.helpers import format_monetary


def _get_current_price(symbol: str) -> str:
    """
    Get and format the current price for a stock symbol.

    Args:
        symbol: Stock symbol to get price for

    Returns:
        Formatted price string or error message
    """
    try:
        price = app_state.price_service.get_price(symbol)
        return f"**Current Price for {symbol}:** {format_monetary(price)} per share"
    except Exception as e:
        return f"Error getting price: {str(e)}"


def _check_holdings(symbol: str) -> str:
    """
    Check and display holdings information for a symbol.

    Args:
        symbol: Stock symbol to check holdings for

    Returns:
        Formatted holdings information or error message
    """
    try:
        if not app_state.current_account:
            return "Please login first"

        holdings = app_state.get_holdings()
        holding = next((h for h in holdings if h.symbol == symbol), None)

        if holding and holding.quantity > 0:
            current_price = app_state.price_service.get_price(symbol)
            current_value = Decimal(holding.quantity) * current_price
            cost_basis_total = Decimal(holding.quantity) * holding.avg_cost_basis
            gain_loss = current_value - cost_basis_total

            return f"""
**Your Holdings for {symbol}:**
- Quantity: {holding.quantity} shares
- Average Cost: {format_monetary(holding.avg_cost_basis)} per share
- Current Price: {format_monetary(current_price)} per share
- Total Cost Basis: {format_monetary(cost_basis_total)}
- Current Value: {format_monetary(current_value)}
- Unrealized Gain/Loss: {format_monetary(gain_loss)}
"""
        else:
            return f"**You don't own any {symbol} shares**"
    except Exception as e:
        return f"Error checking holdings: {str(e)}"


def _execute_buy(symbol: str, quantity: float) -> str:
    """
    Execute a stock purchase transaction.

    Args:
        symbol: Stock symbol to buy
        quantity: Number of shares to buy

    Returns:
        Transaction result message
    """
    try:
        if not app_state.current_account:
            return "Please login first to buy shares"

        if quantity is None or quantity < 1:
            return "Please enter a valid quantity (at least 1 share)"

        quantity = int(quantity)
        account = app_state.current_account
        trading_service = app_state.get_trading_service()

        if not trading_service:
            return "Error: Trading service not available"

        # Get price and calculate cost
        price_per_share = app_state.price_service.get_price(symbol)
        total_cost = price_per_share * quantity
        balance_before = account.cash_balance

        # Execute buy
        trading_service.buy_shares(symbol, quantity)
        balance_after = account.cash_balance

        return f"""
### Purchase Successful!

**Symbol:** {symbol}
**Quantity:** {quantity} shares
**Price per Share:** {format_monetary(price_per_share)}
**Total Cost:** {format_monetary(total_cost)}

**Balance Before:** {format_monetary(balance_before)}
**Balance After:** {format_monetary(balance_after)}

Your shares have been added to your portfolio!
"""
    except Exception as e:
        return f"Error buying shares: {str(e)}"


def _execute_sell(symbol: str, quantity: float) -> str:
    """
    Execute a stock sale transaction.

    Args:
        symbol: Stock symbol to sell
        quantity: Number of shares to sell

    Returns:
        Transaction result message
    """
    try:
        if not app_state.current_account:
            return "Please login first to sell shares"

        if quantity is None or quantity < 1:
            return "Please enter a valid quantity (at least 1 share)"

        quantity = int(quantity)
        account = app_state.current_account
        trading_service = app_state.get_trading_service()

        if not trading_service:
            return "Error: Trading service not available"

        # Get holding info
        holdings = app_state.get_holdings()
        holding = next((h for h in holdings if h.symbol == symbol), None)

        if not holding or holding.quantity < quantity:
            available = holding.quantity if holding else 0
            return f"Error: You don't have enough {symbol} shares. " \
                   f"You have {available} shares."

        # Get price and calculate revenue
        price_per_share = app_state.price_service.get_price(symbol)
        total_revenue = price_per_share * quantity
        balance_before = account.cash_balance
        cost_basis = holding.avg_cost_basis * quantity
        gain_loss = (price_per_share - holding.avg_cost_basis) * quantity

        # Execute sell
        trading_service.sell_shares(symbol, quantity)
        balance_after = account.cash_balance

        return f"""
### Sale Successful!

**Symbol:** {symbol}
**Quantity:** {quantity} shares
**Price per Share:** {format_monetary(price_per_share)}
**Total Revenue:** {format_monetary(total_revenue)}

**Cost Basis:** {format_monetary(cost_basis)}
**Realized Gain/Loss:** {format_monetary(gain_loss)}

**Balance Before:** {format_monetary(balance_before)}
**Balance After:** {format_monetary(balance_after)}

Your shares have been sold!
"""
    except Exception as e:
        return f"Error selling shares: {str(e)}"


def _update_balance_displays() -> Tuple[str, str]:
    """
    Get current balance display text for both buy and sell sections.

    Returns:
        Tuple of (buy_balance_text, sell_balance_text)
    """
    if app_state.current_account:
        balance = app_state.current_account.cash_balance
        text = f"**Cash Balance:** {format_monetary(balance)}"
        return text, text
    return ("**Cash Balance:** Please login first",
            "**Cash Balance:** Please login first")


def create_trading_component():
    """
    Create the stock trading component for buying and selling shares.

    This component is refactored to reduce complexity by splitting
    functionality into smaller, focused functions.
    """
    with gr.Column():
        gr.Markdown("## Stock Trading")

        with gr.Tabs():
            # Buy Section
            with gr.TabItem("Buy Shares"):
                (buy_balance, buy_symbol, buy_quantity, buy_price_display,
                 get_buy_price_btn, buy_btn, buy_output) = _create_buy_section()

            # Sell Section
            with gr.TabItem("Sell Shares"):
                (sell_balance, sell_symbol, sell_quantity, sell_price_display,
                 sell_holdings_display, check_holdings_btn, get_sell_price_btn,
                 sell_btn, sell_output) = _create_sell_section()

    # Wire up event handlers
    _setup_buy_handlers(buy_symbol, buy_quantity, buy_price_display,
                        get_buy_price_btn, buy_btn, buy_output,
                        buy_balance, sell_balance)
    _setup_sell_handlers(sell_symbol, sell_quantity, sell_price_display,
                         sell_holdings_display, check_holdings_btn,
                         get_sell_price_btn, sell_btn, sell_output,
                         buy_balance, sell_balance)

    return _update_balance_displays


def _create_buy_section() -> Tuple:
    """
    Create the buy shares UI section.

    Returns:
        Tuple of (balance_display, symbol_dropdown, quantity_input,
                 price_display, get_price_btn, buy_btn, output_display)
    """
    with gr.Column():
        gr.Markdown("### Buy Stock Shares")
        balance = gr.Markdown("**Cash Balance:** Please login first")

        symbol = gr.Dropdown(
            label="Stock Symbol",
            choices=["AAPL", "TSLA", "GOOGL"],
            value="AAPL"
        )

        quantity = gr.Number(
            label="Quantity",
            placeholder="Enter number of shares to buy",
            minimum=1,
            value=1,
            precision=0
        )

        price_display = gr.Markdown(
            "**Current Price:** Click 'Get Price' to see"
        )
        get_price_btn = gr.Button("Get Current Price")
        buy_btn = gr.Button("Buy Shares", variant="primary")
        output = gr.Markdown()

    return balance, symbol, quantity, price_display, get_price_btn, buy_btn, output


def _create_sell_section() -> Tuple:
    """
    Create the sell shares UI section.

    Returns:
        Tuple of UI components for the sell section
    """
    with gr.Column():
        gr.Markdown("### Sell Stock Shares")
        balance = gr.Markdown("**Cash Balance:** Please login first")

        symbol = gr.Dropdown(
            label="Stock Symbol",
            choices=["AAPL", "TSLA", "GOOGL"],
            value="AAPL"
        )

        holdings_display = gr.Markdown(
            "**Your Holdings:** Click 'Check Holdings' to see"
        )
        check_holdings_btn = gr.Button("Check Holdings")

        quantity = gr.Number(
            label="Quantity",
            placeholder="Enter number of shares to sell",
            minimum=1,
            value=1,
            precision=0
        )

        price_display = gr.Markdown(
            "**Current Price:** Click 'Get Price' to see"
        )
        get_price_btn = gr.Button("Get Current Price")
        sell_btn = gr.Button("Sell Shares", variant="primary")
        output = gr.Markdown()

    return (balance, symbol, quantity, price_display, holdings_display,
            check_holdings_btn, get_price_btn, sell_btn, output)


def _setup_buy_handlers(symbol, quantity, price_display, get_price_btn,
                        buy_btn, output, buy_balance, sell_balance):
    """Set up event handlers for buy section."""
    get_price_btn.click(
        fn=_get_current_price,
        inputs=symbol,
        outputs=price_display
    )

    buy_btn.click(
        fn=_execute_buy,
        inputs=[symbol, quantity],
        outputs=output
    ).then(
        fn=_update_balance_displays,
        inputs=[],
        outputs=[buy_balance, sell_balance]
    )


def _setup_sell_handlers(symbol, quantity, price_display, holdings_display,
                         check_holdings_btn, get_price_btn, sell_btn, output,
                         buy_balance, sell_balance):
    """Set up event handlers for sell section."""
    get_price_btn.click(
        fn=_get_current_price,
        inputs=symbol,
        outputs=price_display
    )

    check_holdings_btn.click(
        fn=_check_holdings,
        inputs=symbol,
        outputs=holdings_display
    )

    sell_btn.click(
        fn=_execute_sell,
        inputs=[symbol, quantity],
        outputs=output
    ).then(
        fn=_update_balance_displays,
        inputs=[],
        outputs=[buy_balance, sell_balance]
    )
