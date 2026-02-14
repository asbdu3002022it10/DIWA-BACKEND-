from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
# Inga unga database file name 'database' nu irundha ippadiye vachukonga
from database import SessionLocal, engine, Base 
# Inga unga model file name 'models' nu irundha ippadiye vachukonga
from models import Employee 
import schemas # Neenga ippo create panna schemas.py

# DB-la table create panna
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Database connect panna dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. POST - New Employee Submit
@app.post("/submit-employee", response_model=schemas.EmployeeResponse)
def submit_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    try:
        new_emp = Employee(**emp.model_dump()) # model_dump() is better in latest Pydantic
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
        return new_emp
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database insertion failed")

# 2. GET - Fetch by Name and ID
@app.get("/employees/{emp_name}/{emp_id}", response_model=schemas.EmployeeResponse)
def read_employee_details(emp_name: str, emp_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(
        Employee.id == emp_id, 
        Employee.emp_name == emp_name
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found!")
    return employee

# 3. PUT - Update Details
@app.put("/employees/update/{emp_id}", response_model=schemas.EmployeeResponse)
def update_employee(emp_id: int, emp_data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update logic - values anupunatha mattum update pannum
    update_data = emp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_emp, key, value)
    
    db.commit()
    db.refresh(db_emp)
    return db_emp

# 4. DELETE - Remove Record
@app.delete("/employees/delete/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(db_emp)
    db.commit()
    return {"message": f"Employee {emp_id} deleted successfully"}