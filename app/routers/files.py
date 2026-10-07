import os
import shutil
import yaml
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.config import UPLOAD_DIR
from app import models

router = APIRouter(prefix="/files", tags=["files"])

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload(
    file: UploadFile = File(...),
    subdir: str = Form(""),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # VULN #4a (Path Traversal): подконтрольный subdir склеивается с базовым путём.
    # Пример: subdir="../../etc" → файл ляжет вне uploads.
    target_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(target_dir, exist_ok=True)

    # VULN #4b (Unrestricted File Upload): сохраняем оригинальное имя,
    # не проверяем расширение/MIME/размер.
    target_path = os.path.join(target_dir, file.filename)
    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    asset = models.FileAsset(filename=file.filename, path=target_path, owner_id=user.id)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return {"id": asset.id, "path": target_path}


@router.get("/download")
def download(path: str, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    # VULN #4c (Path Traversal при чтении): отдаём любой файл по указанному пути.
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Not found")
    from fastapi.responses import FileResponse
    return FileResponse(path)


@router.post("/import-yaml")
def import_yaml(payload: dict, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    # VULN #4d (Insecure Deserialization / RCE): yaml.load без SafeLoader.
    # Позволяет выполнить код через !!python/object/apply.
    raw = payload.get("content", "")
    data = yaml.load(raw)  # noqa: S506
    return {"imported": len(data) if hasattr(data, "__len__") else 1}
