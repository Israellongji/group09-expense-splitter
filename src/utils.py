# src/utils.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple
from src.models import Ledger

def quantize_amount(d: Decimal) -> Decimal:
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_net_balances(ledger: Ledger) -> Dict[str, Decimal]:
    """
    Returns mapping member_id -> Decimal(balance).
    Positive = member should receive money.
    Negative = member owes money.
    """
    balances: Dict[str, Decimal] = {m_id: Decimal("0.00") for m_id in ledger.members}
    for e in ledger.expenses.values():
        amount = Decimal(e.amount)
        participants = e.participants
        if not participants:
            continue
        share = amount / Decimal(len(participants))
        share = quantize_amount(share)
        # payer gets full amount, each participant is debited their share
        balances[e.payer_id] += amount
        for p in participants:
            balances[p] -= share

    # quantize and fix tiny rounding residual so total sums to 0
    for k in balances:
        balances[k] = quantize_amount(balances[k])

    total = sum(balances.values())
    if total != Decimal("0.00"):
        # adjust first member to remove residual (small cents)
        first = next(iter(balances))
        balances[first] = quantize_amount(balances[first] - total)
    return balances

def settle_balances(balances: Dict[str, Decimal]) -> List[Tuple[str, str, Decimal]]:
    """
    Greedy algorithm:
      returns list of tuples (from_id, to_id, amount)
    meaning: from_id pays to_id amount.
    """
    creditors = [(m_id, amt) for m_id, amt in balances.items() if amt > 0]
    debtors = [(m_id, amt) for m_id, amt in balances.items() if amt < 0]

    creditors.sort(key=lambda x: x[1], reverse=True)  # biggest creditor first
    debtors.sort(key=lambda x: x[1])                  # most negative (largest debtor) first

    i = j = 0
    settlements: List[Tuple[str, str, Decimal]] = []
    while i < len(creditors) and j < len(debtors):
        cred_id, cred_amt = creditors[i]
        debt_id, debt_amt = debtors[j]  # debt_amt is negative
        settle_amt = min(cred_amt, -debt_amt)
        settle_amt = quantize_amount(settle_amt)
        if settle_amt == Decimal("0.00"):
            break
        settlements.append((debt_id, cred_id, settle_amt))  # debtor pays creditor
        cred_amt = quantize_amount(cred_amt - settle_amt)
        debt_amt = quantize_amount(debt_amt + settle_amt)   # closer to zero
        creditors[i] = (cred_id, cred_amt)
        debtors[j]   = (debt_id, debt_amt)
        if creditors[i][1] == Decimal("0.00"):
            i += 1
        if debtors[j][1] == Decimal("0.00"):
            j += 1
    return settlements
