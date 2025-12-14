from decimal import Decimal
from typing import Dict, List
from account_core import Account
from trading_engine import Holding
from reporting_and_pricing import PriceService


class PortfolioValuator:
    """
    Calculates the total value of a portfolio by summing cash and the current market value of all holdings.
    """

    def __init__(self, account: Account, holdings: List[Holding], price_service: PriceService) -> None:
        self.account = account
        self.holdings = holdings
        self.price_service = price_service

    def calculate_total_value(self) -> Decimal:
        """
        Calculates the total value of the portfolio.

        Returns:
            Decimal: The total portfolio value.
        """
        total_value = self.calculate_cash_value() + self.calculate_holding_value()
        return total_value

    def calculate_holding_value(self) -> Decimal:
        """
        Calculates the total market value of all holdings.

        Returns:
            Decimal: The total market value of holdings.
        """
        total_holding_value = Decimal('0.00')
        for holding in self.holdings:
            try:
                price = self.price_service.get_price(holding.symbol)
                total_holding_value += Decimal(holding.quantity) * price
            except Exception as e:
                # Log the error and continue with the next holding
                print(f"Error fetching price for {holding.symbol}: {e}")
        return total_holding_value

    def calculate_cash_value(self) -> Decimal:
        """
        Returns the cash value available in the account.

        Returns:
            Decimal: The current cash balance in the account.
        """
        return self.account.cash_balance

    def get_all_holding_values(self) -> Dict[str, Decimal]:
        """
        Provides a breakdown of the market value for each holding.

        Returns:
            Dict[str, Decimal]: A dictionary mapping each symbol to its market value.
        """
        holding_values = {}
        for holding in self.holdings:
            try:
                price = self.price_service.get_price(holding.symbol)
                holding_values[holding.symbol] = Decimal(holding.quantity) * price
            except Exception as e:
                # Log the error and continue with the next holding
                print(f"Error fetching price for {holding.symbol}: {e}")
        return holding_values


class ProfitLossCalculator:
    """
    Computes realized and unrealized profit/loss relative to cumulative net deposits.
    """

    def __init__(self, account: Account, portfolio_valuator: PortfolioValuator) -> None:
        self.account = account
        self.portfolio_valuator = portfolio_valuator

    def calculate_total_pnl(self) -> Decimal:
        """
        Calculates the total profit and loss of the account.

        Returns:
            Decimal: The total profit/loss value.
        """
        portfolio_value = self.portfolio_valuator.calculate_total_value()
        cumulative_net_deposits = self.calculate_cumulative_net_deposits()
        total_pnl = portfolio_value - cumulative_net_deposits
        return total_pnl

    def calculate_realized_pnl(self) -> Decimal:
        """
        Calculates the realized profit/loss, excluding current holdings.

        Returns:
            Decimal: The realized profit/loss.
        """
        # Assume realized P&L is tracked in transactions and is placeholder here
        return Decimal('0.00')  # Placeholder for actual transaction-driven realized P&L calculation

    def calculate_unrealized_pnl(self) -> Decimal:
        """
        Calculates the unrealized profit/loss based on current holdings.

        Returns:
            Decimal: The unrealized profit/loss.
        """
        total_value = self.portfolio_valuator.calculate_holding_value()
        realized_pnl = self.calculate_realized_pnl()
        unrealized_pnl = total_value - realized_pnl
        return unrealized_pnl

    def calculate_cumulative_net_deposits(self) -> Decimal:
        """
        Computes cumulative net deposits as total deposits minus total withdrawals.

        Returns:
            Decimal: The cumulative net deposits.
        """
        return self.account.total_deposits - self.account.total_withdrawals