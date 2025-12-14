import gradio as gr
from components.account_component import create_account_component
from components.funds_component import create_funds_component
from components.trading_component import create_trading_component
from components.portfolio_component import create_portfolio_component
from components.transaction_history_component import create_transaction_history_component


def create_app():
    """Create and return the Gradio app interface."""
    with gr.Blocks(title="Trading Simulation Platform") as demo:
        gr.Markdown("""
        # Trading Simulation Platform
        ### Complete Stock Trading & Portfolio Management System

        Welcome! This platform allows you to:
        - Create and manage trading accounts
        - Deposit and withdraw funds
        - Buy and sell stocks (AAPL, TSLA, GOOGL)
        - Track your portfolio value and holdings
        - View transaction history
        - Analyze profit/loss with charts
        """)

        with gr.Tabs():
            with gr.TabItem("Account Management"):
                create_account_component()

            with gr.TabItem("Funds (Deposit/Withdraw)"):
                create_funds_component()

            with gr.TabItem("Stock Trading"):
                create_trading_component()

            with gr.TabItem("Portfolio Summary"):
                create_portfolio_component()

            with gr.TabItem("Transaction History"):
                create_transaction_history_component()

        gr.Markdown("""
        ---
        ### Quick Start Guide:
        1. **Create Account**: Go to "Account Management" > "Create Account" to create your account
        2. **Deposit Funds**: Go to "Funds" > "Deposit" to add money to your account
        3. **Trade Stocks**: Go to "Stock Trading" to buy or sell shares
        4. **View Portfolio**: Check "Portfolio Summary" to see your holdings and profit/loss
        5. **Check History**: View all your transactions in "Transaction History"
        """)

    return demo


def main():
    """Main entry point for the application."""
    demo = create_app()
    demo.launch()


if __name__ == "__main__":
    main()
