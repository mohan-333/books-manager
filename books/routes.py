from flask import request, jsonify
from . import books_bp
from models import db, Book
import datetime
import requests

# Open Library API URL
OPEN_LIBRARY_API_URL = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json&jscmd=data"

@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        publication_date=datetime.datetime.strptime(data['publication_date'], '%Y-%m-%d').date(),
        isbn=data.get('isbn')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201

@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'publication_date': book.publication_date.strftime('%Y-%m-%d'),
        'isbn': book.isbn
    } for book in books])

@books_bp.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'publication_date': book.publication_date.strftime('%Y-%m-%d'),
        'isbn': book.isbn
    })

@books_bp.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    book = Book.query.get_or_404(id)
    book.title = data['title']
    book.author = data['author']
    book.publication_date = datetime.datetime.strptime(data['publication_date'], '%Y-%m-%d').date()
    book.isbn = data.get('isbn')
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

@books_bp.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

@books_bp.route('/books/isbn/<string:isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    response = requests.get(OPEN_LIBRARY_API_URL.format(isbn))
    if response.status_code != 200:
        return jsonify({'message': 'Error fetching book information'}), response.status_code

    book_data = response.json().get(f"ISBN:{isbn}")
    if not book_data:
        return jsonify({'message': 'Book not found'}), 404

    return jsonify({
        'title': book_data.get('title'),
        'author': ", ".join([author['name'] for author in book_data.get('authors', [])]),
        'publication_date': book_data.get('publish_date')
    })
