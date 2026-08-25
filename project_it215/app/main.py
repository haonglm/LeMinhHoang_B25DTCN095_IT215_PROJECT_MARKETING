from fastapi import FastAPI , Request, status, HTTPException
from fastapi.responses import JSONResponse

from routers import auth, users, campaign, campaign_task
from db import engine, Base
import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def test_connect():
    return {
        "message": "api running"
    }

# health check endpoint
@app.get("/heath", status_code=status.HTTP_200_OK, tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "message": "service is up and running"
    }

# xử lý format lỗi thống nhất
@app.exception_handler(HTTPException)
def custom_http_exception_handle(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code= exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error_detail": exc.detail
        }
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(campaign.router)
app.include_router(campaign_task.router)