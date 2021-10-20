To use most endpoints one must first log in to an account by sending a request to [/login](/login), with a JSON object containing two string properites "username" & "password". The server will respond with a session cookie that most accompany all future requests.
The permissions associated with the user information used to log in will determine what api endpoints can be used.


Each request must be made under the api base url, [/api](/api), so when this document specifies eg `/sensors/1` this refers to the path [/api/sensors/1](/api/sensors/1).


# logs api
A log is a reading of a sensor at a specific time.

Each log is commonly represented as an array of timestamp and value. However, a log also includes information on which use account created that log, which is determined by the session associated with the request.
An alternative representation of a log is an object with keys "value", "timestamp" and "source_user". Timestamp is inputted as an unix time integer and returned as a human readable string, it defaults to the current time if not specified. Source user is internally a user id and is inferred from the request. Value is a number read by the sensor.
```js
Log: [Number, Time]
   : {"value": Number, "timestamp": Time}
   : {"value": Number, "timestamp": Time, "source_user": UserId}
```

## `/logs/<sensor_id>/`
 
### GET
***required permission: "VIEW_LOGS"***
Returns an array of logged values each represented as an array of timestamp and value.
```js
[
	[Timestamp, Value],
	[Timestamp, Value],
	...
]
```
### POST
***required permission: "ADD_LOGS"***
Adds a timestamp value pair to the sensor's log
**Accepted body formats:**
 - `[Timestamp, Value>]`
 - `{"timestamp": Timestamp, "value": Value}`
 - *single type array of either of the above*
 -  `{"value": Value}` (timestamp will default to current time)
 
 where Value is a floating point number and Timestamp is an integer of the number of seconds between the sensor reading and the UNIX Epoch. 

## `/logs/<sensor_id>/last/`
### GET
***required permissions: "VIEW_LOGS"***
Returns the array representation of the most recent log of specified sensor.
``` [Timestamp, Value]```

# sensor api
```js
SensorId: Integer
Sensor: {
	"id": SensorId, 
	"name": String, 
	"description": String,
	"date_installed": Time,
	"update_frequency": Integer; /* time in deciseconds between updates */
}
```

## `/sensors/`
### GET
***required permission: signed in***
Returns an array of all sensors
```js
[ Sensor, Sensor, ...]
```

## `/sensors/<sensor_id>/`
### GET
***required permission: signed in***
Returns an object of the metadata of the specified sensor
```js
Sensor
```
### PATCH
***required permission: MANAGE_SENSORS***
Updates and returns the specified sensor

*Accepted request body format*:
```js
{
	"name"?: String,
	"description"?: String,
	"date_installed"?: Timestamp,
	"update_frequency"?: Integer 
}
```
(all parameters are optional)
Returns: `Sensor`

# permissions api
A permission is a string, each user has some set of associated permissions that allow them access to actions and a set of api endpoints. 
Currently the following permissions exist:
- MANAGE_PERMISSIONS
- CREATE_USERS
- DELETE_USERS
- MANAGE_SENSORS
- VIEW_LOGS
- ADD_LOGS
- EDIT_LOGS

New permissions currently must be added by changing the source code as their functionality is also determined statically in the code.
 
```js
Permission: String
```

### `/permissions/`
#### GET
***required permissions: MANAGE_PERMISSIONS***
returns an array of all recognised permissions
```js
[Permission, Permission, ...]
```

# users api
A user account is associated with an integer and a string, both are static values that can be used to uniquely identify the user. 
Each user also has a password, which is inaccessible through the api.
```js
UserId: Integer
Username: String

User: {"id": UserId, "username": Username}
```

## `/users/`
### GET
***required permissions:  signed in***
returns an array of the id and username of every registered user
```js
[User, User, ...]
```
note this array is *not* guarenteed to be in order of UserId

### POST
***required permissions:  CREATE_USERS***
Creates and returns a new user account
*Accepted request body format*
```js
{
	"username": Username,
	"password": String
}
```
Any additional properties will be ignored.
The UserId will be automatically assigned as an integer aabove any previously assigned UserId.
Note the username must be distinct from all other preexisting usernames.

Returns: `User`

## `/users/<username>`
### GET
***required permissions:  signed in***
Returns the username and id of specified user
```js
User
```

### DELETE
***required permissions: DELETE_USER***
Will delete a user as long as the calling user has a lower UserId than the user to be deleted. In other words, you can only delete accounts *created after your own*.

## `/users/<username>/permissions`
### GET
***required permissions: MANAGE_PERMISSIONS***
Returns an array of all permissions a user has 
```js
[Permission, Permission, ...]
```

### POST
***required permissions: MANAGE_PERMISSIONS***
Provided the calling user has a UserId less than the affected user, this will grant the specified user a permission.
One can only add permissions to users created after oneself, however you do not need to personally have the permission added. As such, the MANAGE_PERMISSIONS permission should be treated as a form of administrator, as it indirectly enables for all other permissions if one has access to a subordinate user (or the ability to CREATE_USERS).

*Accepted request body format:*
```js
Permission
```
Returns: `Permission`

## `/users/<username>/permissions/<permission>`
### GET
***required permissions: MANAGE_PERMISSIONS***
returns the relationship between a user and permission if it exists.
```js
{
	"user": User,
	"permission": {
		"name": Permission,
		"id": PermissionId // Integer
	}
}
```

### DELETE
***required permissions: MANAGE_PERMISSIONS***
Removes a permission from a user. May only be called on users with a greater UserId than the calling User, you can only remove permissions from users created after your own user account.
