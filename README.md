# Isaac Perez

# Database used
MySQL - MySQL workbench

# How to run
1. Create a virtual environment in a secure folder: python3 -m venv env
2. Download the required libraries with "pip install..."
    - pymysql
    - sqlalchemy
    - fastapi
    - pydantic
    - uvicorn
3. In the SQL workbench, copy the database as is in the CloudService.sql file.
4. run the code with 'uvicorn main:app --reload'

# How to run each API endpoint

- [POST]http://127.0.0.1:8000/admin/plans

In JSON format provide this body text:

{
    "name": {plan_name}
    "description": {description}
    "permission": {list of permissions from api's}
    "usage_limit": {usage_limit}
}

It will automatically assign an id number to it.

- [DELETE]http://127.0.0.1:8000/admin/plans/{plan_id}

Replace the {plan_id} with the id number saved in the table made previously.

- [POST]http://127.0.0.1:8000/admin/permissions

In JSON format provide this body text:
{
    "name": {api_name},
    "api_endpoint": {api_endpoint},
    "description": {description}
}

It will automatically assign an id number to it.

- [DELETE]http://127.0.0.1:8000/admin/permission/{permission_id}

Replace the {plan_id} with the id number saved in the table made previously.

- [POST]http://127.0.0.1:8000/admin/subscriptions

In JSON format provide this body text:

{
  "user_id": {username},
  "plan_id": {plan_id}
}

- [PUT]http://127.0.0.1:8000/admin/subscription/{user_id}?new_plan_id={plan_id}

In the api, replace {user_id} with the already made username and {plan_id} with the already made plan_id number.

- [PUT]http://127.0.0.1:8000/admin/users/{user_id}/reset-usage

Replace {user_id} with the username to reset the limit that the user can access the granted api's.

- [GET]http://127.0.0.1:8000/access/{api_name}?user_id={user_id}

Replace {api_name} with the api you want to access such as "weather_api" and {user_id} with the username.
