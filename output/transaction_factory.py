"""
Transaction Factory - Factory Pattern implementation for creating transactions.

This module provides a centralized way to create different types of transactions
with proper validation and consistent initialization.
"""

from decimal import Decimal
from uuid import UUID
from typing import Optional

from transaction_core import Transaction, TransactionType, TransactionStatus


class TransactionFactory:
    """
    Factory class for creating transaction objects.

    Implements the Factory Pattern to encapsulate transaction creation logic
    and ensure all transactions are created with proper validation.
    """

    @staticmethod
    def create_deposit(
        account_id: UUID,
        amount: Decimal,
        status: TransactionStatus = TransactionStatus.COMPLETED
    ) -> Transaction:
        """
        Create a deposit transaction.

        Args:
            account_id: ID of the account receiving the deposit
            amount: Amount being deposited
            status: Initial status of the transaction

        Returns:
            A new deposit Transaction instance

        Raises:
            ValueError: If amount is non-positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        return Transaction(
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            total_amount=amount,
            status=status
        )

    @staticmethod
    def create_withdrawal(
        account_id: UUID,
        amount: Decimal,
        status: TransactionStatus = TransactionStatus.COMPLETED
    ) -> Transaction:
        """
        Create a withdrawal transaction.

        Args:
            account_id: ID of the account from which to withdraw
            amount: Amount being withdrawn
            status: Initial status of the transaction

        Returns:
            A new withdrawal Transaction instance

        Raises:
            ValueError: If amount is non-positive
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        return Transaction(
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            total_amount=amount,
            status=status
        )

    @staticmethod
    def create_buy(
        account_id: UUID,
        symbol: str,
        quantity: int,
        price_per_share: Decimal,
        status: TransactionStatus = TransactionStatus.COMPLETED
    ) -> Transaction:
        """
        Create a buy (purchase) transaction for stocks.

        Args:
            account_id: ID of the account making the purchase
            symbol: Stock symbol being purchased
            quantity: Number of shares being purchased
            price_per_share: Price per share at time of purchase
            status: Initial status of the transaction

        Returns:
            A new buy Transaction instance

        Raises:
            ValueError: If quantity is non-positive or price is non-positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price_per_share <= 0:
            raise ValueError("Price per share must be positive")

        total_amount = price_per_share * quantity

        return Transaction(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            total_amount=total_amount,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            status=status
        )

    @staticmethod
    def create_sell(
        account_id: UUID,
        symbol: str,
        quantity: int,
        price_per_share: Decimal,
        status: TransactionStatus = TransactionStatus.COMPLETED
    ) -> Transaction:
        """
        Create a sell transaction for stocks.

        Args:
            account_id: ID of the account making the sale
            symbol: Stock symbol being sold
            quantity: Number of shares being sold
            price_per_share: Price per share at time of sale
            status: Initial status of the transaction

        Returns:
            A new sell Transaction instance

        Raises:
            ValueError: If quantity is non-positive or price is non-positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price_per_share <= 0:
            raise ValueError("Price per share must be positive")

        total_amount = price_per_share * quantity

        return Transaction(
            account_id=account_id,
            transaction_type=TransactionType.SELL,
            total_amount=total_amount,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            status=status
        )

    @staticmethod
    def create_failed_transaction(
        account_id: UUID,
        transaction_type: TransactionType,
        amount: Decimal,
        failure_reason: str,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price_per_share: Optional[Decimal] = None
    ) -> Transaction:
        """
        Create a failed transaction for auditing purposes.

        Args:
            account_id: ID of the account
            transaction_type: Type of transaction that failed
            amount: Amount involved in the failed transaction
            failure_reason: Reason why the transaction failed
            symbol: Stock symbol (for buy/sell transactions)
            quantity: Number of shares (for buy/sell transactions)
            price_per_share: Price per share (for buy/sell transactions)

        Returns:
            A new failed Transaction instance
        """
        return Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            total_amount=amount,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            status=TransactionStatus.FAILED,
            failure_reason=failure_reason
        )
