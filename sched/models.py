from pydantic import BaseModel, Field, computed_field, StrictInt
from typing import List, Optional, Union, Literal
from datetime import datetime, date, time, timedelta
from enum import Enum

class User(BaseModel):
    firstName : str = Field(min_length=1)
    lastName : str = Field(min_length=1)

    @computed_field
    @property
    def schedName(self) -> str:
        return self.firstName[0] + ' ' + self.lastName
    
class Shift(BaseModel):
    name : str
    # shortName : str
    startTime : timedelta
    lengthHours : StrictInt

class Rotation(BaseModel):
    name : str 
    preBufferHours : int = 0
    postBufferHours : int = 0
    schedulableShifts : Union[Optional[List[Shift]], Literal['all']] = 'all'

class EDRotation(Rotation):
    schedulableShifts : Literal['all'] = 'all'
    preBufferHours : Literal[0] = 0
    postBufferHours : Literal[0] = 0

class OffServiceRotation(Rotation):
    schedulableShifts : List[Shift] = []
    preBufferHours : int = 12
    postBufferHours : int = 24

class Shifts(Enum):
    JAM = Shift(name='J AM', startTime=timedelta(hours=7), lengthHours=12),
    JPM = Shift(name='J PM', startTime=timedelta(hours=19), lengthHours=12),
    UX = Shift(name='UX', startTime=timedelta(hours=7), lengthHours=8),
    UG = Shift(name='UG', startTime=timedelta(hours=22), lengthHours=9)

class JeopardyOnlyRotation(Rotation):
    schedulableShifts : List[Shift] = [Shifts.JAM, Shifts.JPM]

icu_rotations = {
    r : OffServiceRotation(name=r)
    for r in ['PICU','MICU','CCMU','CVCICU','CICU','TBICU','NICU']
}
us_rotations = {
    r : JeopardyOnlyRotation(name=r)
    for r in ['US1','US2']
}
ed_rotations = {
    r : EDRotation(name=r)
    for r in ['ED']
}
rotations = dict(**icu_rotations, **us_rotations, **ed_rotations)


if __name__ == "__main__":
    m = User(firstName='Max', lastName='Spadafore')
    print(rotations)
    # UG = Shift(name='UG', shortName='UG', startTime=timedelta(hours=22), endTime=timedelta(hours=22+9))
    # ED = Rotation(name='ED')
    # PICU = Rotation(name='PICU', preBufferHours=12, postBufferHours=24, schedulableShifts=[])
