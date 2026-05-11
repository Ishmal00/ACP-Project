from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Member:
    name: str
    phone: str
    member_id: int = None
    discount_percent: float = 30.0
    join_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


@dataclass
class Session:
    computer_no: int
    customer_name: str
    session_id: int = None
    member_id: int = None
    start_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_time: str = None
    total_bill: float = 0.0
    is_active: bool = True


@dataclass
class Bill:
    session_id: int
    customer_name: str
    computer_no: int
    start_time: str
    end_time: str
    duration_minutes: float
    rate_per_hour: float
    discount: float
    total_amount: float
