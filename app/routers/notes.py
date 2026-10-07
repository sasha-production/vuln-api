from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import schemas, models

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=schemas.NoteOut)
def create_note(payload: schemas.NoteCreate, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    note = models.Note(title=payload.title, body=payload.body, owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[schemas.NoteOut])
def list_my_notes(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Note).filter(models.Note.owner_id == user.id).all()


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # VULN #3 (IDOR): проверки владельца нет — читаем чужую заметку по id.
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    return note


@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(note_id: int, payload: schemas.NoteUpdate,
                db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.body is not None:
        note.body = payload.body
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(note)
    db.commit()
    return {"ok": True}
