"""
db_models.py — SQLAlchemy models: Python classes that represent our
actual database tables. Alembic will read these to generate migrations.

Note: these are different from app/models/chat.py's Pydantic models.
- Pydantic models (chat.py) validate API request/response JSON shapes.
- SQLAlchemy models (this file) define actual database TABLE structure.
They often look similar but serve completely different jobs.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


def new_uuid():
    # Generates a random unique ID, used as the default for every primary key.
    return uuid.uuid4()


def utcnow():
    # A single, consistent way to get the current time, used for created_at defaults.
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="member")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # "relationship" isn't a real column -- it's a convenience that lets us
    # write user.conversations in Python and get all related rows automatically.
    conversations = relationship("Conversation", back_populates="user")
    documents = relationship("Document", back_populates="uploader")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    agent_runs = relationship("AgentRun", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)          # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # nullable until Step 12 (auth) exists
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    uploader = relationship("User", back_populates="documents")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="agent_runs")
