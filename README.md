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
5. 