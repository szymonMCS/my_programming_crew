from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
import uuid


class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"


class TransactionException(Exception):
    pass


@dataclass(frozen=True)
class Transaction:
    transaction_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    account_id: uuid.UUID
    transaction_type: TransactionType
    total_amount: Decimal
    transaction_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price_per_share: Optional[Decimal] = None
    status: TransactionStatus = field(default=TransactionStatus.PENDING)
    failure_reason: Optional[str] = None

    def __post_init__(self):
        """Post-initialization checks/validations."""
        if self.transaction_type in {TransactionType.BUY, TransactionType.SELL} and self.symbol is None:
            raise TransactionException("Symbol must be provided for buy/sell transactions.")

        if self.transaction_type in {TransactionType.BUY, TransactionType.SELL} and self.quantity is None:
            raise TransactionException("Quantity must be provided for buy/sell transactions.")

        if self.total_amount <= 0:
            raise TransactionException("Total amount must be positive.")

    def mark_as_completed(self) -> "Transaction":
        """Marks the transaction as completed and returns a new immutable instance."""
        return self._replace_status(TransactionStatus.COMPLETED)

    def mark_as_failed(self, reason: str) -> "Transaction":
        """Marks the transaction as failed with the specified reason and returns a new immutable instance."""
        return self._replace_status(TransactionStatus.FAILED, reason)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the transaction into a dictionary representation."""
        return {
            "transaction_id": str(self.transaction_id),
            "account_id": str(self.account_id),
            "transaction_type": self.transaction_type.value,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price_per_share": str(self.price_per_share) if self.price_per_share else None,
            "total_amount": str(self.total_amount),
            "transaction_timestamp": self.transaction_timestamp.isoformat(),
            "status": self.status.value,
            "failure_reason": self.failure_reason,
        }

    def _replace_status(self, new_status: TransactionStatus, reason: Optional[str] = None) -> "Transaction":
        """Safely replaces transaction status and optionally the failure reason."""
        return Transaction(
            account_id=self.account_id,
            transaction_type=self.transaction_type,
            total_amount=self.total_amount,
            symbol=self.symbol,
            quantity=self.quantity,
            price_per_share=self.price_per_share,
            status=new_status,
            failure_reason=reason
        )