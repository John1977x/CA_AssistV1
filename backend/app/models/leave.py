from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from app.db.session import Base


class LeaveMaster(Base):
    __tablename__ = "leave_master"

    leave_master_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    leave_type      = Column(String(100), nullable=False)
    entitled        = Column(Integer, nullable=False)
    calendar_year   = Column(Integer, nullable=False)
    calculation     = Column(String(50), nullable=False)
    is_deleted      = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class LeaveApplication(Base):
    __tablename__ = "leave_application"

    leave_application_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id            = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    employee_id          = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    leave_type           = Column(String(100), nullable=False)
    leave_date           = Column(Date, nullable=False)
    from_date            = Column(Date, nullable=False)
    to_date              = Column(Date, nullable=False)
    reason               = Column(Text)
    attachment_url       = Column(String(500))
    approver_id          = Column(Integer, ForeignKey("user.user_id"))
    status               = Column(String(20), nullable=False, server_default="PENDING")
    approval_notes       = Column(Text)
    is_deleted           = Column(Boolean, nullable=False, server_default="false")
    created_at           = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
