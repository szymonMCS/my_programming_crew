from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from transaction_core import Transaction, TransactionType, TransactionStatus

class Holding:
    def __init__(self, account_id: str, symbol: str, quantity: int, avg_cost_basis: Decimal):
        self.account_id = account_id
        self.symbol = symbol
        self.quantity = quantity
        self.avg_cost_basis = avg_cost_basis
        self.last_updated = datetime.utcnow()

    def validate(self) -> None:
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if self.avg_cost_basis < Decimal('0.00'):
            raise ValueError("Average cost basis cannot be negative")

    def can_sell(self, quantity: int) -> bool:
        return self.quantity >= quantity

    def add_shares(self, quantity: int, price_per_share: Decimal) -> None:
        total_cost = self.quantity * self.avg_cost_basis + quantity * price_per_share
        self.quantity += quantity
        self.update_average_cost(quantity, total_cost)

    def remove_shares(self, quantity: int) -> None:
        if quantity > self.quantity:
            raise ValueError("Not enough shares to sell")
        self.quantity -= quantity

    def update_average_cost(self, new_shares: int, total_cost: Decimal) -> None:
        self.avg_cost_basis = total_cost / (self.quantity + new_shares)
        self.last_updated = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'account_id': self.account_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_cost_basis': self.avg_cost_basis,
            'last_updated': self.last_updated
        }

class TradingService:
    def __init__(self, account, holdings_repo, transactions_repo, price_service, trading_validator):
        self.account = account
        self.holdings_repo = holdings_repo
        self.transactions_repo = transactions_repo
        self.price_service = price_service
        self.trading_validator = trading_validator

    def buy_shares(self, symbol: str, quantity: int) -> None:
        try:
            self.trading_validator.validate_buy(symbol, quantity)
            self._create_buy_transaction(symbol, quantity)
        except Exception as e:
            # log the exception, handle rollback if necessary
            raise

    def sell_shares(self, symbol: str, quantity: int) -> None:
        try:
            self.trading_validator.validate_sell(symbol, quantity)
            self._create_sell_transaction(symbol, quantity)
        except Exception as e:
            # log the exception, handle rollback if necessary
            raise

    def get_holdings(self) -> Dict[str, Any]:
        # return holdings for the account
        pass

    def _create_buy_transaction(self, symbol: str, quantity: int) -> None:
        price_per_share = self.price_service.get_price(symbol)
        total_cost = price_per_share * quantity
        self._update_account_balance(-total_cost)
        self._update_holdings(symbol, quantity, price_per_share)

        # Create and save transaction record
        transaction = Transaction(
            account_id=self.account.account_id,
            transaction_type=TransactionType.BUY,
            total_amount=total_cost,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            status=TransactionStatus.COMPLETED
        )
        self.transactions_repo.save(transaction)

    def _create_sell_transaction(self, symbol: str, quantity: int) -> None:
        price_per_share = self.price_service.get_price(symbol)
        total_revenue = price_per_share * quantity
        self._update_account_balance(total_revenue)
        self._update_holdings(symbol, -quantity, price_per_share)

        # Create and save transaction record
        transaction = Transaction(
            account_id=self.account.account_id,
            transaction_type=TransactionType.SELL,
            total_amount=total_revenue,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            status=TransactionStatus.COMPLETED
        )
        self.transactions_repo.save(transaction)

    def _update_holdings(self, symbol: str, quantity: int, price_per_share: Decimal) -> None:
        holding = self.holdings_repo.find_by_symbol(symbol)
        if not holding:
            # buying new shares
            holding = Holding(self.account.account_id, symbol, 0, Decimal('0.00'))
        if quantity > 0:
            holding.add_shares(quantity, price_per_share)
        else:
            holding.remove_shares(-quantity)
        self.holdings_repo.save(holding)

    def _update_account_balance(self, amount: Decimal) -> None:
        self.account.update_balance(amount)
        # save account changes to repository

class TradingValidator:
    def __init__(self, account, holdings_repo, price_service):
        self.account = account
        self.holdings_repo = holdings_repo
        self.price_service = price_service

    def validate_buy(self, symbol: str, quantity: int) -> None:
        self._validate_symbol(symbol)
        self._validate_affordability(symbol, quantity)

    def validate_sell(self, symbol: str, quantity: int) -> None:
        self._validate_symbol(symbol)
        self._validate_share_availability(symbol, quantity)

    def _validate_symbol(self, symbol: str) -> None:
        if symbol not in ['AAPL', 'TSLA', 'GOOGL']:
            raise ValueError(f"Unsupported symbol: {symbol}")

    def _validate_affordability(self, symbol: str, quantity: int) -> None:
        price_per_share = self.price_service.get_price(symbol)
        total_cost = price_per_share * quantity
        if total_cost > self.account.cash_balance:
            raise ValueError(f"Insufficient funds to buy {quantity} shares of {symbol}")

    def _validate_share_availability(self, symbol: str, quantity: int) -> None:
        holding = self.holdings_repo.find_by_symbol(symbol)
        if not holding or holding.quantity < quantity:
            raise ValueError(f"Not enough shares to sell: {symbol}")
