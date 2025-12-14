import gradio as gr
from app_state import app_state
from utils.helpers import format_monetary


def create_transaction_history_component():
    """Create the transaction history component."""

    with gr.Column():
        gr.Markdown("## Transaction History")

        refresh_btn = gr.Button("Refresh Transaction History", variant="primary")

        with gr.Row():
            with gr.Column():
                transaction_count = gr.Markdown()

        with gr.Row():
            transaction_table = gr.Dataframe(
                headers=["Date/Time", "Type", "Symbol", "Quantity", "Price", "Amount", "Status"],
                datatype=["str", "str", "str", "str", "str", "str", "str"],
                row_count=20
            )

    def refresh_transaction_history():
        try:
            if not app_state.current_account:
                return "Please login first to view transaction history", None

            transactions = app_state.get_transaction_history()

            if not transactions:
                return "**Total Transactions:** 0\n\nNo transactions yet. Start by depositing funds!", []

            # Create transaction table data
            transaction_data = []
            for txn in transactions:
                timestamp = txn.transaction_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                txn_type = txn.transaction_type.value
                symbol = txn.symbol or "-"
                quantity = str(txn.quantity) if txn.quantity else "-"
                price = format_monetary(txn.price_per_share) if txn.price_per_share else "-"
                amount = format_monetary(txn.total_amount)
                status = txn.status.value

                transaction_data.append([
                    timestamp,
                    txn_type,
                    symbol,
                    quantity,
                    price,
                    amount,
                    status
                ])

            # Create summary
            count_md = f"""
**Total Transactions:** {len(transactions)}

**Transaction Types:**
- Deposits: {sum(1 for t in transactions if t.transaction_type.value == 'DEPOSIT')}
- Withdrawals: {sum(1 for t in transactions if t.transaction_type.value == 'WITHDRAWAL')}
- Buys: {sum(1 for t in transactions if t.transaction_type.value == 'BUY')}
- Sells: {sum(1 for t in transactions if t.transaction_type.value == 'SELL')}
"""

            return count_md, transaction_data

        except Exception as e:
            return f"Error retrieving transaction history: {str(e)}", None

    # Connect event handlers
    refresh_btn.click(
        fn=refresh_transaction_history,
        inputs=[],
        outputs=[transaction_count, transaction_table]
    )

    # Return the refresh function for external use
    return refresh_transaction_history
