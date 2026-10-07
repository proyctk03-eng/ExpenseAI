"""Router cho giao diện Web."""
import os
from typing import Optional
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from src.config import SECRET_KEY, ALGORITHM
from src.database import get_db
from src.models import User

router = APIRouter(tags=["web"])
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "templates"))
templates = Jinja2Templates(directory=templates_dir)


def _get_web_user(request: Request, db: Session) -> Optional[User]:
    """Helper lấy User từ cookie session cho Web routes."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except (JWTError, Exception):
        return None

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.get("/transactions", response_class=HTMLResponse)
def transactions_page(request: Request):
    return templates.TemplateResponse(request=request, name="transactions.html")

@router.get("/stats", response_class=HTMLResponse)
def stats_page(request: Request):
    return templates.TemplateResponse(request=request, name="stats.html")

@router.get("/budgets", response_class=HTMLResponse)
def budgets_page(request: Request):
    return templates.TemplateResponse(request=request, name="budgets.html")

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse(request=request, name="settings.html")

@router.get("/feedback", response_class=HTMLResponse)
@router.get("/support", response_class=HTMLResponse)
def feedback_page(request: Request):
    return templates.TemplateResponse(request=request, name="feedback.html")

@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    # S-FIX M-02: Server-side route guard cho trang admin
    user = _get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/admin", status_code=status.HTTP_303_SEE_OTHER)
    if not user.is_admin and not user.has_permission("*:*"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="admin.html")


# --- SE3: robots.txt ---
@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return """User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin
Disallow: /settings
Sitemap: /sitemap.xml
"""


# --- SE4: sitemap.xml ---
@router.get("/sitemap.xml", response_class=PlainTextResponse)
def sitemap_xml(request: Request):
    base_url = str(request.base_url).rstrip("/")
    pages = ["/", "/login", "/register", "/transactions", "/stats", "/budgets", "/feedback"]
    urls = "\n".join(
        f"""  <url>
    <loc>{base_url}{page}</loc>
    <changefreq>daily</changefreq>
    <priority>{"1.0" if page == "/" else "0.8"}</priority>
  </url>"""
        for page in pages
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
