from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_year = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'published_year': self.published_year
        }

# Create the database (only needed for the first run)
with app.app_context():
    db.create_all()

# GET all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# GET a book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description="Book not found")
    return jsonify(book.to_dict()), 200

# POST a new book (Create)
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()

    if not data or not 'title' in data or not 'author' in data:
        abort(400, description="Title and author are required")

    new_book = Book(
        title=data['title'],
        author=data['author'],
        published_year=data.get('published_year', None)
    )

    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201

# PUT (Update) an existing book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description="Book not found")

    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.published_year = data.get('published_year', book.published_year)

    db.session.commit()
    return jsonify(book.to_dict()), 200

# DELETE a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description="Book not found")

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': error.description}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': error.description}), 400

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
