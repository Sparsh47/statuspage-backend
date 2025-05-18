from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base

# Association table for many-to-many relationship between teams and services
team_services = Table(
    "team_services",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, index=True)
    description = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    current_status = Column(String, default="operational")  # operational, degraded, partial_outage, major_outage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="services")
    teams = relationship("Team", secondary=team_services, back_populates="services")
    status_updates = relationship("ServiceStatusUpdate", back_populates="service", order_by="desc(ServiceStatusUpdate.created_at)")
    incidents = relationship("Incident", secondary="incident_services", back_populates="services")

class ServiceStatusUpdate(Base):
    __tablename__ = "service_status_updates"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(String)  # operational, degraded, partial_outage, major_outage
    message = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    service = relationship("Service", back_populates="status_updates")
    user = relationship("User")