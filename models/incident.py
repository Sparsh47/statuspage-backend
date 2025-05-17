from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base

# Association table for many-to-many relationship between incidents and services
incident_services = Table(
    "incident_services",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incidents.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, default="incident")  # incident or maintenance
    status = Column(String, default="investigating")  # investigating, identified, monitoring, resolved
    impact = Column(String, default="minor")  # minor, major, critical
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    services = relationship("Service", secondary=incident_services, back_populates="incidents")
    updates = relationship("IncidentUpdate", back_populates="incident", order_by="desc(IncidentUpdate.created_at)")

class IncidentUpdate(Base):
    __tablename__ = "incident_updates"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    message = Column(Text)
    status = Column(String)  # investigating, identified, monitoring, resolved
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    incident = relationship("Incident", back_populates="updates")
    user = relationship("User")