import enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional
from datetime import date as DateType

# DATABASE_URL = "postgresql://user:password@localhost/clinic_shift" # 例: 実際の接続情報に置き換えてください
# 動作確認のため一時的にSQLiteを使用します
DATABASE_URL = "sqlite:///./clinic_shift.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # SQLite用の設定
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StaffRank(str, enum.Enum):
    VETERAN = "VETERAN"
    JUNIOR = "JUNIOR"

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    rank = Column(Enum(StaffRank), nullable=False)
    can_recept = Column(Boolean, default=False, nullable=False) # レセコン操作スキル
    max_work_days_per_week = Column(Integer, default=5)

    off_requests = relationship("OffRequest", back_populates="staff")
    assignments = relationship("ShiftAssignment", back_populates="staff")

class ShiftSlot(Base):
    __tablename__ = "shift_slots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # 例: "午前診", "午後診"
    min_staff = Column(Integer, default=1, nullable=False)

class OffRequest(Base):
    __tablename__ = "off_requests"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    date = Column(Date, nullable=False)

    staff = relationship("Staff", back_populates="off_requests")

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    slot_id = Column(Integer, ForeignKey("shift_slots.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)

    staff = relationship("Staff", back_populates="assignments")
    slot = relationship("ShiftSlot")

# --- Pydantic models for API ---
class StaffBase(BaseModel):
    name: str
    rank: StaffRank
    can_recept: bool
    max_work_days_per_week: int

class StaffModel(StaffBase):
    id: int
    class Config:
        orm_mode = True

class OffRequestCreate(BaseModel):
    staff_id: int
    date: DateType

class ShiftAssignmentModel(BaseModel):
    date: DateType
    slot_id: int
    staff_id: int
    class Config:
        orm_mode = True