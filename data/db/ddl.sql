CREATE TABLE ShiftType (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    startHour INTEGER NOT NULL,
    startMinute INTEGER NOT NULL,
    durationMinutes INTEGER NOT NULL,
    postBufferMins INTEGER NOT NULL,
    isClinical INTEGER NOT NULL,
    isCounted INTEGER NOT NULL,
    isNight INTEGER NOT NULL
);

CREATE TABLE RotationType (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    preBufferMins INTEGER NOT NULL,
    postBufferMins INTEGER NOT NULL,
    isDefault INTEGER NOT NULL
);

CREATE TABLE GenerationPeriod (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    
    startYear INTEGER NOT NULL,
    startMonth INTEGER NOT NULL,
    startDay INTEGER NOT NULL,

    durationDays INTEGER NOT NULL
);

CREATE TABLE UserRotation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startYear INTEGER NOT NULL,
    startMonth INTEGER NOT NULL,
    startDay INTEGER NOT NULL,
    durationDays INTEGER NOT NULL,
    generationPeriodId INTEGER,
    rotationTypeId INTEGER,
    academicYearId INTEGER,
    FOREIGN KEY (generationPeriodId)
        REFERENCES GenerationPeriod (id)
    FOREIGN KEY (rotationTypeId)
        REFERENCES RotationType (id)
    FOREIGN KEY (academicYearId)
        REFERENCES AcademicYear (id)
);

CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lastName TEXT NOT NULL,
    firstName TEXT NOT NULL,
    nickname TEXT,
    email TEXT,
    edIsDefault INTEGER NOT NULL
);

CREATE TABLE AcademicYear (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    startYear INTEGER NOT NULL,
    startMonth INTEGER NOT NULL,
    startDay INTEGER NOT NULL,
    durationDays INTEGER NOT NULL
);

CREATE TABLE RotationTypeToShiftType (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rotationTypeId INTEGER,
    shiftTypeId INTEGER,
    FOREIGN KEY (rotationTypeId)
        REFERENCES RotationType (id)
    FOREIGN KEY (shiftTypeId)
        REFERENCES ShiftType (id)
);