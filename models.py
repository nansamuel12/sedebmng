from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    # Set once, when the password is entered correctly. Never asked again.
    is_authenticated = Column(Boolean, default=False)
    # Personal code used in the invite link (t.me/<bot>?start=<code>)
    invite_code = Column(String(16), unique=True, index=True, nullable=False)
    # Small JSON note: half-finished steps, pending invite, password tries.
    # Stored in the database so a restart / sleeping host never loses it.
    state = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class Partnership(Base):
    """Two users who are connected (via invite link) and can fine each other."""
    __tablename__ = "partnerships"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id"),)

    id = Column(Integer, primary_key=True)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # always the smaller id
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Entry(Base):
    """
    One request that needs the OTHER person's answer.

    kind = "fine"    -> creator fines `other`.     `other` must accept / reject.
    kind = "payment" -> creator says "I paid".     `other` (who received) must accept / reject.

    status: pending | accepted | rejected | cancelled
    Money is stored in integer cents (no float errors).
    """
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    kind = Column(String(10), index=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    other_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String(12), default="pending", index=True)
    created_at = Column(DateTime, default=utcnow)
    responded_at = Column(DateTime, nullable=True)

    creator = relationship("User", foreign_keys=[creator_id])
    other = relationship("User", foreign_keys=[other_id])


class SeenUpdate(Base):
    """Telegram retries a message if our answer is slow. We remember update ids so a
    retry can never create a fine twice."""
    __tablename__ = "seen_updates"

    update_id = Column(BigInteger, primary_key=True, autoincrement=False)
    created_at = Column(DateTime, default=utcnow)
