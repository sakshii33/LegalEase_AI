# database.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, create_engine, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

# Database setup (SQLite file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "simplifier.db")

engine = create_engine(f"sqlite:///{db_path}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # We'll hash later
    documents = relationship("Document", back_populates="user")

# Document Model
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)          # original text
    simplified_content = Column(Text, nullable=True)  # simplified text
    flesch_ease_before = Column(Integer, nullable=True)
    flesch_ease_after = Column(Integer, nullable=True)
    grade_before = Column(Integer, nullable=True)
    grade_after = Column(Integer, nullable=True)
    fog_before = Column(Integer, nullable=True)
    fog_after = Column(Integer, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="documents")

# Create tables
Base.metadata.create_all(bind=engine)
