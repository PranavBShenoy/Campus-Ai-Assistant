import datetime
import uuid
import enum
from typing import Optional, Any
from sqlalchemy import String, Integer, Float, Boolean, JSON, DateTime, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    student_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

class DocumentStatus(str, enum.Enum):
    uploading = "uploading"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"
    deleted = "deleted"

class ConversationMode(str, enum.Enum):
    basic_llm = "basic_llm"
    academic_rag = "academic_rag"

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    original_filename: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus))
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    chunk_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    upload_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    processed_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Document {self.original_filename} ({self.status})>"

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    mode: Mapped[ConversationMode] = mapped_column(Enum(ConversationMode))

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Conversation {self.title}>"

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(String)
    sources_json: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    mode: Mapped[ConversationMode] = mapped_column(Enum(ConversationMode))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.role}: {self.content[:20]}...>"

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String)
    subjects_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    sessions_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    constraints_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    start_date: Mapped[datetime.date] = mapped_column(DateTime)
    end_date: Mapped[datetime.date] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<StudyPlan {self.title}>"

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    question: Mapped[str] = mapped_column(String)
    basic_llm_response: Mapped[str] = mapped_column(String)
    rag_response: Mapped[str] = mapped_column(String)
    sources_json: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    basic_latency_ms: Mapped[float] = mapped_column(Float)
    rag_latency_ms: Mapped[float] = mapped_column(Float)
    has_citations: Mapped[bool] = mapped_column(Boolean)
    groundedness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f"<EvaluationRun {self.id}>"
