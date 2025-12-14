import gradio as gr
from decimal import Decimal
from app_state import app_state
from utils.helpers import format_monetary


def create_funds_component():
    """Create the funds management component for deposits and withdrawals."""

    with gr.Column():
        gr.Markdown("## Funds Management")

        with gr.Tabs():
            with gr.TabItem("Deposit"):
                with gr.Column():
                    current_balance_deposit = gr.Markdown("**Current Balance:** Please login first")
                    deposit_amount = gr.Number(
                        label="Deposit Amount",
                        placeholder="Enter amount to deposit (min $1.00)",
                        minimum=1.00,
                        value=100.00
                    )
                    deposit_btn = gr.Button("Deposit Funds", variant="primary")
                    deposit_output = gr.Markdown()

            with gr.TabItem("Withdraw"):
                with gr.Column():
                    current_balance_withdraw = gr.Markdown("**Current Balance:** Please login first")
                    withdraw_amount = gr.Number(
                        label="Withdrawal Amount",
                        placeholder="Enter amount to withdraw",
                        minimum=0.01,
                        value=50.00
                    )
                    withdraw_btn = gr.Button("Withdraw Funds", variant="primary")
                    withdraw_output = gr.Markdown()

    def deposit_funds(amount):
        try:
            if not app_state.current_account:
                return "Please login first to deposit funds"

            if amount is None or amount <= 0:
                return "Please enter a valid deposit amount"

            account = app_state.current_account
            balance_before = account.cash_balance

            # Perform deposit
            transaction_id = app_state.funds_service.deposit(account, Decimal(str(amount)))

            balance_after = account.cash_balance

            return f"""
### Deposit Successful!

**Transaction ID:** {transaction_id}
**Amount Deposited:** {format_monetary(Decimal(str(amount)))}
**Balance Before:** {format_monetary(balance_before)}
**Balance After:** {format_monetary(balance_after)}
**Total Deposits:** {format_monetary(account.total_deposits)}

Your funds have been added to your account.
"""
        except Exception as e:
            return f"Error processing deposit: {str(e)}"

    def withdraw_funds(amount):
        try:
            if not app_state.current_account:
                return "Please login first to withdraw funds"

            if amount is None or amount <= 0:
                return "Please enter a valid withdrawal amount"

            account = app_state.current_account
            balance_before = account.cash_balance

            # Perform withdrawal
            transaction_id = app_state.funds_service.withdraw(account, Decimal(str(amount)))

            balance_after = account.cash_balance

            return f"""
### Withdrawal Successful!

**Transaction ID:** {transaction_id}
**Amount Withdrawn:** {format_monetary(Decimal(str(amount)))}
**Balance Before:** {format_monetary(balance_before)}
**Balance After:** {format_monetary(balance_after)}
**Total Withdrawals:** {format_monetary(account.total_withdrawals)}

Your funds have been withdrawn from your account.
"""
        except Exception as e:
            return f"Error processing withdrawal: {str(e)}"

    def update_balance_display():
        if app_state.current_account:
            balance_text = f"**Current Balance:** {format_monetary(app_state.current_account.cash_balance)}"
            return balance_text, balance_text
        return "**Current Balance:** Please login first", "**Current Balance:** Please login first"

    # Connect event handlers
    deposit_btn.click(
        fn=deposit_funds,
        inputs=deposit_amount,
        outputs=deposit_output
    ).then(
        fn=update_balance_display,
        inputs=[],
        outputs=[current_balance_deposit, current_balance_withdraw]
    )

    withdraw_btn.click(
        fn=withdraw_funds,
        inputs=withdraw_amount,
        outputs=withdraw_output
    ).then(
        fn=update_balance_display,
        inputs=[],
        outputs=[current_balance_deposit, current_balance_withdraw]
    )

    # Update balance on component load
    def load_balances():
        return update_balance_display()

    # Return the update function for external use
    return load_balances
