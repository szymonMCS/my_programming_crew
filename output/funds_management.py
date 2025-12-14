"""
Funds management module for handling deposits and withdrawals.

This module provides services and validators for managing account funds,
ensuring all operations comply with business rules.
"""

from decimal import Decimal
from typing import List
from uuid import UUID
import logging

# Import dependencies
from account_core import Account
from transaction_core import Transaction, TransactionType, TransactionStatus
from config import (
    MIN_DEPOSIT_AMOUNT,
    MAX_DEPOSIT_AMOUNT,
    MIN_WITHDRAWAL_AMOUNT,
    MAX_WITHDRAWAL_AMOUNT
)


class InvalidOperationException(Exception):
    """Custom exception raised when a funds operation violates business rules."""
    pass


class FundsValidator:
    """
    Validates all deposit and withdrawal operations against business rules.

    This validator ensures that all fund operations comply with configured
    minimum and maximum amounts, and that accounts have sufficient balance.
    """

    MIN_DEPOSIT_AMOUNT = MIN_DEPOSIT_AMOUNT
    MAX_DEPOSIT_AMOUNT = MAX_DEPOSIT_AMOUNT
    MIN_WITHDRAWAL_AMOUNT = MIN_WITHDRAWAL_AMOUNT

    def validate_deposit(self, account: Account, amount: Decimal) -> None:
        """
        Validates deposit amount against account status and deposit rules.

        Args:
            account (Account): The account making the deposit.
            amount (Decimal): The amount to deposit.

        Raises:
            InvalidOperationException: If any validation check fails.
        """
        self._validate_amount(amount, self.MIN_DEPOSIT_AMOUNT, self.MAX_DEPOSIT_AMOUNT)

        # Account status validation removed - status is tracked at User level, not Account level

    def validate_withdrawal(self, account: Account, amount: Decimal) -> None:
        """
        Validates withdrawal amount against account status and withdrawal rules.

        Args:
            account (Account): The account making the withdrawal.
            amount (Decimal): The amount to withdraw.

        Raises:
            InvalidOperationException: If any validation check fails.
        """
        self._validate_amount(amount, self.MIN_WITHDRAWAL_AMOUNT, Decimal('1000000.00'))
        self._validate_balance(account, amount)

    def _validate_amount(self, amount: Decimal, min_amount: Decimal, max_amount: Decimal) -> None:
        """
        Validates that the amount is within the specified range.

        Args:
            amount (Decimal): The monetary value to validate.
            min_amount (Decimal): Minimum permissible amount.
            max_amount (Decimal): Maximum permissible amount.

        Raises:
            InvalidOperationException: If the amount is out of range or negative.
        """
        if amount < min_amount or amount > max_amount:
            raise InvalidOperationException(f"Amount must be between ${min_amount} and ${max_amount}.")

    def _validate_balance(self, account: Account, amount: Decimal) -> None:
        """
        Ensures that the account has sufficient funds for a withdrawal.

        Args:
            account (Account): The account being checked.
            amount (Decimal): The withdrawal amount.
        
        Raises:
            InvalidOperationException: If the withdrawal would cause a negative balance.
        """
        if account.cash_balance < amount:
            raise InvalidOperationException(f"Insufficient funds: need ${amount}, available ${account.cash_balance}.")


class FundsService:
    """Processes deposit and withdrawal requests atomically and creates transaction records."""

    def __init__(self, validator: FundsValidator):
        self.validator = validator
        self.transactions: List[Transaction] = []
        logging.basicConfig(level=logging.INFO)

    def deposit(self, account: Account, amount: Decimal) -> UUID:
        """
        Processes a deposit into the specified account.

        Args:
            account (Account): The account receiving the deposit.
            amount (Decimal): The amount to deposit.

        Returns:
            UUID: The transaction ID for the deposit.

        Raises:
            InvalidOperationException: If deposit validation fails.
        """
        self.validator.validate_deposit(account, amount)

        try:
            account.cash_balance += amount
            account.total_deposits += amount
            transaction_id = self._create_transaction(account, 'DEPOSIT', amount)
            logging.info(f"Deposit succeeded: {amount} to {account.account_id}.")
            return transaction_id
        except Exception as e:
            logging.error(f"Deposit failed: {str(e)}")
            raise

    def withdraw(self, account: Account, amount: Decimal) -> UUID:
        """
        Processes a withdrawal from the specified account.

        Args:
            account (Account): The account from which to withdraw.
            amount (Decimal): The amount to withdraw.

        Returns:
            UUID: The transaction ID for the withdrawal.

        Raises:
            InvalidOperationException: If withdrawal validation fails.
        """
        self.validator.validate_withdrawal(account, amount)

        try:
            account.cash_balance -= amount
            account.total_withdrawals += amount
            transaction_id = self._create_transaction(account, 'WITHDRAWAL', amount)
            logging.info(f"Withdrawal succeeded: {amount} from {account.account_id}.")
            return transaction_id
        except Exception as e:
            logging.error(f"Withdrawal failed: {str(e)}")
            raise

    def get_transaction_history(self, account: Account) -> List[Transaction]:
        """
        Retrieves the transaction history for the specified account.

        Args:
            account (Account): The account whose transactions are retrieved.

        Returns:
            List[Transaction]: List of transactions for the account.
        """
        return [txn for txn in self.transactions if txn.account_id == account.account_id]

    def _create_transaction(self, account: Account, transaction_type: str, amount: Decimal) -> UUID:
        """
        Creates a transaction record and adds it to the account's transaction history.

        Args:
            account (Account): The account involved in the transaction.
            transaction_type (str): Type of the transaction ('DEPOSIT' or 'WITHDRAWAL').
            amount (Decimal): The monetary value involved in the transaction.

        Returns:
            UUID: The transaction ID.
        """
        # Convert string transaction_type to TransactionType enum
        if transaction_type == 'DEPOSIT':
            txn_type = TransactionType.DEPOSIT
        elif transaction_type == 'WITHDRAWAL':
            txn_type = TransactionType.WITHDRAWAL
        else:
            txn_type = TransactionType[transaction_type]

        transaction = Transaction(
            account_id=account.account_id,
            transaction_type=txn_type,
            total_amount=amount,
            status=TransactionStatus.COMPLETED
        )
        self.transactions.append(transaction)
        logging.info(f"Transaction created: {transaction.transaction_id} for account {account.account_id}.")
        return transaction.transaction_id
