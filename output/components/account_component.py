import gradio as gr
from app_state import app_state
from utils.helpers import format_monetary


def create_account_component():
    """Create the account management component."""

    with gr.Column():
        gr.Markdown("## Account Management")

        with gr.Tabs():
            with gr.TabItem("Create Account"):
                with gr.Column():
                    username_create = gr.Textbox(
                        label="Username",
                        placeholder="Enter username"
                    )
                    email_create = gr.Textbox(
                        label="Email",
                        placeholder="Enter email"
                    )
                    create_btn = gr.Button("Create Account", variant="primary")
                    create_output = gr.Markdown()

            with gr.TabItem("Login"):
                with gr.Column():
                    username_login = gr.Textbox(
                        label="Username",
                        placeholder="Enter username to login"
                    )
                    login_btn = gr.Button("Login", variant="primary")
                    login_output = gr.Markdown()

            with gr.TabItem("Account Info"):
                with gr.Column():
                    refresh_info_btn = gr.Button("Refresh Account Info")
                    account_info_output = gr.Markdown()

    def create_account(username, email):
        try:
            if not username or not email:
                return "Please provide both username and email"

            user = app_state.create_user(username, email)
            app_state.login_user(username)

            return f"""
### Account Created Successfully!

**User ID:** {user.user_id}
**Username:** {user.username}
**Email:** {user.email}
**Status:** {user.status.value}
**Created At:** {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}

You are now logged in. You can start using the platform!
"""
        except Exception as e:
            return f"Error creating account: {str(e)}"

    def login(username):
        try:
            if not username:
                return "Please provide a username"

            success = app_state.login_user(username)

            if success:
                account = app_state.get_current_account()
                return f"""
### Login Successful!

**Username:** {app_state.current_user.username}
**Account ID:** {account.account_id}
**Cash Balance:** {format_monetary(account.cash_balance)}
"""
            else:
                return f"User '{username}' not found. Please create an account first."
        except Exception as e:
            return f"Error logging in: {str(e)}"

    def refresh_account_info():
        try:
            if not app_state.current_user or not app_state.current_account:
                return "Please login first to view account information"

            user = app_state.current_user
            account = app_state.current_account

            return f"""
### Account Information

#### User Details
- **Username:** {user.username}
- **Email:** {user.email}
- **User ID:** {user.user_id}
- **Status:** {user.status.value}
- **Active:** {'Yes' if user.is_active() else 'No'}
- **Created:** {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}

#### Account Details
- **Account ID:** {account.account_id}
- **Cash Balance:** {format_monetary(account.cash_balance)}
- **Total Deposits:** {format_monetary(account.total_deposits)}
- **Total Withdrawals:** {format_monetary(account.total_withdrawals)}
- **Net Deposits:** {format_monetary(account.total_deposits - account.total_withdrawals)}
- **Created:** {account.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
        except Exception as e:
            return f"Error retrieving account info: {str(e)}"

    # Connect event handlers
    create_btn.click(
        fn=create_account,
        inputs=[username_create, email_create],
        outputs=create_output
    )

    login_btn.click(
        fn=login,
        inputs=username_login,
        outputs=login_output
    )

    refresh_info_btn.click(
        fn=refresh_account_info,
        inputs=[],
        outputs=account_info_output
    )
