import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

# Import actual implementation classes
from account_core import User, Account, AccountStatus
from transaction_core import Transaction, TransactionType, TransactionStatus
from funds_management import FundsService, FundsValidator, InvalidOperationException

class TestUserIntegration:
    """Integration tests for User class"""

    def test_should_create_active_user(self):
        user = User(
            user_id=uuid4(),
            username='testuser',
            email='test@example.com',
            created_at=datetime.now()
        )
        assert user.is_active() == True
        assert user.validate() == True
        assert user.status == AccountStatus.ACTIVE

    def test_should_convert_user_to_dict(self):
        user_id = uuid4()
        user = User(
            user_id=user_id,
            username='testuser',
            email='test@example.com',
            created_at=datetime.now()
        )
        user_dict = user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['status'] == 'ACTIVE'

    def test_should_handle_suspended_user(self):
        user = User(
            user_id=uuid4(),
            username='testuser',
            email='test@example.com',
            created_at=datetime.now(),
            status=AccountStatus.SUSPENDED
        )
        assert user.is_active() == False
        assert user.validate() == False


class TestAccountIntegration:
    """Integration tests for Account class"""

    @pytest.fixture
    def account(self):
        return Account(
            account_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(),
            cash_balance=Decimal('1000.00')
        )

    def test_should_create_account_with_zero_balance(self):
        account = Account(
            account_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now()
        )
        assert account.cash_balance == Decimal('0.00')
        assert account.total_deposits == Decimal('0.00')
        assert account.total_withdrawals == Decimal('0.00')
        assert account.validate() == True

    def test_should_update_balance_correctly(self, account):
        initial_balance = account.cash_balance
        account.update_balance(Decimal('500.00'))
        assert account.cash_balance == initial_balance + Decimal('500.00')
        assert account.cash_balance == Decimal('1500.00')

    def test_should_reject_negative_balance_update(self, account):
        with pytest.raises(ValueError) as exc_info:
            account.update_balance(Decimal('-2000.00'))
        assert "negative" in str(exc_info.value).lower()

    def test_should_check_withdrawal_possibility(self, account):
        assert account.can_withdraw(Decimal('500.00')) == True
        assert account.can_withdraw(Decimal('1000.00')) == True
        assert account.can_withdraw(Decimal('1000.01')) == False
        assert account.can_withdraw(Decimal('2000.00')) == False

    def test_should_convert_account_to_dict(self, account):
        account_dict = account.to_dict()
        assert 'account_id' in account_dict
        assert 'user_id' in account_dict
        assert account_dict['cash_balance'] == '1000.00'
        assert account_dict['total_deposits'] == '0.00'
        assert account_dict['total_withdrawals'] == '0.00'


class TestTransactionIntegration:
    """Integration tests for Transaction class"""

    def test_should_create_deposit_transaction(self):
        transaction = Transaction(
            account_id=uuid4(),
            transaction_type=TransactionType.DEPOSIT,
            total_amount=Decimal('500.00'),
            status=TransactionStatus.PENDING
        )
        assert transaction.transaction_type == TransactionType.DEPOSIT
        assert transaction.total_amount == Decimal('500.00')
        assert transaction.status == TransactionStatus.PENDING
        assert transaction.transaction_id is not None
        assert transaction.transaction_timestamp is not None

    def test_should_create_buy_transaction(self):
        transaction = Transaction(
            account_id=uuid4(),
            transaction_type=TransactionType.BUY,
            total_amount=Decimal('1500.00'),
            symbol='AAPL',
            quantity=10,
            price_per_share=Decimal('150.00'),
            status=TransactionStatus.COMPLETED
        )
        assert transaction.transaction_type == TransactionType.BUY
        assert transaction.symbol == 'AAPL'
        assert transaction.quantity == 10
        assert transaction.price_per_share == Decimal('150.00')
        assert transaction.transaction_id is not None

    def test_should_convert_transaction_to_dict(self):
        transaction = Transaction(
            account_id=uuid4(),
            transaction_type=TransactionType.WITHDRAWAL,
            total_amount=Decimal('200.00'),
            status=TransactionStatus.COMPLETED
        )
        transaction_dict = transaction.to_dict()
        assert transaction_dict['transaction_type'] == 'WITHDRAWAL'
        assert transaction_dict['total_amount'] == '200.00'
        assert transaction_dict['status'] == 'COMPLETED'
        assert 'transaction_id' in transaction_dict
        assert 'transaction_timestamp' in transaction_dict


