from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Document
from app.schemas import DocumentCreate, DocumentOut
from app.security import get_current_user

router = APIRouter(
    prefix="/v1/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(payload: DocumentCreate, session: SessionDep) -> Document:
    doc = Document(title=payload.title)
    session.add(doc)
    await session.commit()
    return doc


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: int, session: SessionDep) -> Document:
    doc = await session.get(Document, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return doc

@router.delete("/{document_id}", response_model=DocumentOut)
async def delete_document(document_id: int, session: SessionDep) -> Document:
    doc = await session.get(Document, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    await session.delete(doc)
    await session.commit()
    return doc
