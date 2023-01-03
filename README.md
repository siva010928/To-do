
# To-do 

A Basic To-do list API that uses REST API,authentication and implementation of CRUD functionalities using FastAPI as framework and database as MySQL with secured authenticated RESTAPI end-points.




## Appendix

- database.py
- models.py
- schemas.py
- main.py



## Installation

Install TO-DO with pip

```bash
  cd TO-DO
  pip install requirements.txt
  uvicorn main:app --reload
```
    
## Usage
Swagger UI
Fast API provides an interactive API that’s brought to us by swagger UI. I’ll save myself from explaining swagger UI and instead will provide a link if you want to check it out, but trust me, it’s pretty cool.

To see it in action, add /docs# to the end of the URL we set for our first route.

http://127.0.0.1:8000/docs#

This will give you a cool UI to work with so you can interact with your API and get more information than just some data. This will list out all your routes as you add them.

To test things out, click on the route that is currently available and then click “try it out” and then “execute.”

## AUNTHENTICATION

You can see additional Authorize green button in  http://127.0.0.1:8000/docs#  page with the  interactive APIs. you can't execute a APIs without proper AUNTHENTICATION you should authorize first with correct credential even-though you already logged in with correct credentials.

### main.py

```python
from fastapi import Depends, FastAPI,HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import SessionLocal
from sqlalchemy.orm import Session
import schemas,secrets,models

app = FastAPI()
security = HTTPBasic()


# For the simplest cases, you can use HTTP Basic Auth.
# In HTTP Basic Auth, the application expects a header that contains a username and a password.
# If it doesn't receive it, it returns an HTTP 401 "Unauthorized" error.

# we want to secure those APIs implemented in this app where attacker can modify data through API-request


# this method ensures wheather credential entered by the user valid or not 
# correct-username: siva
# correct-password: 123

def verify_credential(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"siva"
    
    # secrets.compare_digest() needs to take bytes or a str that only contains ASCII characters 
    # (the ones in English), this means it wouldn't work with characters.

    # To handle that, we first convert the username and password to bytes encoding them with UTF-8.
    # Then we can use secrets.compare_digest() to ensure that correct username and password.
    
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"123"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username



# this method return local database session that acts as current database
def get_session():
    session=SessionLocal()
    try:
        yield session
    finally:
        session.close()


# In the following APIs we use HTTPBasicCredentials as parameter 
# to ensure API security through verify_credential method


# to get all the tasks created by user

@app.get("/")
def getTasks(credentials: HTTPBasicCredentials = Depends(security),session: Session = Depends(get_session)):
    verify_credential(credentials)
    Tasks = session.query(models.Task).all()
    return Tasks


# to get a task based on primary key
@app.get("/{id}")
def getTask(id:int, session: Session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    Task = session.query(models.Task).get(id)
    return Task


# to create a task with a given parameter string
@app.post("/")
def addTask(Task:schemas.Task, session: Session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    Task = models.Task(task = Task.task)
    session.add(Task)
    session.commit()
    session.refresh(Task)
    return Task

# to update a task with primary id and string
@app.put("/{id}")
def updateTask(id:int, Task:schemas.Task, session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    TaskObject = session.query(models.Task).get(id)
    TaskObject.task = Task.task
    session.commit()
    return TaskObject

# to delete a task with primary id 
@app.delete("/{id}")
def deleteTask(id:int, session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    TaskObject = session.query(models.Task).get(id)
    session.delete(TaskObject)
    session.commit()
    session.close()
    return 'Task was deleted'
```

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Create sqlite engine instance
engine = create_engine("sqlite:///todo.db")

#Create declaritive base meta instance
Base = declarative_base()

#Create session local class for session maker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

### models.py

```python
from sqlalchemy import Column, Integer, String
from database import Base
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    task = Column(String(256))
```

### schemas.py

```python
from pydantic import BaseModel

class Task(BaseModel):
    task: str
    
```