class TestFundsManagementIntegration:
    """Integration tests for Funds Management module"""

    @pytest.fixture
    def validator(self):
        return FundsValidator()

    @pytest.fixture
    def service(self, validator):
        return FundsService(validator)

    @pytest.fixture
    def account(self):
        return Account(
            account_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(),
            cash_balance=Decimal('1000.00')
        )

    def test_should_deposit_valid_amount(self, service, account):
        initial_balance = account.cash_balance
        transaction_id = service.deposit(account, Decimal('500.00'))

        assert account.cash_balance == initial_balance + Decimal('500.00')
        assert account.total_deposits == Decimal('500.00')
        assert transaction_id is not None

    def test_should_reject_deposit_below_minimum(self, service, account):
        with pytest.raises(InvalidOperationException) as exc_info:
            service.deposit(account, Decimal('0.50'))
        assert "between" in str(exc_info.value).lower()

    def test_should_reject_deposit_above_maximum(self, service, account):
        with pytest.raises(InvalidOperationException) as exc_info:
            service.deposit(account, Decimal('2000000.00'))
        assert "between" in str(exc_info.value).lower()

    def test_should_withdraw_valid_amount(self, service, account):
        initial_balance = account.cash_balance
        transaction_id = service.withdraw(account, Decimal('300.00'))

        assert account.cash_balance == initial_balance - Decimal('300.00')
        assert account.total_withdrawals == Decimal('300.00')
        assert transaction_id is not None

    def test_should_reject_withdrawal_exceeding_balance(self, service, account):
        with pytest.raises(InvalidOperationException) as exc_info:
            service.withdraw(account, Decimal('1500.00'))
        assert "insufficient" in str(exc_info.value).lower()

    def test_should_track_multiple_transactions(self, service, account):
        # Deposit
        service.deposit(account, Decimal('500.00'))
        assert account.cash_balance == Decimal('1500.00')

        # Withdraw
        service.withdraw(account, Decimal('200.00'))
        assert account.cash_balance == Decimal('1300.00')

        # Another deposit
        service.deposit(account, Decimal('100.00'))
        assert account.cash_balance == Decimal('1400.00')

        # Final totals
        assert account.total_deposits == Decimal('600.00')
        assert account.total_withdrawals == Decimal('200.00')

    def test_should_get_transaction_history(self, service, account):
        service.deposit(account, Decimal('500.00'))
        service.withdraw(account, Decimal('100.00'))
        service.deposit(account, Decimal('200.00'))

        history = service.get_transaction_history(account)
        assert len(history) == 3
        assert all(isinstance(t, Transaction) for t in history)


class TestValidationRules:
    """Tests for business rule validation"""

    @pytest.fixture
    def validator(self):
        return FundsValidator()

    @pytest.fixture
    def account(self):
        return Account(
            account_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(),
            cash_balance=Decimal('1000.00')
        )

    def test_should_validate_deposit_amount_precision(self, validator, account):
        # Should accept 2 decimal places
        validator.validate_deposit(account, Decimal('100.50'))
        validator.validate_deposit(account, Decimal('100.99'))

    def test_should_validate_minimum_deposit(self, validator, account):
        # Minimum is $1.00
        validator.validate_deposit(account, Decimal('1.00'))

        with pytest.raises(InvalidOperationException):
            validator.validate_deposit(account, Decimal('0.99'))

    def test_should_validate_withdrawal_against_balance(self, validator, account):
        # Can withdraw up to balance
        validator.validate_withdrawal(account, Decimal('1000.00'))

        # Cannot exceed balance
        with pytest.raises(InvalidOperationException):
            validator.validate_withdrawal(account, Decimal('1000.01'))

    def test_should_allow_withdrawal_leaving_zero_balance(self, validator, account):
        # Minimum balance is $0.00
        validator.validate_withdrawal(account, Decimal('1000.00'))
        account.update_balance(Decimal('-1000.00'))
        assert account.cash_balance == Decimal('0.00')
