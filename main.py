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




@app.get("/users/me")
def read_current_user(username: str = Depends(verify_credential)):
    return {"username": username}


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