# src/main.py
from decimal import Decimal
from src.models import Ledger
from src.utils import compute_net_balances, settle_balances

def demo():
    ledger = Ledger()
    a = ledger.add_member("Alice")
    b = ledger.add_member("Bob")
    c = ledger.add_member("Charlie")

    # Alice pays 120 split among A,B,C
    ledger.add_expense(a.id, "120.00", participants=[a.id, b.id, c.id], description="Dinner")
    # Bob pays 45.50 split between A and B
    ledger.add_expense(b.id, "45.50", participants=[a.id, b.id], description="Taxi")

    balances = compute_net_balances(ledger)
    print("== Balances ==")
    for mid, bal in balances.items():
        print(f"{ledger.members[mid].name}: {bal}")

    settlements = settle_balances(balances)
    print("\n== Settlements (who pays who) ==")
    for frm, to, amt in settlements:
        print(f"{ledger.members[frm].name} -> {ledger.members[to].name}: {amt}")

if __name__ == "__main__":
    demo()
