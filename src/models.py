# src/models.py
from dataclasses import dataclass, asdict, field
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, UTC 
from typing import List, Dict, Any
import json

@dataclass
class Member:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ''
    email: str | None = None

@dataclass
class Expense:
    id: str = field(default_factory=lambda: str(uuid4()))
    payer_id: str = ''
    amount: Decimal = Decimal('0.00')
    participants: List[str] = field(default_factory=list)
    description: str = ''
    date: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

class Ledger:
    """
    Simple in-memory ledger. Use Ledger.save/load(...) for persistence (JSON).
    """
    def __init__(self):
        self.members: Dict[str, Member] = {}
        self.expenses: Dict[str, Expense] = {}

    def add_member(self, name: str, email: str | None = None) -> Member:
        m = Member(name=name, email=email)
        self.members[m.id] = m
        return m

    def add_expense(self, payer_id: str, amount, participants: List[str], description: str = '') -> Expense:
        if payer_id not in self.members:
            raise ValueError("payer_id not found in ledger")
        if any(p not in self.members for p in participants):
            raise ValueError("one or more participants not found in ledger")
        amt = Decimal(str(amount))
        e = Expense(payer_id=payer_id, amount=amt, participants=participants, description=description)
        self.expenses[e.id] = e
        return e

    def to_serializable(self) -> Dict[str, Any]:
        return {
            "members": {mid: asdict(m) for mid, m in self.members.items()},
            "expenses": {
                eid: {"id": e.id, "payer_id": e.payer_id, "amount": str(e.amount),
                      "participants": e.participants, "description": e.description, "date": e.date}
                for eid, e in self.expenses.items()
            }
        }

    def save(self, path: str = "data.json") -> None:
        with open(path, "w") as f:
            json.dump(self.to_serializable(), f, indent=2)

    @classmethod
    def load(cls, path: str = "data.json") -> "Ledger":
        with open(path) as f:
            data = json.load(f)
        ledger = cls()
        for mid, md in data.get("members", {}).items():
            m = Member(id=md["id"], name=md["name"], email=md.get("email"))
            ledger.members[m.id] = m
        for eid, ed in data.get("expenses", {}).items():
            e = Expense(id=ed["id"], payer_id=ed["payer_id"], amount=Decimal(ed["amount"]),
                        participants=ed["participants"], description=ed.get("description", ""), date=ed.get("date", ""))
            ledger.expenses[e.id] = e
        return ledger
