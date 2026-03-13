"""
routers/auth.py  (B.12)
JWT Authentication Router

Endpoints:
    POST /api/auth/register        — Create a new disaster-manager account
    POST /api/auth/login           — Obtain access + refresh tokens
    POST /api/auth/refresh         — Exchange refresh token for new access token
    GET  /api/auth/me              — Get current user profile
    PUT  /api/auth/me              — Update profile (name, org)
    GET  /api/auth/simulations     — List simulations owned by current user
    GET  /api/auth/export/{sim_id} — Export simulation result as PDF

Roles:
    admin   — full access, user management
    manager — create/run simulations, export reports
    viewer  — read-only access to results
"""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.auth.jwt_handler import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user, require_admin,
)
from app.database import get_db

router = APIRouter()


# ─── Pydantic schemas ─────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name:    str
    email:        EmailStr
    password:     str = Field(min_length=8)
    organisation: Optional[str] = None
    role:         str = "manager"          # admin | manager | viewer

class UserOut(BaseModel):
    id:           str
    full_name:    str
    email:        str
    role:         str
    organisation: Optional[str]
    created_at:   str

class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class ProfileUpdate(BaseModel):
    full_name:    Optional[str]
    organisation: Optional[str]


# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserRegister):
    db = get_db()

    # Prevent duplicate emails
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(400, "Email already registered.")

    # Only allow 'admin' role assignment by existing admins (simplified: open for manager/viewer)
    if data.role == "admin":
        raise HTTPException(403, "Cannot self-register as admin. Contact system administrator.")

    user_doc = {
        "full_name":    data.full_name,
        "email":        data.email,
        "hashed_pw":    hash_password(data.password),
        "role":         data.role,
        "organisation": data.organisation,
        "created_at":   datetime.utcnow().isoformat(),
        "is_active":    True,
    }
    result = await db.users.insert_one(user_doc)
    return UserOut(
        id           = str(result.inserted_id),
        full_name    = data.full_name,
        email        = data.email,
        role         = data.role,
        organisation = data.organisation,
        created_at   = user_doc["created_at"],
    )


# ─── Login ────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """Standard OAuth2 password flow — username field carries email."""
    db   = get_db()
    user = await db.users.find_one({"email": form.username})

    if not user or not verify_password(form.password, user["hashed_pw"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.get("is_active", True):
        raise HTTPException(403, "Account is deactivated.")

    token_data = {
        "sub":   str(user["_id"]),
        "email": user["email"],
        "role":  user["role"],
        "name":  user["full_name"],
    }
    return TokenResponse(
        access_token  = create_access_token(token_data),
        refresh_token = create_refresh_token(token_data),
    )


# ─── Refresh token ────────────────────────────────────────────────────────────
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Expected refresh token.")

    token_data = {
        "sub":   payload["sub"],
        "email": payload["email"],
        "role":  payload["role"],
        "name":  payload.get("name", ""),
    }
    return TokenResponse(
        access_token  = create_access_token(token_data),
        refresh_token = create_refresh_token(token_data),
    )


# ─── Current user profile ─────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
async def get_profile(current: dict = Depends(get_current_user)):
    db   = get_db()
    user = await db.users.find_one({"_id": ObjectId(current["sub"])})
    if not user:
        raise HTTPException(404, "User not found.")
    return UserOut(
        id           = str(user["_id"]),
        full_name    = user["full_name"],
        email        = user["email"],
        role         = user["role"],
        organisation = user.get("organisation"),
        created_at   = user.get("created_at", ""),
    )


@router.put("/me", response_model=UserOut)
async def update_profile(body: ProfileUpdate,
                          current: dict = Depends(get_current_user)):
    db = get_db()
    update = {k: v for k, v in body.dict().items() if v is not None}
    if update:
        await db.users.update_one(
            {"_id": ObjectId(current["sub"])},
            {"$set": update}
        )
    user = await db.users.find_one({"_id": ObjectId(current["sub"])})
    return UserOut(
        id           = str(user["_id"]),
        full_name    = user["full_name"],
        email        = user["email"],
        role         = user["role"],
        organisation = user.get("organisation"),
        created_at   = user.get("created_at", ""),
    )


# ─── User's simulations ───────────────────────────────────────────────────────
@router.get("/simulations")
async def list_my_simulations(current: dict = Depends(get_current_user)):
    """Return all simulation runs created by the current user."""
    db   = get_db()
    docs = await db.simulations.find(
        {"owner_id": current["sub"]},
        {"_id": 1, "config.name": 1, "status": 1, "created_at": 1}
    ).to_list(length=100)
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"simulations": docs, "count": len(docs)}


# ─── Export simulation as PDF ─────────────────────────────────────────────────
@router.get("/export/{sim_id}")
async def export_simulation_pdf(sim_id: str,
                                 current: dict = Depends(get_current_user)):
    """
    Generate a PDF report for a simulation run.
    Uses ReportLab to build a structured document with:
        - Simulation config summary
        - Method comparison table
        - Cost breakdown
        - Key metrics
    """
    db  = get_db()
    doc = await db.simulations.find_one({"_id": ObjectId(sim_id)})
    if not doc:
        raise HTTPException(404, "Simulation not found.")
    if doc.get("owner_id") != current["sub"] and current.get("role") != "admin":
        raise HTTPException(403, "Access denied.")

    pdf_bytes = _build_pdf(doc)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="simulation_{sim_id}.pdf"'
        }
    )


