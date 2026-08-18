"""Модели данных AutoFL (SQLAlchemy 2.0, async).

Реализация Этапа 2. Статус задачи — через src/workflow/state_machine.py.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(
        String(32), unique=True, index=True
    )  # kwork | flru | youdo
    name: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    accounts: Mapped[list["Account"]] = relationship(back_populates="platform")
    tasks: Mapped[list["Task"]] = relationship(back_populates="platform")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"))
    login: Mapped[str] = mapped_column(String(128))
    profile_url: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(16), default="active"
    )  # active | paused | banned
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    platform: Mapped[Platform] = relationship(back_populates="accounts")
    sessions: Mapped[list["Session"]] = relationship(back_populates="account")
    tasks: Mapped[list["Task"]] = relationship(back_populates="account")
    earnings: Mapped[list["Earning"]] = relationship(back_populates="account")


class Session(Base):
    """Сохранённая браузерная сессия (storage_state) для повторного входа."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    storage_path: Mapped[str] = mapped_column(Text)  # путь к Playwright storage_state
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account: Mapped[Account] = relationship(back_populates="sessions")


class Candidate(Base):
    """Найденное задание ДО решения о принятии в работу."""

    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint(
            "platform_id", "external_id", name="uq_candidate_platform_ext"
        ),
        Index("ix_candidate_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"))
    external_id: Mapped[str] = mapped_column(String(64))
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text, default="")
    budget_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deadline: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), default="new"
    )  # new | skipped | accepted
    safety_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw: Mapped[str] = mapped_column(Text, default="{}")  # сырые данные площадки
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_task_status", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"))
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True
    )
    candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("candidates.id"), nullable=True
    )
    external_id: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text, default="")
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="discovered")
    safety_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[str] = mapped_column(String(64), default="")
    complexity: Mapped[str] = mapped_column(String(16), default="simple")
    revisions_left: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    platform: Mapped[Platform] = relationship(back_populates="tasks")
    account: Mapped[Optional[Account]] = relationship(back_populates="tasks")
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    deliverable: Mapped[str] = mapped_column(Text)  # готовый результат
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16), default="draft"
    )  # draft | approved | submitted | rejected

    task: Mapped[Task] = relationship(back_populates="submissions")


class Revision(Base):
    __tablename__ = "revisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    client_request: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Earning(Base):
    __tablename__ = "earnings"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    status: Mapped[str] = mapped_column(
        String(16), default="pending"
    )  # pending | paid
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account: Mapped[Account] = relationship(back_populates="earnings")


class AuditLog(Base):
    """Аудит всех внешних действий: кто/что/когда сделал."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(
        String(64)
    )  # discover | apply | submit | message | approve
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FundingSource(Base):
    """Платёжный инструмент агента: дебетовая карта / СБП-номер (Трек B1).

    PAN хранится только в зашифрованном виде (src/security/vault.py);
    для передачи заказчику используется masked-вид или СБП-номер.
    """

    __tablename__ = "funding_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(8))  # card | sbp
    holder: Mapped[str] = mapped_column(String(256), default="")
    bank: Mapped[str] = mapped_column(String(128), default="")
    pan_enc: Mapped[str] = mapped_column(Text, default="")  # зашифрованный PAN
    sbp_phone: Mapped[str] = mapped_column(String(32), default="")
    masked: Mapped[str] = mapped_column(
        String(32), default=""
    )  # 1234 **** **** 5678
    status: Mapped[str] = mapped_column(
        String(16), default="active"
    )  # active | paused | blocked
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Transaction(Base):
    """Операция по средствам агента: доход (оплата заказа) или расход
    (SMS-активация, капча, подписка и т.п.). Идемпотентно по ref."""

    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("ref", name="uq_transaction_ref"),
        Index("ix_transaction_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("funding_sources.id"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    direction: Mapped[str] = mapped_column(String(8))  # income | expense
    category: Mapped[str] = mapped_column(String(32), default="other")
    # payment_income | registration | captcha | email | subscription |
    # execution | proxy | fee | other
    ref: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(
        String(16), default="pending"
    )  # pending | confirmed | rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task: Mapped[Optional[Task]] = relationship()
    source: Mapped[Optional[FundingSource]] = relationship()


class Mailbox(Base):
    """Почтовый ящик, созданный для регистрации аккаунта (Трек B2)."""

    __tablename__ = "mailboxes"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password_enc: Mapped[str] = mapped_column(Text, default="")
    provider: Mapped[str] = mapped_column(String(32), default="dry_run")
    status: Mapped[str] = mapped_column(
        String(16), default="new"
    )  # new | ready | used | expired
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PhoneNumber(Base):
    """Номер из SMS-активации (Трек B3)."""

    __tablename__ = "phone_numbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(String(32), default="dry_run")
    number: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(
        String(16), default="requested"
    )  # requested | code_received | used | canceled
    code: Mapped[str] = mapped_column(String(16), default="")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CaptchaRequest(Base):
    """Запрос на решение капчи (Трек B4)."""

    __tablename__ = "captcha_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(String(32), default="dry_run")
    captcha_type: Mapped[str] = mapped_column(String(32), default="image")
    status: Mapped[str] = mapped_column(
        String(16), default="requested"
    )  # requested | solved | failed
    solution: Mapped[str] = mapped_column(String(256), default="")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ProvisioningJob(Base):
    """Задание на регистрацию одного аккаунта (Трек B5)."""

    __tablename__ = "provisioning_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("platforms.id"), nullable=True
    )
    email_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("mailboxes.id"), nullable=True
    )
    phone_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("phone_numbers.id"), nullable=True
    )
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True
    )
    identity: Mapped[str] = mapped_column(Text, default="{}")
    credentials_enc: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(16), default="new"
    )  # new | in_progress | done | failed
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
