from sqlalchemy import Table, Column, ForeignKey, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, 
                            mapped_column, relationship,
                            MappedAsDataclass, Session)
from typing import Optional, List
from pydantic import BaseModel, StrictInt, Field, EmailStr, ConfigDict

class Base(DeclarativeBase, MappedAsDataclass):
    pass

rotation_type_sched_shifts_association = Table(
    'rotation_type_sched_shifts_association',
    Base.metadata,
    Column("rotationTypeId", ForeignKey("rotation_types.id"), primary_key=True),
    Column("shiftTypeId", ForeignKey("shift_types.id"), primary_key=True)
)

class ShiftTypeDb(Base):
    __tablename__ = 'shift_types'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    name : Mapped[str]
    startHour : Mapped[int]
    startMinute : Mapped[int]
    durationMinutes : Mapped[int]
    postBufferMins : Mapped[int]
    isClinical : Mapped[bool]
    isCounted : Mapped[bool]
    isNight : Mapped[bool]

class RotationTypeDb(Base):
    __tablename__ = 'rotation_types'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    name : Mapped[str]
    preBufferMins : Mapped[int]
    postBufferMins : Mapped[int]
    isDefault : Mapped[bool]

    schedulableShiftTypes : Mapped[List[ShiftTypeDb]] = relationship(
        secondary=rotation_type_sched_shifts_association,
        init=False
    )

class GenerationPeriodDb(Base):
    __tablename__ = 'generation_periods'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    name : Mapped[str]
    startYear : Mapped[int]
    startMonth : Mapped[int]
    startDay : Mapped[int]
    durationDays : Mapped[int]

class UserDb(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    lastName : Mapped[str]
    edIsDefault : Mapped[bool]
    firstName : Mapped[Optional[str]] = mapped_column(default=None)
    nickname : Mapped[Optional[str]] = mapped_column(default=None)
    email : Mapped[Optional[str]] = mapped_column(default=None)

    rotations : Mapped[List["UserRotationDb"]] = relationship(back_populates="user", init=False)

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    lastName : str
    edIsDefault : bool
    firstName : Optional[str] = None
    nickname : Optional[str] = None
    email : Optional[str] = None

class AcademicYearDb(Base):
    __tablename__ = 'academic_years'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    name : Mapped[str]
    startYear : Mapped[int]
    startMonth : Mapped[int]
    startDay : Mapped[int]
    durationDays : Mapped[int]

class UserRotationDb(Base):
    __tablename__ = 'user_rotations'

    id : Mapped[int] = mapped_column(primary_key=True, init=False)
    startYear : Mapped[int]
    startMonth : Mapped[int]
    startDay : Mapped[int]
    durationDays : Mapped[int]

    userId : Mapped[int] = mapped_column(ForeignKey("users.id"), init=False)
    generationPeriodId : Optional[Mapped[int]] = mapped_column(ForeignKey("generation_periods.id"), init=False)
    rotationTypeId : Mapped[int] = mapped_column(ForeignKey("rotation_types.id"), init=False)
    academicYearId : Optional[Mapped[int]] = mapped_column(ForeignKey("academic_years.id"), init=False)

    user : Mapped[UserDb] = relationship(back_populates="rotations")
    rotationType : Mapped[RotationTypeDb] = relationship()
    generationPeriod : Optional[Mapped[GenerationPeriodDb]] = relationship(default=None)
    academicYear : Optional[Mapped[AcademicYearDb]] = relationship(default=None)

if __name__ == '__main__':
    engine = create_engine('sqlite://', echo=True)
    Base.metadata.create_all(engine)

    bob_orm = UserDb(lastName=4, edIsDefault=True)
    bob_model = User.model_validate(bob_orm)
    print(bob_model)
