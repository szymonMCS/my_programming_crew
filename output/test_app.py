"""
Test script for the Trading Simulation Platform
Tests all major functionalities without launching the UI
"""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from decimal import Decimal
from app_state import app_state
from transaction_core import TransactionType

def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")


def test_account_creation():
    """Test user and account creation"""
    print_separator("TEST 1: Account Creation")

    try:
        user = app_state.create_user("john_trader", "john@example.com")
        print(f"✓ Created user: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Status: {user.status.value}")

        # Login
        success = app_state.login_user("john_trader")
        assert success, "Login should succeed"
        print(f"✓ Logged in successfully")

        account = app_state.get_current_account()
        assert account is not None, "Account should exist"
        print(f"✓ Account ID: {account.account_id}")
        print(f"  Initial Balance: ${account.cash_balance}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_deposit_and_withdrawal():
    """Test deposit and withdrawal operations"""
    print_separator("TEST 2: Deposits and Withdrawals")

    try:
        account = app_state.get_current_account()

        # Test deposit
        print("\n→ Depositing $1,000.00...")
        txn_id = app_state.funds_service.deposit(account, Decimal('1000.00'))
        print(f"✓ Deposit successful! Transaction ID: {txn_id}")
        print(f"  New Balance: ${account.cash_balance}")

        # Another deposit
        print("\n→ Depositing $500.00...")
        txn_id = app_state.funds_service.deposit(account, Decimal('500.00'))
        print(f"✓ Deposit successful! Transaction ID: {txn_id}")
        print(f"  New Balance: ${account.cash_balance}")

        # Test withdrawal
        print("\n→ Withdrawing $300.00...")
        txn_id = app_state.funds_service.withdraw(account, Decimal('300.00'))
        print(f"✓ Withdrawal successful! Transaction ID: {txn_id}")
        print(f"  New Balance: ${account.cash_balance}")

        print(f"\n✓ Final Balance: ${account.cash_balance}")
        print(f"  Total Deposits: ${account.total_deposits}")
        print(f"  Total Withdrawals: ${account.total_withdrawals}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_stock_trading():
    """Test stock buying and selling"""
    print_separator("TEST 3: Stock Trading")

    try:
        trading_service = app_state.get_trading_service()
        account = app_state.get_current_account()

        # Get initial prices
        print("\n→ Current stock prices:")
        for symbol in ['AAPL', 'TSLA', 'GOOGL']:
            price = app_state.price_service.get_price(symbol)
            print(f"  {symbol}: ${price}")

        # Buy AAPL
        print(f"\n→ Buying 5 shares of AAPL...")
        print(f"  Balance before: ${account.cash_balance}")
        trading_service.buy_shares('AAPL', 5)
        print(f"✓ Purchase successful!")
        print(f"  Balance after: ${account.cash_balance}")

        # Buy TSLA (only 1 share since we don't have enough for 2)
        print(f"\n→ Buying 1 share of TSLA...")
        print(f"  Balance before: ${account.cash_balance}")
        if account.cash_balance >= app_state.price_service.get_price('TSLA'):
            trading_service.buy_shares('TSLA', 1)
            print(f"✓ Purchase successful!")
            print(f"  Balance after: ${account.cash_balance}")
        else:
            print(f"✗ Not enough funds for TSLA")

        # Check holdings
        print("\n→ Current holdings:")
        holdings = app_state.get_holdings()
        for holding in holdings:
            if holding.quantity > 0:
                print(f"  {holding.symbol}: {holding.quantity} shares @ ${holding.avg_cost_basis}")

        # Sell some AAPL
        print(f"\n→ Selling 2 shares of AAPL...")
        print(f"  Balance before: ${account.cash_balance}")
        trading_service.sell_shares('AAPL', 2)
        print(f"✓ Sale successful!")
        print(f"  Balance after: ${account.cash_balance}")

        # Check holdings after sale
        print("\n→ Holdings after sale:")
        holdings = app_state.get_holdings()
        for holding in holdings:
            if holding.quantity > 0:
                print(f"  {holding.symbol}: {holding.quantity} shares @ ${holding.avg_cost_basis}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_portfolio_valuation():
    """Test portfolio valuation and P&L calculations"""
    print_separator("TEST 4: Portfolio Valuation")

    try:
        account = app_state.get_current_account()
        valuator = app_state.get_portfolio_valuator()
        pnl_calc = app_state.get_profit_loss_calculator()

        if not valuator or not pnl_calc:
            print("✗ Valuator or P&L calculator not available")
            return False

        # Calculate values
        cash_value = valuator.calculate_cash_value()
        holdings_value = valuator.calculate_holding_value()
        total_value = valuator.calculate_total_value()

        print(f"\n→ Portfolio Summary:")
        print(f"  Cash Balance: ${cash_value}")
        print(f"  Holdings Value: ${holdings_value}")
        print(f"  Total Portfolio Value: ${total_value}")

        # P&L
        net_deposits = pnl_calc.calculate_cumulative_net_deposits()
        total_pnl = pnl_calc.calculate_total_pnl()

        print(f"\n→ Profit/Loss:")
        print(f"  Net Deposits: ${net_deposits}")
        print(f"  Total P&L: ${total_pnl}")
        pnl_percentage = (total_pnl / net_deposits * 100) if net_deposits > 0 else Decimal('0')
        print(f"  P&L Percentage: {pnl_percentage:.2f}%")

        # Holdings breakdown
        print(f"\n→ Holdings Breakdown:")
        holdings = app_state.get_holdings()
        for holding in holdings:
            if holding.quantity > 0:
                current_price = app_state.price_service.get_price(holding.symbol)
                value = Decimal(holding.quantity) * current_price
                cost = Decimal(holding.quantity) * holding.avg_cost_basis
                gain_loss = value - cost
                print(f"  {holding.symbol}:")
                print(f"    Quantity: {holding.quantity} shares")
                print(f"    Avg Cost: ${holding.avg_cost_basis}/share")
                print(f"    Current Price: ${current_price}/share")
                print(f"    Total Value: ${value}")
                print(f"    Gain/Loss: ${gain_loss}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_transaction_history():
    """Test transaction history retrieval"""
    print_separator("TEST 5: Transaction History")

    try:
        transactions = app_state.get_transaction_history()

        print(f"\n→ Total Transactions: {len(transactions)}")

        # Count by type
        deposits = sum(1 for t in transactions if t.transaction_type == TransactionType.DEPOSIT)
        withdrawals = sum(1 for t in transactions if t.transaction_type == TransactionType.WITHDRAWAL)
        buys = sum(1 for t in transactions if t.transaction_type == TransactionType.BUY)
        sells = sum(1 for t in transactions if t.transaction_type == TransactionType.SELL)

        print(f"  Deposits: {deposits}")
        print(f"  Withdrawals: {withdrawals}")
        print(f"  Buys: {buys}")
        print(f"  Sells: {sells}")

        print("\n→ Recent Transactions (last 5):")
        for i, txn in enumerate(transactions[:5]):
            timestamp = txn.transaction_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            txn_type = txn.transaction_type.value
            amount = txn.total_amount
            symbol = f" {txn.symbol}" if txn.symbol else ""
            print(f"  {i+1}. [{timestamp}] {txn_type}{symbol} - ${amount}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  TRADING SIMULATION PLATFORM - COMPREHENSIVE TEST")
    print("="*60)

    results = []

    results.append(("Account Creation", test_account_creation()))
    results.append(("Deposits & Withdrawals", test_deposit_and_withdrawal()))
    results.append(("Stock Trading", test_stock_trading()))
    results.append(("Portfolio Valuation", test_portfolio_valuation()))
    results.append(("Transaction History", test_transaction_history()))

    print_separator("TEST RESULTS")
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All tests passed successfully!")
    else:
        print("\n✗ Some tests failed. Please review the errors above.")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
