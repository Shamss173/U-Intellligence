"""
Department router
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.department import Department
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter()

# UBL Departments
UBL_DEPARTMENTS = [
    {"code": "branch_banking", "name": "Branch Banking", "description": "Branch Banking operations and procedures"},
    {"code": "audit_risk", "name": "Audit and Risk Review", "description": "Audit and risk management procedures"},
    {"code": "compliance", "name": "Compliance", "description": "Compliance policies and procedures"},
    {"code": "cibg", "name": "CIBG", "description": "Corporate and Investment Banking Group"},
    {"code": "digital_banking", "name": "Digital Banking Group", "description": "Digital banking services and operations"},
    {"code": "finance", "name": "Finance", "description": "Financial management and accounting procedures"},
    {"code": "hrg", "name": "Human Resource Group", "description": "Human resources policies and procedures"},
    {"code": "it", "name": "Information Technology", "description": "IT operations and technology policies"},
    {"code": "islamic_banking", "name": "Islamic Banking", "description": "Islamic banking products and procedures"},
    {"code": "legal_secretary", "name": "Legal and Secretary Dept", "description": "Legal and secretarial services"},
    {"code": "operations_transformation", "name": "Operations and Transformation", "description": "Operations and transformation initiatives"},
    {"code": "risk_credit", "name": "Risk and Credit Policy", "description": "Risk management and credit policies"},
    {"code": "shared_services", "name": "Shared Services Group", "description": "Shared services operations"},
    {"code": "special_assets", "name": "Special Assets Management", "description": "Special assets and recovery management"},
    {"code": "treasury_capital", "name": "Treasury and Capital Markets", "description": "Treasury operations and capital markets"},
    {"code": "ubl_international", "name": "UBL International", "description": "International banking operations"},
    {"code": "consumer_banking", "name": "Consumer Banking Group", "description": "Consumer banking products and services"},
]


@router.get("/", response_model=List[dict])
async def get_departments(db: Session = Depends(get_db)):
    """Get all available departments"""
    # Initialize departments if not exists
    existing_departments = db.query(Department).all()
    if not existing_departments:
        for dept in UBL_DEPARTMENTS:
            db_dept = Department(**dept)
            db.add(db_dept)
        db.commit()
        db.refresh_all()
    
    departments = db.query(Department).all()
    return [
        {
            "id": dept.id,
            "code": dept.code,
            "name": dept.name,
            "description": dept.description
        }
        for dept in departments
    ]


@router.get("/{department_code}")
async def get_department(department_code: str, db: Session = Depends(get_db)):
    """Get specific department by code"""
    department = db.query(Department).filter(Department.code == department_code).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {
        "id": department.id,
        "code": department.code,
        "name": department.name,
        "description": department.description
    }

