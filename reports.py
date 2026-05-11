from tabulate import tabulate
from datetime import datetime
import database as db


# ───────────────────────────────
#  REPORTS
# ───────────────────────────────

class ReportGenerator:

    def daily_revenue_report(self, date: str = None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        sessions = db.get_all_sessions()

        # filter by date and completed sessions only
        daily = [
            s for s in sessions
            if s[4].startswith(date) and s[7] == 0  # is_active = 0
        ]

        if not daily:
            print(f"\n  No completed sessions found for {date}\n")
            return

        table_data = []
        total_revenue = 0.0

        for s in daily:
            session_id  = s[0]
            computer_no = s[1]
            customer    = s[2]
            start_time  = s[4]
            end_time    = s[5] if s[5] else "N/A"
            bill        = s[6]
            total_revenue += bill

            table_data.append([
                session_id,
                computer_no,
                customer,
                start_time,
                end_time,
                f"Rs. {bill:.2f}"
            ])

        headers = ["ID", "PC No", "Customer", "Start Time", "End Time", "Bill"]

        print("\n" + "=" * 60)
        print(f"      DAILY REVENUE REPORT — {date}")
        print("=" * 60)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print("-" * 60)
        print(f"  Total Sessions  : {len(daily)}")
        print(f"  Total Revenue   : Rs. {total_revenue:.2f}")
        print("=" * 60)

    def all_members_report(self):
        members = db.get_all_members()

        if not members:
            print("\n  No members found!\n")
            return

        table_data = []
        for m in members:
            table_data.append([
                m[0],           # member_id
                m[1],           # name
                m[2],           # phone
                f"{m[3]}%",     # discount
                m[4]            # join_date
            ])

        headers = ["ID", "Name", "Phone", "Discount", "Join Date"]

        print("\n" + "=" * 55)
        print("           ALL MEMBERS LIST")
        print("=" * 55)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n  Total Members: {len(members)}")
        print("=" * 55)

    def active_sessions_report(self):
        sessions = db.get_active_sessions()

        if not sessions:
            print("\n  No active sessions right now!\n")
            return

        table_data = []
        for s in sessions:
            # calculate how long they have been sitting
            fmt = "%Y-%m-%d %H:%M:%S"
            start = datetime.strptime(s[4], fmt)
            elapsed = round((datetime.now() - start).total_seconds() / 60, 1)

            table_data.append([
                s[0],           # session_id
                s[1],           # computer_no
                s[2],           # customer_name
                s[4],           # start_time
                f"{elapsed} mins"
            ])

        headers = ["ID", "PC No", "Customer", "Start Time", "Elapsed"]

        print("\n" + "=" * 60)
        print("           ACTIVE SESSIONS RIGHT NOW")
        print("=" * 60)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n  Total Active: {len(sessions)}")
        print("=" * 60)


# ───────────────────────────────
#  TEST
# ───────────────────────────────

if __name__ == "__main__":
    db.create_tables()

    report = ReportGenerator()

    print("\n--- Testing All Members Report ---")
    report.all_members_report()

    print("\n--- Testing Active Sessions Report ---")
    report.active_sessions_report()

    print("\n--- Testing Daily Revenue Report ---")
    report.daily_revenue_report(datetime.now().strftime("%Y-%m-%d"))
