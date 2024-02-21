from pydantic import BaseModel, Field, computed_field, StrictInt, EmailStr
from typing import List, Optional, Union, Literal, Dict
from datetime import datetime, date, time, timedelta
from enum import Enum

class DayOfWeek(Enum):
    Mon = 'Mon'
    Tue = 'Tue'
    Wed = 'Wed'
    Thu = 'Thu'
    Fri = 'Fri'
    Sat = 'Sat'
    Sun = 'Sun'

ALL_DAYS_OF_WEEK = list(DayOfWeek)

class Rule(BaseModel):
    name : str
    description : str = ''

class ShiftRule(Rule):
    pass

class UserRule(Rule):
    pass

class ShiftType(BaseModel):
    name : str
    # shortName : str
    startTime : timedelta
    duration: timedelta
    postBuffer : timedelta = timedelta(seconds=0)

    isClinical : bool = True
    isCounted : bool = True
    isNight : bool = False

    shiftRules : Optional[List[ShiftRule]] = None

class StaffingRule(ShiftRule):
     minStaffing : StrictInt
     maxStaffing : StrictInt

class WeeklyStaffingRule(StaffingRule):
    appliesToDays : List[DayOfWeek] = ALL_DAYS_OF_WEEK
    minStaffing : Union[StrictInt, Dict[DayOfWeek, StrictInt]]
    maxStaffing : Union[StrictInt, Dict[DayOfWeek, StrictInt]]

class DayOfMonthStaffingRule(StaffingRule):
    dayOfMonth : timedelta

class CustomDateStaffingRule(StaffingRule):
    '''Set specific staffing for a certain shift on a certain day'''
    customDate: date

class WorkloadRule(UserRule):
    pass

class RotationType(BaseModel):
    name : str
    abbrv : Optional[str] = None
    preBufferHours : int = 0
    postBufferHours : int = 0
    schedulableShifts : Union[Optional[List[ShiftType]], Literal['all']] = 'all'

class ScheduledRotation(BaseModel):
    rotationType : RotationType
    startDate : date
    endDate : date

class User(BaseModel):
    firstName : str = Field(min_length=1)
    lastName : str = Field(min_length=1)
    email : EmailStr

    @computed_field
    @property
    def schedName(self) -> str:
        return self.firstName[0] + ' ' + self.lastName

class Shift(BaseModel):
    shiftType : ShiftType
    startDate : date
    assignedUser : Optional[User] = None

import pandas as pd

if __name__ == '__main__':
    shifts_csv = pd.read_csv('data/shifts.csv')
    # shifts_csv['startTime'] = pd.to_timedelta(shifts_csv['startTime'])
    shifts = [ShiftType(**r.to_dict()) for _, r in shifts_csv.iterrows()]
    print(shifts)
