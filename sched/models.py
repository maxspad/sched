from pydantic import BaseModel, StrictInt, Field, EmailStr
from datetime import date, time, datetime, timedelta
from enum import Enum
from typing import Union, List, Dict, Optional

class ShiftType(BaseModel):
    id : StrictInt
    name : str
    startTime : timedelta
    endTime : timedelta
    postBuffer : timedelta = timedelta(seconds=0)
    isClinical : bool = True
    isCounted : bool = True
    isNight : bool = False

class ScheduleableShiftsType(Enum):
    ALL = 'all'
    NONE = 'none'

class RotationType(BaseModel):
    id : StrictInt
    name : str
    preBuffer : timedelta = timedelta(seconds=0)
    postBuffer : timedelta = timedelta(seconds=0)
    isDefault : bool = False
    scheduleableShifts : Optional[Union[ScheduleableShiftsType, List[ShiftType]]] = None

class GenerationPeriod(BaseModel):
    id : StrictInt
    name : str
    startDate : date
    endDate : date 

class User(BaseModel):
    id : StrictInt
    lastName : str = Field(min_length=1)
    firstName : str = Field(min_length=1)
    nickname : Optional[str] = None
    email : Optional[EmailStr] = None
    edIsDefault : bool = True

class AcademicYear(BaseModel):
    id : StrictInt
    name : str
    startDate : date
    endDate : date

class UserRotation(BaseModel):
    id : StrictInt
    startDate : date
    endDate : date
    generationPeriod : Optional[GenerationPeriod] = None
    rotation : RotationType
    ay : AcademicYear

class Shift(BaseModel):
    
    shiftType : ShiftType
    user : Optional[User] = None

