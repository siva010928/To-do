from fastapi import Depends, FastAPI,HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import SessionLocal
from sqlalchemy.orm import Session
import schemas,secrets,models

app = FastAPI()
security = HTTPBasic()

def verify_credential(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"siva"
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


def get_session():
    session=SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/")
def getTasks(credentials: HTTPBasicCredentials = Depends(security),session: Session = Depends(get_session)):
    verify_credential(credentials)
    Tasks = session.query(models.Task).all()
    return Tasks


@app.get("/{id}")
def getTask(id:int, session: Session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    Task = session.query(models.Task).get(id)
    return Task


@app.post("/")
def addTask(Task:schemas.Task, session: Session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    Task = models.Task(task = Task.task)
    session.add(Task)
    session.commit()
    session.refresh(Task)
    return Task

@app.put("/{id}")
def updateTask(id:int, Task:schemas.Task, session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    TaskObject = session.query(models.Task).get(id)
    TaskObject.task = Task.task
    session.commit()
    return TaskObject

@app.delete("/{id}")
def deleteTask(id:int, session = Depends(get_session),credentials: HTTPBasicCredentials = Depends(security)):
    verify_credential(credentials)
    TaskObject = session.query(models.Task).get(id)
    session.delete(TaskObject)
    session.commit()
    session.close()
    return 'Task was deleted'