def _build_pdf(sim_doc: dict) -> bytes:
    """Build PDF bytes using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle)
        from reportlab.lib.units import cm
        import io

        buf    = io.BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=A4,
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        # ── Title ────────────────────────────────────────────────────────────
        title_style = ParagraphStyle("title", parent=styles["Title"],
                                      textColor=colors.HexColor("#1a5276"),
                                      fontSize=18, spaceAfter=12)
        story.append(Paragraph("Flood Relief Simulation Report", title_style))
        story.append(Paragraph(
            f"Simulation: {sim_doc.get('config', {}).get('name', 'N/A')}",
            styles["Heading2"]
        ))
        story.append(Paragraph(
            f"Status: {sim_doc.get('status', 'N/A')}  |  "
            f"Created: {sim_doc.get('created_at', 'N/A')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.5*cm))

        # ── Config table ─────────────────────────────────────────────────────
        cfg = sim_doc.get("config", {})
        config_data = [
            ["Parameter", "Value"],
            ["Case Study",          cfg.get("case_study", "—")],
            ["Districts",           ", ".join(cfg.get("selected_districts", []))],
            ["Planning Horizon",    f"{cfg.get('n_periods', '—')} periods"],
            ["Period Length",       f"{cfg.get('period_hours', '—')} hours"],
            ["Truck Capacity",      f"{cfg.get('truck_capacity', '—')} units"],
            ["UAV Capacity",        f"{cfg.get('uav_capacity', '—')} units"],
            ["Training Episodes",   str(cfg.get('n_training_episodes', '—'))],
        ]
        story.append(Paragraph("Simulation Configuration", styles["Heading3"]))
        config_tbl = Table(config_data, colWidths=[7*cm, 9*cm])
        config_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#2e86c1")),
            ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID",         (0,0), (-1,-1), 0.5, colors.grey),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#eaf4fb")]),
            ("FONTSIZE",     (0,0), (-1,-1), 10),
            ("PADDING",      (0,0), (-1,-1), 6),
        ]))
        story.append(config_tbl)
        story.append(Spacer(1, 0.5*cm))

        # ── Results table ─────────────────────────────────────────────────────
        results = sim_doc.get("results", [])
        if results:
            story.append(Paragraph("Method Comparison", styles["Heading3"]))
            res_data = [["Method", "Total Cost", "Dep. Cost", "Trans. Cost", "Max Dep. Time"]]
            for r in results:
                res_data.append([
                    r.get("method",               "—"),
                    f"{r.get('total_cost',       0):.1f}",
                    f"{r.get('deprivation_cost', 0):.1f}",
                    f"{r.get('transport_cost',   0):.1f}",
                    str(r.get("max_deprivation_time", "—")),
                ])
            res_tbl = Table(res_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3*cm])
            res_tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#1e8449")),
                ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
                ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID",         (0,0), (-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#eafaf1")]),
                ("FONTSIZE",     (0,0), (-1,-1), 9),
                ("PADDING",      (0,0), (-1,-1), 5),
            ]))
            story.append(res_tbl)

        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            "Generated by Flood Relief India AI Engine",
            ParagraphStyle("footer", parent=styles["Normal"],
                            textColor=colors.grey, fontSize=8)
        ))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        # Fallback: return a plain-text PDF header if ReportLab not installed
        return (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"% ReportLab not installed. Install with: pip install reportlab\n"
        )


# ─── Admin: list all users ────────────────────────────────────────────────────
@router.get("/users", dependencies=[Depends(require_admin)])
async def list_all_users():
    db   = get_db()
    docs = await db.users.find(
        {}, {"_id": 1, "full_name": 1, "email": 1, "role": 1, "created_at": 1}
    ).to_list(length=500)
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"users": docs, "count": len(docs)}


@router.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
async def deactivate_user(user_id: str):
    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return {"message": f"User {user_id} deactivated."}