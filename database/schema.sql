CREATE TABLE 'sensors' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'name' TEXT DEFAULT 'New sensor',
'description' TEXT DEFAULT NULL,
'date_installed' TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE 'log' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'timestamp' TEXT DEFAULT CURRENT_TIMESTAMP,
'sensor' INTEGER DEFAULT NULL REFERENCES 'sensors' ('id'),
'value' REAL DEFAULT NULL
);