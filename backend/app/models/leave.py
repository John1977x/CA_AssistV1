from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from app.db.session import Base


class LeaveMaster(Base):
    __tablename__ = "leave_master"

    leave_master_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    leave_type      = Column(String(100), nullable=False)
    entitled        = Column(Integer, nullable=False)
    calendar_year   = Column(Integer, nullable=False)
    calculation     = Column(String(50), nullable=False)  # MONTHLY / YEARLY / QUARTERLY
    is_deleted      = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
