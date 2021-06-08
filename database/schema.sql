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
'value' REAL DEFAULT NULL,
'source_user' INTEGER DEFAULT NULL REFERENCES 'users' ('id')
);

CREATE TABLE 'users' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'username' TEXT DEFAULT NULL,
'password_hash' TEXT DEFAULT NULL
);

CREATE TABLE 'user_permissions' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'user_id' INTEGER DEFAULT NULL REFERENCES 'users' ('id'),
'permission_id' INTEGER DEFAULT NULL REFERENCES 'permissions' ('id')
);

CREATE TABLE 'permissions' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'permission_name' INTEGER DEFAULT NULL
);


INSERT INTO 'users' ('username') VALUES ('SYSTEM');
INSERT INTO 'permissions' ('permission_name') VALUES ('MANAGE_PERMISSIONS');
INSERT INTO 'user_permissions' ('user_id', 'permission_id') VALUES (1, 1);
INSERT INTO 'permissions' ('permission_name') VALUES ('CREATE_USERS');
INSERT INTO 'user_permissions' ('user_id', 'permission_id') VALUES (1, 2);
INSERT INTO 'permissions' ('permission_name') VALUES ('DELETE_USERS');
INSERT INTO 'user_permissions' ('user_id', 'permission_id') VALUES (1, 3);
INSERT INTO 'permissions' ('permission_name') VALUES ('MANAGE_SENSORS');
INSERT INTO 'user_permissions' ('user_id', 'permission_id') VALUES (1, 4);

