from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base, engine, SessionLocal


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String
    )

    podcast_url: Mapped[str] = mapped_column(
        String
    )

    status: Mapped[str] = mapped_column(
        String,
        default="created"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id")
    )

    artifact_type: Mapped[str] = mapped_column(
        String
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(engine)


def create_session(title: str, podcast_url: str):

    db = SessionLocal()

    session = Session(
        id=str(uuid4()),
        title=title,
        podcast_url=podcast_url,
        status="created"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    db.close()

    return session


def save_artifact(
    session_id: str,
    artifact_type: str,
    content: str
):

    db = SessionLocal()

    artifact = Artifact(
        id=str(uuid4()),
        session_id=session_id,
        artifact_type=artifact_type,
        content=content
    )

    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    db.close()

    return artifact

def get_session(session_id: str):

    db = SessionLocal()

    session = db.get(Session, session_id)

    db.close()

    return session


def get_artifacts(session_id: str):

    db = SessionLocal()

    artifacts = (
        db.query(Artifact)
        .filter(Artifact.session_id == session_id)
        .order_by(Artifact.created_at)
        .all()
    )

    db.close()

    return artifacts

def get_latest_artifact(session_id: str, artifact_type: str):
    db = SessionLocal()

    artifact = (
        db.query(Artifact)
        .filter(
            Artifact.session_id == session_id,
            Artifact.artifact_type == artifact_type
        )
        .order_by(Artifact.created_at.desc())
        .first()
    )

    db.close()

    return artifact

def update_session(
    session_id: str,
    title: str | None = None,
    status: str | None = None
):
    db = SessionLocal()

    session = db.get(Session, session_id)

    if session is None:
        db.close()
        return None

    if title is not None:
        session.title = title

    if status is not None:
        session.status = status

    db.commit()
    db.refresh(session)

    db.close()

    return session

def list_sessions():

    db = SessionLocal()

    sessions = (
        db.query(Session)
        .order_by(Session.updated_at.desc())
        .all()
    )

    db.close()

    return sessions

def load_session_memory(session_id: str):

    session = get_session(session_id)

    if session is None:
        return None

    artifacts = get_artifacts(session_id)

    return {
        "session": session,
        "artifacts": artifacts
    }