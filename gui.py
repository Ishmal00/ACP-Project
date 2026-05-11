import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import urllib.request
import io

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import database as db
from models import Member, Session
from billing import BillingEngine
from reports import ReportGenerator

# ── Color Palette ──
BG_DARK    = "#0d0d1a"
BG_CARD    = "#13132b"
BG_PANEL   = "#1a1a3e"
ACCENT     = "#ff4d6d"
ACCENT2    = "#4cc9f0"
GREEN      = "#06d6a0"
YELLOW     = "#ffd166"
TEXT_WHITE = "#f0f0ff"
TEXT_GRAY  = "#8888aa"
BTN_HOVER  = "#ff2244"


class CyberCafeApp:

    def __init__(self, root):
        self.root = root
        self.root.title("☕ Cyber Cafe Billing System")
        self.root.geometry("1050x680")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        db.create_tables()
        self.report = ReportGenerator()

        self._setup_styles()
        self.build_sidebar()
        self.build_main_area()
        self.show_tab("sessions")

    # ───────────────────────────────
    #  STYLES
    # ───────────────────────────────

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background=BG_PANEL,
                        foreground=TEXT_WHITE,
                        fieldbackground=BG_PANEL,
                        rowheight=32,
                        font=("Consolas", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=ACCENT,
                        foreground=TEXT_WHITE,
                        font=("Consolas", 10, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", TEXT_WHITE)])

        style.configure("Vertical.TScrollbar",
                        background=BG_PANEL,
                        troughcolor=BG_DARK,
                        arrowcolor=TEXT_GRAY)

    # ───────────────────────────────
    #  SIDEBAR
    # ───────────────────────────────

    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=BG_CARD, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=ACCENT, pady=18)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="☕", font=("Segoe UI Emoji", 28),
                 bg=ACCENT, fg=TEXT_WHITE).pack()
        tk.Label(logo_frame, text="CYBER CAFE",
                 font=("Consolas", 13, "bold"), bg=ACCENT, fg=TEXT_WHITE).pack()
        tk.Label(logo_frame, text="Billing System",
                 font=("Consolas", 9), bg=ACCENT, fg="#ffcccc").pack()

        # Stats bar
        stats = tk.Frame(self.sidebar, bg=BG_PANEL, pady=10)
        stats.pack(fill="x", padx=8, pady=10)

        tk.Label(stats, text="📡  System Online",
                 font=("Consolas", 9), bg=BG_PANEL, fg=GREEN).pack()

        now = datetime.now().strftime("%d %b %Y")
        tk.Label(stats, text=f"📅  {now}",
                 font=("Consolas", 9), bg=BG_PANEL, fg=TEXT_GRAY).pack(pady=2)

        # Nav buttons
        tk.Label(self.sidebar, text="NAVIGATION",
                 font=("Consolas", 8, "bold"), bg=BG_CARD,
                 fg=TEXT_GRAY).pack(anchor="w", padx=15, pady=(10, 4))

        self.nav_btns = {}
        nav_items = [
            ("sessions", "🖥️   Sessions",   ACCENT),
            ("members",  "👤   Members",    ACCENT2),
            ("reports",  "📊   Reports",    YELLOW),
        ]

        for key, label, color in nav_items:
            btn = tk.Button(
                self.sidebar, text=label,
                font=("Consolas", 11, "bold"),
                bg=BG_CARD, fg="#ffffff",
                relief="raised", bd=2,
                anchor="w",
                padx=20, pady=10,
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=ACCENT,
                activebackground=BG_PANEL,
                activeforeground="#ffffff",
                command=lambda k=key: self.show_tab(k)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_btns[key] = (btn, color)

        # Footer
        tk.Label(self.sidebar, text="ACP Project\nCappersoft © 2026",
                 font=("Consolas", 8), bg=BG_CARD,
                 fg=TEXT_GRAY, justify="center").pack(side="bottom", pady=15)

    # ───────────────────────────────
    #  MAIN AREA
    # ───────────────────────────────

    def build_main_area(self):
        self.main = tk.Frame(self.root, bg=BG_DARK)
        self.main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(self.main, bg=BG_CARD, pady=12, padx=20)
        topbar.pack(fill="x")

        self.tab_title = tk.Label(topbar, text="",
                                  font=("Consolas", 15, "bold"),
                                  bg=BG_CARD, fg=TEXT_WHITE)
        self.tab_title.pack(side="left")

        self.clock_lbl = tk.Label(topbar, text="",
                                  font=("Consolas", 10),
                                  bg=BG_CARD, fg=TEXT_GRAY)
        self.clock_lbl.pack(side="right")
        self._tick()

        # Content area
        self.content = tk.Frame(self.main, bg=BG_DARK)
        self.content.pack(fill="both", expand=True, padx=15, pady=12)

        # Build all tabs (hidden initially)
        self.tab_session = tk.Frame(self.content, bg=BG_DARK)
        self.tab_members = tk.Frame(self.content, bg=BG_DARK)
        self.tab_reports = tk.Frame(self.content, bg=BG_DARK)

        self.build_session_tab()
        self.build_members_tab()
        self.build_reports_tab()

    def _tick(self):
        now = datetime.now().strftime("%H:%M:%S  |  %A")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self._tick)

    def show_tab(self, key):
        tabs = {"sessions": self.tab_session,
                "members":  self.tab_members,
                "reports":  self.tab_reports}
        titles = {
            "sessions": "🖥️   Session Management",
            "members":  "👤   Member Management",
            "reports":  "📊   Revenue Reports",
        }

        for frame in tabs.values():
            frame.pack_forget()

        tabs[key].pack(fill="both", expand=True)
        self.tab_title.config(text=titles[key])

        # Highlight active nav
        for k, (btn, color) in self.nav_btns.items():
            if k == key:
                btn.config(bg=BG_PANEL, fg="#ffffff")
            else:
                btn.config(bg=BG_CARD, fg="#ffffff")

    # ───────────────────────────────
    #  HELPERS
    # ───────────────────────────────

    def card(self, parent, title, pady=10):
        outer = tk.Frame(parent, bg=BG_CARD, pady=pady, padx=18,
                         highlightbackground=ACCENT,
                         highlightthickness=1)
        outer.pack(fill="x", pady=(0, 12))

        tk.Label(outer, text=title,
                 font=("Consolas", 11, "bold"),
                 fg=ACCENT, bg=BG_CARD).pack(anchor="w", pady=(0, 8))
        return outer

    def make_label(self, parent, text, row, col):
        tk.Label(parent, text=text,
                 font=("Consolas", 10), fg=TEXT_GRAY, bg=BG_CARD
                 ).grid(row=row, column=col, padx=10, pady=6, sticky="w")

    def make_entry(self, parent, row, col, width=22, placeholder=""):
        entry = tk.Entry(parent,
                         font=("Consolas", 10),
                         bg=BG_PANEL, fg=TEXT_WHITE,
                         insertbackground=ACCENT,
                         width=width, relief="flat", bd=6,
                         highlightthickness=1,
                         highlightbackground=ACCENT2,
                         highlightcolor=ACCENT)
        entry.grid(row=row, column=col, padx=10, pady=6, sticky="w")
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=TEXT_GRAY)
            entry.bind("<FocusIn>",  lambda e, en=entry, ph=placeholder: self._clear_ph(en, ph))
            entry.bind("<FocusOut>", lambda e, en=entry, ph=placeholder: self._restore_ph(en, ph))
        return entry

    def _clear_ph(self, entry, ph):
        if entry.get() == ph:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT_WHITE)

    def _restore_ph(self, entry, ph):
        if entry.get() == "":
            entry.insert(0, ph)
            entry.config(fg=TEXT_GRAY)

    def make_button(self, parent, text, cmd, color=ACCENT,
                    row=0, col=0, padx=6, pady=8, width=18):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=color, fg="#ffffff",
                        font=("Consolas", 11, "bold"),
                        relief="raised", bd=3,
                        padx=14, pady=8,
                        cursor="hand2", width=width,
                        activebackground=self._darken(color),
                        activeforeground="#ffffff",
                        highlightthickness=2,
                        highlightbackground=color,
                        highlightcolor=color)
        btn.grid(row=row, column=col, padx=padx, pady=pady)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._darken(color), fg="#ffffff"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color, fg="#ffffff"))
        return btn

    def _darken(self, hex_color):
        mapping = {
            ACCENT:  "#cc2244",
            GREEN:   "#04a87e",
            ACCENT2: "#2ba8d0",
            YELLOW:  "#ccaa44",
            "#555577": "#444466",
        }
        return mapping.get(hex_color, "#333355")

    def make_treeview(self, parent, cols, heights=10):
        frame = tk.Frame(parent, bg=BG_DARK,
                         highlightbackground=ACCENT2,
                         highlightthickness=1)
        frame.pack(fill="both", expand=True, pady=(4, 0))

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=heights)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Alternate row colors
        tree.tag_configure("odd",  background="#1a1a3e")
        tree.tag_configure("even", background="#13132b")

        return tree

    # ───────────────────────────────
    #  TAB 1 — SESSIONS
    # ───────────────────────────────

    def build_session_tab(self):
        # Stats row
        stats_row = tk.Frame(self.tab_session, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 10))

        self._stat_box(stats_row, "🖥️", "Active PCs",    self._count_active,  ACCENT)
        self._stat_box(stats_row, "👥", "Total Members", self._count_members, ACCENT2)
        self._stat_box(stats_row, "💰", "Today Revenue", self._today_revenue, GREEN)

        # Form card
        form_card = self.card(self.tab_session, "  ▶   START NEW SESSION")
        grid = tk.Frame(form_card, bg=BG_CARD)
        grid.pack(fill="x")

        self.make_label(grid, "Customer Name:", 0, 0)
        self.sess_name = self.make_entry(grid, 0, 1, placeholder="e.g. Ali Khan")

        self.make_label(grid, "Computer No:", 0, 2)
        self.sess_pc = self.make_entry(grid, 0, 3, width=8, placeholder="1-20")

        self.make_label(grid, "Member ID (optional):", 1, 0)
        self.sess_member = self.make_entry(grid, 1, 1, placeholder="Leave blank if guest")

        btn_row = tk.Frame(form_card, bg=BG_CARD)
        btn_row.pack(pady=(6, 0))

        self.make_button(btn_row, "▶  Start Session", self.start_session, GREEN,   0, 0)
        self.make_button(btn_row, "⏹  End Session",   self.end_session,   ACCENT,  0, 1)
        self.make_button(btn_row, "🔄  Refresh",       self.load_sessions, "#555577", 0, 2)

        # Table
        tk.Label(self.tab_session, text="  🟢  ACTIVE SESSIONS",
                 font=("Consolas", 10, "bold"),
                 fg=GREEN, bg=BG_DARK).pack(anchor="w", pady=(4, 2))

        cols = ("ID", "PC No", "Customer", "Member ID", "Start Time", "Status")
        self.sess_tree = self.make_treeview(self.tab_session, cols, heights=8)
        self.load_sessions()

    def _stat_box(self, parent, icon, label, value_fn, color):
        box = tk.Frame(parent, bg=BG_CARD, padx=16, pady=10,
                       highlightbackground=color, highlightthickness=1)
        box.pack(side="left", expand=True, fill="x", padx=5)

        tk.Label(box, text=icon, font=("Segoe UI Emoji", 18),
                 bg=BG_CARD, fg=color).pack()
        tk.Label(box, text=value_fn(),
                 font=("Consolas", 18, "bold"),
                 bg=BG_CARD, fg=color).pack()
        tk.Label(box, text=label,
                 font=("Consolas", 9),
                 bg=BG_CARD, fg=TEXT_GRAY).pack()

    def _count_active(self):
        return str(len(db.get_active_sessions()))

    def _count_members(self):
        return str(len(db.get_all_members()))

    def _today_revenue(self):
        rev = db.get_daily_revenue(datetime.now().strftime("%Y-%m-%d"))
        return f"Rs.{rev:.0f}"

    def start_session(self):
        name = self.sess_name.get().strip()
        pc   = self.sess_pc.get().strip()

        if not name or name == "e.g. Ali Khan":
            messagebox.showwarning("Missing!", "Please enter Customer Name!")
            return
        if not pc or pc == "1-20":
            messagebox.showwarning("Missing!", "Please enter PC Number!")
            return
        try:
            pc = int(pc)
        except ValueError:
            messagebox.showerror("Error", "PC Number must be a number!")
            return

        member_raw = self.sess_member.get().strip()
        member_id  = None
        if member_raw and member_raw != "Leave blank if guest":
            try:
                member_id = int(member_raw)
            except ValueError:
                messagebox.showerror("Error", "Member ID must be a number!")
                return

        session = Session(computer_no=pc, customer_name=name, member_id=member_id)
        db.start_session(session)

        for e in [self.sess_name, self.sess_pc, self.sess_member]:
            e.delete(0, tk.END)

        messagebox.showinfo("✅ Started!", f"Session started for {name} on PC {pc}!")
        self.load_sessions()

    def end_session(self):
        selected = self.sess_tree.selection()
        if not selected:
            messagebox.showwarning("Select!", "Please select a session row to end!")
            return

        values      = self.sess_tree.item(selected[0])["values"]
        session_id  = values[0]
        computer_no = values[1]
        customer    = values[2]
        member_id   = values[3]
        start_time  = values[4]

        end_time  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_member = str(member_id) not in ("None", "", "0")

        engine = BillingEngine(is_member=is_member)
        bill   = engine.generate_bill(session_id, customer, computer_no,
                                      start_time, end_time)
        db.end_session(session_id, end_time, bill.total_amount)

        receipt = (
            f"╔══════════════════════════╗\n"
            f"║    CYBER CAFE RECEIPT    ║\n"
            f"╠══════════════════════════╣\n"
            f"  Customer  : {customer}\n"
            f"  PC No     : {computer_no}\n"
            f"  Duration  : {bill.duration_minutes:.1f} mins\n"
            f"  Rate/Hr   : Rs. {bill.rate_per_hour:.2f}\n"
            f"  Discount  : Rs. {bill.discount:.2f}\n"
            f"══════════════════════════\n"
            f"  TOTAL     : Rs. {bill.total_amount:.2f}\n"
            f"╚══════════════════════════╝\n"
            f"     Thank you! Come again!"
        )
        messagebox.showinfo("🧾 Receipt", receipt)
        self.load_sessions()

    def load_sessions(self):
        for row in self.sess_tree.get_children():
            self.sess_tree.delete(row)
        for i, s in enumerate(db.get_active_sessions()):
            tag = "odd" if i % 2 else "even"
            self.sess_tree.insert("", "end", tags=(tag,), values=(
                s[0], s[1], s[2],
                s[3] if s[3] else "Guest",
                s[4], "🟢 Active"
            ))

    # ───────────────────────────────
    #  TAB 2 — MEMBERS
    # ───────────────────────────────

    def build_members_tab(self):
        form_card = self.card(self.tab_members, "  ➕   ADD NEW MEMBER")
        grid = tk.Frame(form_card, bg=BG_CARD)
        grid.pack(fill="x")

        self.make_label(grid, "Full Name:", 0, 0)
        self.mem_name = self.make_entry(grid, 0, 1, placeholder="e.g. Sara Ahmed")

        self.make_label(grid, "Phone:", 0, 2)
        self.mem_phone = self.make_entry(grid, 0, 3, placeholder="03xx-xxxxxxx")

        btn_row = tk.Frame(form_card, bg=BG_CARD)
        btn_row.pack(pady=(6, 0))

        self.make_button(btn_row, "➕  Add Member",    self.add_member,    GREEN,    0, 0)
        self.make_button(btn_row, "🗑️  Delete Member",  self.delete_member, ACCENT,   0, 1)
        self.make_button(btn_row, "🔄  Refresh",        self.load_members,  "#555577", 0, 2)

        tk.Label(self.tab_members, text="  👥  ALL MEMBERS  —  30% Discount on Sessions",
                 font=("Consolas", 10, "bold"),
                 fg=ACCENT2, bg=BG_DARK).pack(anchor="w", pady=(4, 2))

        cols = ("ID", "Name", "Phone", "Discount %", "Join Date")
        self.mem_tree = self.make_treeview(self.tab_members, cols, heights=12)
        self.load_members()

    def add_member(self):
        name  = self.mem_name.get().strip()
        phone = self.mem_phone.get().strip()

        if not name or name == "e.g. Sara Ahmed":
            messagebox.showwarning("Missing!", "Please enter member name!")
            return
        if not phone or phone == "03xx-xxxxxxx":
            messagebox.showwarning("Missing!", "Please enter phone number!")
            return

        db.add_member(Member(name=name, phone=phone))
        for e in [self.mem_name, self.mem_phone]:
            e.delete(0, tk.END)
        messagebox.showinfo("✅ Added!", f"Member '{name}' added! They get 30% discount.")
        self.load_members()

    def delete_member(self):
        selected = self.mem_tree.selection()
        if not selected:
            messagebox.showwarning("Select!", "Please select a member row!")
            return
        values    = self.mem_tree.item(selected[0])["values"]
        member_id = values[0]
        name      = values[1]
        if messagebox.askyesno("Confirm Delete", f"Delete member '{name}'?"):
            db.delete_member(member_id)
            messagebox.showinfo("Deleted!", f"Member '{name}' removed.")
            self.load_members()

    def load_members(self):
        for row in self.mem_tree.get_children():
            self.mem_tree.delete(row)
        for i, m in enumerate(db.get_all_members()):
            tag = "odd" if i % 2 else "even"
            self.mem_tree.insert("", "end", tags=(tag,), values=(
                m[0], m[1], m[2], f"{m[3]}%", m[4]
            ))

    # ───────────────────────────────
    #  TAB 3 — REPORTS
    # ───────────────────────────────

    def build_reports_tab(self):
        form_card = self.card(self.tab_reports, "  📊   REVENUE ANALYTICS")
        ctrl = tk.Frame(form_card, bg=BG_CARD)
        ctrl.pack(fill="x")

        self.make_label(ctrl, "Select Date:", 0, 0)
        self.rep_date = self.make_entry(ctrl, 0, 1,
                                        placeholder=datetime.now().strftime("%Y-%m-%d"))

        btn_row = tk.Frame(form_card, bg=BG_CARD)
        btn_row.pack(pady=(6, 0))

        self.make_button(btn_row, "💰 Daily Revenue",   self.show_daily,        GREEN,    0, 0)
        self.make_button(btn_row, "📋 All Sessions",    self.show_all_sessions, ACCENT2,  0, 1)
        self.make_button(btn_row, "🗑️  Clear",           self.clear_report,      "#555577", 0, 2)

        # Output
        out_frame = tk.Frame(self.tab_reports, bg=BG_PANEL,
                             highlightbackground=ACCENT2,
                             highlightthickness=1)
        out_frame.pack(fill="both", expand=True)

        self.rep_text = tk.Text(
            out_frame,
            font=("Consolas", 10),
            bg=BG_PANEL, fg=TEXT_WHITE,
            insertbackground=ACCENT,
            relief="flat", padx=16, pady=12,
            spacing1=2, spacing2=2
        )
        scroll = ttk.Scrollbar(out_frame, orient="vertical",
                               command=self.rep_text.yview)
        self.rep_text.configure(yscrollcommand=scroll.set)
        self.rep_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Tags for colors
        self.rep_text.tag_config("header", foreground=ACCENT,  font=("Consolas", 11, "bold"))
        self.rep_text.tag_config("green",  foreground=GREEN)
        self.rep_text.tag_config("yellow", foreground=YELLOW)
        self.rep_text.tag_config("gray",   foreground=TEXT_GRAY)

    def show_daily(self):
        date_raw = self.rep_date.get().strip()
        date = date_raw if date_raw != datetime.now().strftime("%Y-%m-%d") else datetime.now().strftime("%Y-%m-%d")

        sessions = db.get_all_sessions()
        daily    = [s for s in sessions if s[4].startswith(date) and s[7] == 0]

        self.rep_text.delete("1.0", tk.END)
        self.rep_text.insert(tk.END, f"  DAILY REVENUE REPORT\n", "header")
        self.rep_text.insert(tk.END, f"  Date : {date}\n", "gray")
        self.rep_text.insert(tk.END, "  " + "─" * 52 + "\n", "gray")

        if not daily:
            self.rep_text.insert(tk.END, "\n  No completed sessions found for this date.\n", "gray")
            return

        self.rep_text.insert(tk.END,
            f"  {'ID':<5} {'PC':<5} {'Customer':<18} {'Duration':<12} {'Bill':>10}\n", "yellow")
        self.rep_text.insert(tk.END, "  " + "─" * 52 + "\n", "gray")

        total = 0.0
        for s in daily:
            total += s[6]
            dur = ""
            if s[5]:
                try:
                    fmt  = "%Y-%m-%d %H:%M:%S"
                    mins = (datetime.strptime(s[5], fmt) - datetime.strptime(s[4], fmt)).total_seconds() / 60
                    dur  = f"{mins:.0f} min"
                except:
                    dur = "N/A"
            self.rep_text.insert(tk.END,
                f"  {s[0]:<5} {s[1]:<5} {s[2]:<18} {dur:<12} Rs.{s[6]:>8.2f}\n")

        self.rep_text.insert(tk.END, "  " + "─" * 52 + "\n", "gray")
        self.rep_text.insert(tk.END, f"  Sessions  : {len(daily)}\n", "green")
        self.rep_text.insert(tk.END, f"  Revenue   : Rs. {total:.2f}\n", "green")

    def show_all_sessions(self):
        sessions = db.get_all_sessions()
        self.rep_text.delete("1.0", tk.END)
        self.rep_text.insert(tk.END, "  ALL SESSIONS HISTORY\n", "header")
        self.rep_text.insert(tk.END, "  " + "─" * 55 + "\n", "gray")

        if not sessions:
            self.rep_text.insert(tk.END, "\n  No sessions found!\n", "gray")
            return

        self.rep_text.insert(tk.END,
            f"  {'ID':<5} {'PC':<5} {'Customer':<16} {'Status':<10} {'Bill':>10}\n", "yellow")
        self.rep_text.insert(tk.END, "  " + "─" * 55 + "\n", "gray")

        for s in sessions:
            status = "🟢 Active" if s[7] == 1 else "✅ Done"
            self.rep_text.insert(tk.END,
                f"  {s[0]:<5} {s[1]:<5} {s[2]:<16} {status:<10} Rs.{s[6]:>8.2f}\n")

    def clear_report(self):
        self.rep_text.delete("1.0", tk.END)


# ───────────────────────────────
#  RUN
# ───────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = CyberCafeApp(root)
    root.mainloop()