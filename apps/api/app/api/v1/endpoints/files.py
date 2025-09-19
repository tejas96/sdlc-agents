"""File upload and management endpoints."""

import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import CurrentUser
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/upload")
async def upload_files(
    current_user: CurrentUser,
    files: list[UploadFile] = File(...),
    session_id: str = None,
) -> dict[str, Any]:
    """Upload multiple files for agent processing."""

    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Create session directory
    session_dir = Path(settings.AGENTS_DIR) / f"uploads_{session_id}"
    session_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    total_size = 0

    for file in files:
        # Validate file size (10MB limit)
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} is too large (max 10MB)"
            )

        total_size += file_size

        # Save file
        file_path = session_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(file_content)

        uploaded_files.append({
            "filename": file.filename,
            "size": file_size,
            "path": str(file_path),
            "content_type": file.content_type,
        })

    return {
        "session_id": session_id,
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files),
        "total_size": total_size,
        "upload_directory": str(session_dir),
    }


@router.get("/{session_id}")
async def list_session_files(
    session_id: str,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """List files in a session directory."""

    session_dir = Path(settings.AGENTS_DIR) / f"uploads_{session_id}"

    if not session_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    files = []
    for file_path in session_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": str(file_path),
            })

    return {
        "session_id": session_id,
        "files": files,
        "total_files": len(files),
        "session_directory": str(session_dir),
    }


@router.get("/{session_id}/{filename}")
async def download_file(
    session_id: str,
    filename: str,
    current_user: CurrentUser,
) -> FileResponse:
    """Download a file from a session directory."""

    session_dir = Path(settings.AGENTS_DIR) / f"uploads_{session_id}"
    file_path = session_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.delete("/{session_id}/{filename}")
async def delete_file(
    session_id: str,
    filename: str,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete a file from a session directory."""

    session_dir = Path(settings.AGENTS_DIR) / f"uploads_{session_id}"
    file_path = session_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {e!s}"
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete an entire session directory."""

    session_dir = Path(settings.AGENTS_DIR) / f"uploads_{session_id}"

    if not session_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        import shutil
        shutil.rmtree(session_dir)
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {e!s}"
        )
