from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List
import asyncio

app = FastAPI()

# Database setup
DATABASE_URL = "mysql+pymysql://root:Csdegree2002!@localhost:3306/CloudService" # change 'root', 'Csdegree2002!', 'Cloudservice' with correct username, password, and database name
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models that take the tables from database
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    api_permissions = Column(String)  # list of API names, comma seperated
    usage_limit = Column(Integer)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    api_endpoint = Column(String)
    description = Column(String)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    usage_count = Column(Integer, default=0)
    plan = relationship("SubscriptionPlan")

# creates the tables
Base.metadata.create_all(bind=engine)

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class PlanCreate(BaseModel):
    name: str
    description: str
    api_permissions: List[str]
    usage_limit: int

class PermissionCreate(BaseModel):
    name: str
    api_endpoint: str
    description: str

class SubscriptionUpdate(BaseModel):
    user_id: str
    plan_id: int

# Management APIs
@app.post("/admin/plans", response_model=dict)
async def create_plan(plan: PlanCreate, db: SessionLocal = Depends(get_db)):
    # This endpoint allows admins to create new subscription plans.
    try:
        db_plan = SubscriptionPlan(
            name=plan.name,
            description=plan.description,
            api_permissions=','.join(plan.api_permissions),
            usage_limit=plan.usage_limit
        )
        db.add(db_plan)
        db.commit()
        return {"message": "Plan created successfully."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Plan already exists.")

# deletes the subsrciption plan
@app.delete("/admin/plans/{plan_id}", response_model=dict)
async def delete_plan(plan_id: int, db: SessionLocal = Depends(get_db)):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found.")

    # finds users with this deleted plan
    users_with_plan = db.query(UserSubscription).filter(UserSubscription.plan_id == plan_id).all()
    default_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "Free Plan").first()

    if not default_plan:
        raise HTTPException(status_code=500, detail="Default plan not found. Create a 'Free Plan' first.")

    # Update users to the default plan
    for user_subscription in users_with_plan:
        user_subscription.plan_id = default_plan.id
        user_subscription.usage_count = 0
        db.commit()

    # Delete the plan
    db.delete(plan)
    db.commit()
    return {"message": f"Subscription plan with ID {plan_id} deleted and affected users updated to 'Free Plan'."}

# creates permissions
@app.post("/admin/permissions", response_model=dict)
async def create_permission(permission: PermissionCreate, db: SessionLocal = Depends(get_db)):
    try:
        db_permission = Permission(
            name=permission.name,
            api_endpoint=permission.api_endpoint,
            description=permission.description
        )
        db.add(db_permission)
        db.commit()
        return {"message": "Permission created successfully."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Permission already exists.")

# deletes permission 
@app.delete("/admin/permissions/{permission_id}", response_model=dict)
async def delete_permission(permission_id: int, db: SessionLocal = Depends(get_db)):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")

    permission_name = permission.name
    db.delete(permission)
    db.commit()

    # Update plans to remove the deleted permission
    update_plans_after_permission_deletion(permission_name, db)

    return {"message": f"Permission with ID {permission_id} deleted successfully."}

def update_plans_after_permission_deletion(permission_name: str, db):
    plans = db.query(SubscriptionPlan).all()
    for plan in plans:
        permissions = plan.api_permissions.split(',')
        if permission_name in permissions:
            permissions.remove(permission_name)
            plan.api_permissions = ','.join(permissions)
            db.commit()

# assigns subscription plan to user
@app.post("/admin/subscriptions", response_model=dict)
async def assign_subscription(subscription: SubscriptionUpdate, db: SessionLocal = Depends(get_db)):
    db_subscription = UserSubscription(
        user_id=subscription.user_id,
        plan_id=subscription.plan_id
    )
    db.add(db_subscription)
    db.commit()
    return {"message": "Subscription assigned successfully."}

# updates user subscription plan to the provided id number
@app.put("/admin/users/subscription/{user_id}", response_model=dict)
async def update_user_subscription(user_id: str, new_plan_id: int, db: SessionLocal = Depends(get_db)):
    user_subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    new_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == new_plan_id).first()
    if not new_plan:
        raise HTTPException(status_code=404, detail="New subscription plan not found.")

    user_subscription.plan_id = new_plan_id
    user_subscription.usage_count = 0  # Reset usage count
    db.commit()
    return {"message": f"User {user_id}'s subscription updated to plan ID {new_plan_id}."}

# resets specified user's usage count
@app.put("/admin/users/{user_id}/reset-usage", response_model=dict)
async def reset_user_usage(user_id: str, db: SessionLocal = Depends(get_db)):
    user_subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    user_subscription.usage_count = 0
    db.commit()
    return {"message": f"Usage count reset for user {user_id}."}

# provides access to the api name wanted according to the assigned plan
@app.get("/access/{api_name}", response_model=dict)
async def access_api(api_name: str, user_id: str, db: SessionLocal = Depends(get_db)):
    user_subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not user_subscription:
        raise HTTPException(status_code=403, detail="No subscription found.")

    plan = user_subscription.plan
    if api_name not in plan.api_permissions.split(','):
        raise HTTPException(status_code=403, detail="Access denied for this API.")

    if user_subscription.usage_count >= plan.usage_limit:
        raise HTTPException(status_code=403, detail="Usage limit exceeded.")

    user_subscription.usage_count += 1
    db.commit()
    return {"message": f"Access granted to {api_name}."}

# Random APIs
@app.get("/api/weather")
async def weather_api():
    return {"weather": "hot"}

@app.get("/api/stocks")
async def stocks_api():
    return {"stocks": "making money"}

@app.get("/api/news")
async def news_api():
    return {"news": "breaking news"}

@app.get("/api/games")
async def games_api():
    return {"games": "Playstation and Nintendo"}

@app.get("/api/sports")
async def sports_api():
    return {"sports": "watch live"}

@app.get("/api/movies")
async def movies_api():
    return {"movies": "top movies"}
