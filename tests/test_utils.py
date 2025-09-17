# tests/test_utils.py
from decimal import Decimal
from src.models import Ledger
from src.utils import compute_net_balances, settle_balances

def test_three_way_split():
    ledger = Ledger()
    a = ledger.add_member("A")
    b = ledger.add_member("B")
    c = ledger.add_member("C")
    ledger.add_expense(a.id, "120.00", participants=[a.id, b.id, c.id])
    balances = compute_net_balances(ledger)
    assert balances[a.id] == Decimal("80.00")
    assert balances[b.id] == Decimal("-40.00")
    assert balances[c.id] == Decimal("-40.00")

    settlements = settle_balances(balances)
    assert len(settlements) == 2
    amounts = sorted([s[2] for s in settlements])
    assert amounts == [Decimal("40.00"), Decimal("40.00")]
