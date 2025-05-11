from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Float, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    OPERATOR = "operator"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductionOrder(Base):
    __tablename__ = "production_orders"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    in_production = Column(Boolean, default=False)
    in_quality = Column(Boolean, default=False)
    quality_forms = relationship("QualityForm", back_populates="production_order")
    production_forms = relationship("ProductionForm", back_populates="production_order")

    @classmethod
    def get_by_order_number(cls, db, order_number):
        return db.query(cls).filter(cls.order_number == order_number).first()

class QualityForm(Base):
    __tablename__ = "quality_forms"
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    apariencia = Column(String(50), nullable=False)  # A, B, C
    color = Column(String(50), nullable=False)  # A, B, C
    olor = Column(String(50), nullable=False)  # A, B, C
    humedad = Column(Float, nullable=False)  # 10-14%
    proteina = Column(Float, nullable=False)  # 18-22%
    grasa = Column(Float, nullable=False)  # 2-4%
    fibra = Column(Float, nullable=False)  # 3-5%
    cenizas = Column(Float, nullable=False)  # 5-7%
    created_at = Column(DateTime, default=datetime.utcnow)
    
    production_order = relationship("ProductionOrder", back_populates="quality_forms")
    user = relationship("User")

class ProductionForm(Base):
    __tablename__ = "production_forms"
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    dieta = Column(String(50), nullable=False)
    molienda = Column(Float, nullable=False)
    durabilidad = Column(Float, nullable=False)
    dureza = Column(Integer, nullable=False)
    temperatura = Column(Integer, nullable=False)
    peletizadora = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    production_order = relationship("ProductionOrder", back_populates="production_forms")
    user = relationship("User")

class DailyPlan(Base):
    __tablename__ = 'daily_plans'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    estimated_orders = Column(Integer)
    die_size = Column(Float)
    soy_tons = Column(Float)
    corn_cake_tons = Column(Float)
    
    @classmethod
    def get_by_date(cls, db, date):
        return db.query(cls).filter(cls.date == date).first() 