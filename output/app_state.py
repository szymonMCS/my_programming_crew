from uuid import uuid4, UUID
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from account_core import User, Account, AccountStatus
from transaction_core import Transaction, TransactionType, TransactionStatus
from trading_engine import Holding, TradingService, TradingValidator
from funds_management import FundsService, FundsValidator
from portfolio_valuation import PortfolioValuator, ProfitLossCalculator
from reporting_and_pricing import PriceService


class HoldingsRepository:
    """In-memory repository for holdings."""

    def __init__(self):
        self.holdings: Dict[str, Dict[str, Holding]] = {}  # account_id -> {symbol -> Holding}

    def find_by_symbol(self, account_id: UUID, symbol: str) -> Optional[Holding]:
        """Find holding by symbol for a specific account."""
        account_holdings = self.holdings.get(str(account_id), {})
        return account_holdings.get(symbol)

    def get_all(self, account_id: UUID) -> List[Holding]:
        """Get all holdings for an account."""
        account_holdings = self.holdings.get(str(account_id), {})
        return list(account_holdings.values())

    def save(self, holding: Holding) -> None:
        """Save or update a holding."""
        account_id_str = str(holding.account_id)
        if account_id_str not in self.holdings:
            self.holdings[account_id_str] = {}

        if holding.quantity > 0:
            self.holdings[account_id_str][holding.symbol] = holding
        elif holding.symbol in self.holdings[account_id_str]:
            # Remove holding if quantity is 0
            del self.holdings[account_id_str][holding.symbol]


class TransactionsRepository:
    """In-memory repository for transactions."""

    def __init__(self):
        self.transactions: List[Transaction] = []

    def save(self, transaction: Transaction) -> None:
        """Save a transaction."""
        self.transactions.append(transaction)

    def get_by_account(self, account_id: UUID) -> List[Transaction]:
        """Get all transactions for an account."""
        return [txn for txn in self.transactions if txn.account_id == account_id]


class AppState:
    """Global application state manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.users: Dict[str, User] = {}  # username -> User
        self.accounts: Dict[UUID, Account] = {}  # account_id -> Account
        self.user_accounts: Dict[UUID, UUID] = {}  # user_id -> account_id

        # Repositories
        self.holdings_repo = HoldingsRepository()
        self.transactions_repo = TransactionsRepository()

        # Services
        self.price_service = PriceService()
        self.funds_validator = FundsValidator()
        self.funds_service = FundsService(self.funds_validator)

        self.current_user: Optional[User] = None
        self.current_account: Optional[Account] = None

        self._initialized = True

    def create_user(self, username: str, email: str) -> User:
        """Create a new user and account."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")

        user = User(
            user_id=uuid4(),
            username=username,
            email=email,
            created_at=datetime.now()
        )

        account = Account(
            account_id=uuid4(),
            user_id=user.user_id,
            created_at=datetime.now()
        )

        self.users[username] = user
        self.accounts[account.account_id] = account
        self.user_accounts[user.user_id] = account.account_id

        return user

    def login_user(self, username: str) -> bool:
        """Login a user by username."""
        if username not in self.users:
            return False

        user = self.users[username]
        account_id = self.user_accounts.get(user.user_id)

        if account_id:
            self.current_user = user
            self.current_account = self.accounts[account_id]
            return True

        return False

    def logout_user(self) -> None:
        """Logout current user."""
        self.current_user = None
        self.current_account = None

    def get_current_account(self) -> Optional[Account]:
        """Get current logged-in account."""
        return self.current_account

    def get_trading_service(self) -> Optional[TradingService]:
        """Get trading service for current account."""
        if not self.current_account:
            return None

        # Create a wrapper for holdings_repo that works with TradingService
        class HoldingsRepoAdapter:
            def __init__(self, repo, account_id):
                self.repo = repo
                self.account_id = account_id

            def find_by_symbol(self, symbol: str) -> Optional[Holding]:
                return self.repo.find_by_symbol(self.account_id, symbol)

            def save(self, holding: Holding) -> None:
                self.repo.save(holding)

        holdings_adapter = HoldingsRepoAdapter(self.holdings_repo, self.current_account.account_id)

        trading_validator = TradingValidator(
            self.current_account,
            holdings_adapter,
            self.price_service
        )

        trading_service = TradingService(
            self.current_account,
            holdings_adapter,
            self.transactions_repo,
            self.price_service,
            trading_validator
        )

        return trading_service

    def get_portfolio_valuator(self) -> Optional[PortfolioValuator]:
        """Get portfolio valuator for current account."""
        if not self.current_account:
            return None

        holdings = self.holdings_repo.get_all(self.current_account.account_id)
        return PortfolioValuator(self.current_account, holdings, self.price_service)

    def get_profit_loss_calculator(self) -> Optional[ProfitLossCalculator]:
        """Get P&L calculator for current account."""
        valuator = self.get_portfolio_valuator()
        if not valuator or not self.current_account:
            return None

        return ProfitLossCalculator(self.current_account, valuator)

    def get_transaction_history(self) -> List[Transaction]:
        """Get transaction history for current account."""
        if not self.current_account:
            return []

        # Combine both funds and trading transactions
        funds_txns = self.funds_service.get_transaction_history(self.current_account)
        trading_txns = self.transactions_repo.get_by_account(self.current_account.account_id)

        all_txns = funds_txns + trading_txns
        # Sort by timestamp descending
        all_txns.sort(key=lambda t: t.transaction_timestamp, reverse=True)

        return all_txns

    def get_holdings(self) -> List[Holding]:
        """Get all holdings for current account."""
        if not self.current_account:
            return []

        return self.holdings_repo.get_all(self.current_account.account_id)


# Global app state instance
app_state = AppState()
