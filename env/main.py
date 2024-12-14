from fastapi import FastAPI,Path,Query
from typing import List
from pydantic import BaseModel,Field
import asyncio

app=FastAPI()

class Student(BaseModel):
    id:int
    name:str = Field(max_length=6) 
    subjects:List[str]

student_data={"id":"1","name":"Jainis","subjects":["xyz","abc"]}

@app.get("/")
def index():
    try:
        student = Student(**student_data)
        print(student)
        return {"Hello":"world","data":student}
    except Exception as e:
        return {"error":str(e)}

@app.get("/div/{a}/{b}")
def div(a:int,b:int,cities:List[int]=Query([1,2])):
    return {"DIV":a/b,"cities":cities}

@app.get("/data/{name}/{age}")
def data(name:str = Path(min_length=3,max_length=6),age:int = Path(ge=18,le=25),perc:int = Query(ge=1,le=100)):
    return {"Name":name,"age":age,"Perc":perc}


async def other_function():
    print("other function starts")
    await asyncio.sleep(2)
    print("other function ends")

async def someother_function():
    print("someother function starts")
    await asyncio.sleep(10)
    print("someother function ends")

@app.get("/main")
async def main():
    print("main method is call")
    task = asyncio.create_task(other_function())
    task1= asyncio.create_task(someother_function())
    await task
    await task1
    print("main method is ended")


