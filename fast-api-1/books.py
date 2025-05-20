from fastapi import Body, FastAPI, HTTPException

app = FastAPI()

BOOKS = [
  {"title": "Title One", "author": "author One", "category": "science"},
  {"title": "Title Two", "author": "author Two", "category": "science"},
  {"title": "Title Three", "author": "author Three", "category": "history"},
  {"title": "Title Four", "author": "author Four", "category": "math"},
  {"title": "Title Five", "author": "author Five", "category": "math"},
  {"title": "Title Six", "author": "author Two", "category": "math"},
]

@app.get('/books')
async def read_all_books():
  return BOOKS


# @app.get('/books/')
# async def read_book_by_category(category: str):
#   books_to_return = []
#   for book in BOOKS:
#     if book['category'].casefold() == category.casefold():
#       books_to_return.append(book)

#   return books_to_return

# @app.get('/books/{book_title}')
# async def read_book_by_title(book_title):
#   for book in BOOKS:
#     if book.get('title').casefold() == book_title.casefold():
#       return book
  
#   raise HTTPException(status_code=404, detail= f"Book with title {book_title} not found")

# @app.get('/books/{book_author}')
# async def read_book_by_title(book_author: str, category: str):
#   books_to_return = []
#   for book in BOOKS:
#     if book.get('author').casefold() == book_author.casefold() and book.get('category').casefold() == category.casefold():
#       books_to_return.append(book)

#   return books_to_return

# @app.get('/books/{book_author}')
# async def read_books_by_author(book_author: str):
#   books_to_return = []
#   for book in BOOKS:
#     if book.get('author').casefold() == book_author.casefold():
#       books_to_return.append(book)
      
#   return books_to_return

@app.get('/books/')
async def get_books_by_author(author: str):
  books_to_return = []
  for book in BOOKS:
    if book.get('author').casefold() == author.casefold():
      books_to_return.append(book)
      
  return books_to_return

@app.post('/books')
async def create_a_book(new_book=Body()):
  BOOKS.append(new_book)
  
  
@app.put('/books')
async def update_book(updated_book=Body()):
  for i in range(len(BOOKS)):
    if BOOKS[i]['title'].casefold() == updated_book['title'].casefold():
      BOOKS[i] = updated_book
      
@app.delete('/books/delete_book/{book_title}')
async def delete_book(book_title: str):
  for i in range(len(BOOKS)):
    if book_title.casefold() == BOOKS[i].get('title').casefold():
      BOOKS.pop(i)
      break
      
