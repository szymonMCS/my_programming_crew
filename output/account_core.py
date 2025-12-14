"""
Domain models for user accounts and account management.

This module contains the core domain models for the trading platform:
- AccountStatus: Enumeration of possible account states
- User: Represents a platform user
- Account: Represents a trading account with cash balance
"""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict


class AccountStatus(Enum):
    """Enumeration of possible account status values."""

    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'
    CLOSED = 'CLOSED'


class User:
    """
    Represents a user in the trading simulation platform.

    A user can have one or more trading accounts and contains
    authentication and profile information.

    Attributes:
        user_id: Unique identifier for the user
        username: Display name for the user
        email: User email address
        created_at: Account creation timestamp
        status: Current account status (ACTIVE, SUSPENDED, CLOSED)
    """

    def __init__(
        self,
        user_id: UUID,
        username: str,
        email: str,
        created_at: datetime,
        status: AccountStatus = AccountStatus.ACTIVE
    ) -> None:
        """
        Initialize a new User.

        Args:
            user_id: Unique identifier for the user
            username: Display name for the user
            email: User email address
            created_at: Account creation timestamp
            status: Initial account status (defaults to ACTIVE)
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = created_at
        self.status = status

    def validate(self) -> bool:
        """
        Validate user's status.

        Returns:
            True if the user is active, False otherwise
        """
        return self.status == AccountStatus.ACTIVE

    def to_dict(self) -> Dict[str, str]:
        """
        Convert user attributes to a dictionary.

        Returns:
            Dictionary representation of the user with string values
        """
        return {
            'user_id': str(self.user_id),
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value
        }

    def is_active(self) -> bool:
        """
        Check if user account is active.

        Returns:
            True if user account status is ACTIVE, False otherwise
        """
        return self.status == AccountStatus.ACTIVE


class Account:
    """
    Represents a trading account in the trading simulation platform.

    An account holds cash balance, tracks lifetime deposits/withdrawals,
    and belongs to a specific user.

    Attributes:
        account_id: Unique identifier for the account
        user_id: Reference to the User entity this account belongs to
        cash_balance: Available cash balance in USD
        total_deposits: Cumulative lifetime deposits
        total_withdrawals: Cumulative lifetime withdrawals
        created_at: Account creation timestamp
    """

    def __init__(
        self,
        account_id: UUID,
        user_id: UUID,
        created_at: datetime,
        cash_balance: Decimal = Decimal('0.00'),
        total_deposits: Decimal = Decimal('0.00'),
        total_withdrawals: Decimal = Decimal('0.00')
    ) -> None:
        """
        Initialize a new Account.

        Args:
            account_id: Unique identifier for the account
            user_id: ID of the user who owns this account
            created_at: Account creation timestamp
            cash_balance: Initial cash balance (defaults to 0.00)
            total_deposits: Initial total deposits (defaults to 0.00)
            total_withdrawals: Initial total withdrawals (defaults to 0.00)
        """
        self.account_id = account_id
        self.user_id = user_id
        self.cash_balance = cash_balance
        self.total_deposits = total_deposits
        self.total_withdrawals = total_withdrawals
        self.created_at = created_at

    def validate(self) -> bool:
        """
        Validate account state.

        Ensures the account has a non-negative cash balance.

        Returns:
            True if account state is valid (balance >= 0), False otherwise
        """
        return self.cash_balance >= Decimal('0.00')

    def update_balance(self, amount: Decimal) -> None:
        """
        Update the cash balance of the account.

        Args:
            amount: The amount to add to the balance (can be negative)

        Raises:
            ValueError: If the update would result in a negative balance
        """
        new_balance = self.cash_balance + amount
        if new_balance < Decimal('0.00'):
            raise ValueError("New balance cannot be negative.")
        self.cash_balance = new_balance

    def can_withdraw(self, amount: Decimal) -> bool:
        """
        Check if the account can safely withdraw the specified amount.

        Args:
            amount: The amount to check for withdrawal

        Returns:
            True if withdrawal is possible without going negative,
            False otherwise
        """
        return (self.cash_balance - amount) >= Decimal('0.00')

    def to_dict(self) -> Dict[str, str]:
        """
        Convert account attributes to a dictionary.

        Returns:
            Dictionary representation with all account data as strings
        """
        return {
            'account_id': str(self.account_id),
            'user_id': str(self.user_id),
            'cash_balance': f'{self.cash_balance:.2f}',
            'total_deposits': f'{self.total_deposits:.2f}',
            'total_withdrawals': f'{self.total_withdrawals:.2f}',
            'created_at': self.created_at.isoformat()
        }
