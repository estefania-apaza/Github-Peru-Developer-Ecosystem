from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    company = Column(String(200))
    location = Column(String(200))
    email = Column(String(200))
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    repositories = relationship("Repository", back_populates="owner")

class Repository(Base):
    __tablename__ = 'repositories'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(200), nullable=False)
    full_name = Column(String(400))
    description = Column(Text)
    language = Column(String(100))
    stargazers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    owner = relationship("User", back_populates="repositories")
    classification = relationship("Classification", back_populates="repository", uselist=False)

class Classification(Base):
    __tablename__ = 'classifications'
    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey('repositories.id'), unique=True)
    industry_code = Column(String(10))
    industry_name = Column(String(200))
    confidence = Column(String(50))
    reasoning = Column(Text)
    
    repository = relationship("Repository", back_populates="classification")