from abc import ABC, abstractmethod
from datetime import datetime
from models import Bill


# ───────────────────────────────
#  STRATEGY PATTERN (OOP)
# ───────────────────────────────

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, duration_minutes: float) -> tuple:
        pass


class RegularPricing(PricingStrategy):
    RATE_PER_HOUR = 30.0

    def calculate(self, duration_minutes: float) -> tuple:
        hours = duration_minutes / 60
        total = round(hours * self.RATE_PER_HOUR, 2)
        discount = 0.0
        return total, discount, self.RATE_PER_HOUR


class MemberPricing(PricingStrategy):
    RATE_PER_HOUR = 30.0
    DISCOUNT_PERCENT = 30.0

    def calculate(self, duration_minutes: float) -> tuple:
        hours = duration_minutes / 60
        original = hours * self.RATE_PER_HOUR
        discount = round(original * (self.DISCOUNT_PERCENT / 100), 2)
        total = round(original - discount, 2)
        return total, discount, self.RATE_PER_HOUR


# ───────────────────────────────
#  BILLING ENGINE
# ───────────────────────────────

class BillingEngine:

    def __init__(self, is_member: bool = False):
        if is_member:
            self.strategy = MemberPricing()
        else:
            self.strategy = RegularPricing()

    def generate_bill(self, session_id, customer_name, computer_no,
                      start_time: str, end_time: str) -> Bill:

        # calculate duration
        fmt = "%Y-%m-%d %H:%M:%S"
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        duration_minutes = round((end - start).total_seconds() / 60, 2)

        # apply pricing strategy
        total_amount, discount, rate = self.strategy.calculate(duration_minutes)

        bill = Bill(
            session_id=session_id,
            customer_name=customer_name,
            computer_no=computer_no,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            rate_per_hour=rate,
            discount=discount,
            total_amount=total_amount
        )
        return bill

    def print_receipt(self, bill: Bill):
        print("=" * 40)
        print("     CYBER CAFE - RECEIPT")
        print("=" * 40)
        print(f"  Customer    : {bill.customer_name}")
        print(f"  Computer No : {bill.computer_no}")
        print(f"  Start Time  : {bill.start_time}")
        print(f"  End Time    : {bill.end_time}")
        print(f"  Duration    : {bill.duration_minutes:.1f} mins")
        print(f"  Rate/Hour   : Rs. {bill.rate_per_hour:.2f}")
        if bill.discount > 0:
            print(f"  Discount    : Rs. {bill.discount:.2f} (Member 30%)")
        print("-" * 40)
        print(f"  TOTAL       : Rs. {bill.total_amount:.2f}")
        print("=" * 40)
        print("   Thank you! Visit Again :)")
        print("=" * 40)


# ───────────────────────────────
#  TEST
# ───────────────────────────────

if __name__ == "__main__":
    print("--- Regular Customer ---")
    engine1 = BillingEngine(is_member=False)
    bill1 = engine1.generate_bill(
        session_id=1,
        customer_name="Ali Khan",
        computer_no=3,
        start_time="2026-04-28 10:00:00",
        end_time="2026-04-28 11:30:00"
    )
    engine1.print_receipt(bill1)

    print()

    print("--- Member Customer ---")
    engine2 = BillingEngine(is_member=True)
    bill2 = engine2.generate_bill(
        session_id=2,
        customer_name="Sara Ahmed",
        computer_no=5,
        start_time="2026-04-28 12:00:00",
        end_time="2026-04-28 13:00:00"
    )
    engine2.print_receipt(bill2)
