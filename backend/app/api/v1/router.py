from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.auth_v2 import router as auth_v2_router
from app.api.v1.endpoints.users import router as users_router, roles_router, branches_router
from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.enquiries import router as enquiries_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.billing import router as billing_router
from app.api.v1.endpoints.subscription import router as subscription_router
from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.companies_v2 import router as companies_v2_router
from app.api.v1.endpoints.communications import router as communications_router

api_router = APIRouter(prefix="/api/v1")
# New v2 endpoints (multi-company, multi-role)
api_router.include_router(auth_v2_router)
api_router.include_router(companies_v2_router)
# Legacy endpoints
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(branches_router)
api_router.include_router(customers_router)
api_router.include_router(enquiries_router)
api_router.include_router(tasks_router)
api_router.include_router(billing_router)
api_router.include_router(subscription_router)
api_router.include_router(companies_router, prefix="/companies", tags=["companies"])
api_router.include_router(communications_router, prefix="/communications", tags=["communications"])
