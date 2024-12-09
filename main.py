from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()

DATABASE_URL = "postgresql://postgres:root@db:5454/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)
    post = relationship('Post', back_populates='author')


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    authorid = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    author = relationship('Author', back_populates='post')
    subtitle = Column(String)


Base.metadata.create_all(bind=engine)




class AuthorBase(BaseModel):
    name: str
    age: int


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
    post: List['Post'] = []

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    text: str
    subtitle: str


class PostCreate(PostBase):
    authorid: int


class Post(PostBase):
    id: int
    created: datetime.datetime
    authorid: int

    class Config:
        orm_mode = True




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.post("/authors", response_model=Author)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


@app.put("/authors/{author_id}", response_model=Author)
def update_author(author_id: int, updated_author: AuthorCreate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in updated_author.dict().items():
        setattr(author, key, value)
    db.commit()
    db.refresh(author)
    return author


@app.get("/authors", response_model=List[Author])
def read_authors(db: Session = Depends(get_db)):
    return db.query(Author).all()


@app.delete("/authors/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()
    return {"message": "Author deleted"}


@app.post("/posts", response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in updated_post.dict().items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@app.get("/posts", response_model=List[Post])
def read_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}


@app.get("/authorAndPosts", response_model=List[Author])
def posts_and_author(db: Session = Depends(get_db)):
    return db.query(Author).join(Post).all()
