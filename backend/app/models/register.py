from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Register(Base):
    __tablename__ = "register"

    register_id     = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    in_out_ward     = Column(String(10), nullable=False)           # INWARD | OUTWARD
    doc_date        = Column(Date, nullable=False)
    doc_type        = Column(String(60), nullable=False)
    doc_description = Column(Text, nullable=False)
    client_id       = Column(Integer, ForeignKey("customer.customer_id"))
    owner_id        = Column(Integer, ForeignKey("user.user_id"))
    employee_id     = Column(Integer, ForeignKey("user.user_id"))
    sent_date       = Column(Date)
    acknowledgement = Column(String(200))
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted      = Column(Boolean, nullable=False, default=False)

    tenant   = relationship("Tenant")
    client   = relationship("Customer", foreign_keys=[client_id])
    owner    = relationship("User", foreign_keys=[owner_id])
    employee = relationship("User", foreign_keys=[employee_id])
