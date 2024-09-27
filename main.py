from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID, uuid4
import re

app = FastAPI()

class Book(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publication_year: int = Field(..., gt=0, le=2024)
    isbn: str
    
    @field_validator('isbn')
    def validate_isbn(cls, v):
        # Validating ISBN-10 (9 digits + X or 10 digits) or ISBN-13 (13 digits)
        if not re.match(r'^\d{9}[\dXx]$|^\d{13}$', v):
            raise ValueError('Invalid ISBN format')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "publication_year": 1960,
                "isbn": "9780446310789"
            }
        }

books_db: List[Book] = []

@app.post("/books/", response_model=Book)
async def create_book(book: Book):
    books_db.append(book)
    return book

@app.get("/books/", response_model=List[Book])
async def read_books():
    return books_db

@app.get("/books/{book_id}", response_model=Book)
async def read_book(book_id: UUID):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: UUID, updated_book: Book):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            updated_book_dict = updated_book.model_dump()
            updated_book_dict['id'] = book_id
            books_db[i] = Book(**updated_book_dict)
            return books_db[i]
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
async def delete_book(book_id: UUID):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            del books_db[i]
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
