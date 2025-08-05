# Book Store API

A Flask-based REST API for managing a book store inventory with dual database persistence (PostgreSQL and MongoDB).

## 🏗️ Architecture

The application follows a layered architecture pattern:

```
📁 book-store/
├── 🎮 controller/         # REST API endpoints
├── 🧠 logic/             # Business logic layer
├── 💾 repository/        # Data access layer
├── 📋 dto/               # Data Transfer Objects
├── 🔧 enums/             # Enumeration definitions
└── 🐳 Docker files       # Containerization
```

### Key Components

- **Controller Layer**: Handles HTTP requests and responses
- **Logic Layer**: Implements business rules and orchestrates data operations
- **Repository Layer**: Abstract data access with PostgreSQL and MongoDB implementations
- **DTO Layer**: Data structure definitions for books, filters, and genres
- **Dual Persistence**: Simultaneous storage in both PostgreSQL and MongoDB

## 🚀 Features

### Core Functionality
- ✅ Create new books with validation
- 📖 Retrieve books by ID or with advanced filtering
- 💰 Update book prices
- 🗑️ Delete books from inventory
- 📊 Get total book count

### Advanced Filtering
Filter books by:
- **Author** name
- **Price range** (minimum and maximum)
- **Publication year range**
- **Genres** (multiple selection)

### Supported Genres
- `SCI_FI` - Science Fiction
- `NOVEL` - General Novels
- `HISTORY` - Historical books
- `MANGA` - Japanese comics
- `ROMANCE` - Romance novels
- `PROFESSIONAL` - Professional/technical books

## 📚 API Endpoints

### Health Check
```http
GET /books/health
```
Returns: `"OK"` with status 200

### Create Book
```http
POST /book
Content-Type: application/json

{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 1925,
  "price": 15,
  "genres": ["NOVEL", "ROMANCE"]
}
```

### Get Books (with filtering)
```http
GET /books?persistenceMethod=POSTGRES&author=Tolkien&price-bigger-than=10&genres=SCI_FI,NOVEL
```

**Query Parameters:**
- `persistenceMethod` - `POSTGRES` or `MONGO` (required)
- `author` - Filter by author name
- `price-bigger-than` - Minimum price filter
- `price-less-than` - Maximum price filter
- `year-bigger-than` - Minimum year filter
- `year-less-than` - Maximum year filter
- `genres` - Comma-separated list of genres

### Get Single Book
```http
GET /book?id=123&persistenceMethod=POSTGRES
```

### Update Book Price
```http
PUT /book?id=123&price=25
```

### Delete Book
```http
DELETE /book?id=123
```

### Get Total Books Count
```http
GET /books/total?persistenceMethod=POSTGRES
```

## 🐳 Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start
```bash
# Start all services
docker-compose up

# The API will be available at: http://localhost:4785
```

### Services
- **PostgreSQL**: Port 5432 (credentials: postgres/docker)
- **MongoDB**: Port 27017
- **Flask App**: Port 4785 (external) → 8574 (internal)

## 🛠️ Local Development

### Requirements
- Python 3.12+
- PostgreSQL
- MongoDB

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd book-store

# Install dependencies
pip install -r requirements.txt

# Set environment variables (if running locally)
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export MONGO_HOST=localhost
export MONGO_PORT=27017

# Run the application
python main.py
```

### Dependencies
```
Flask==2.2.3
Werkzeug==2.2.2
SQLAlchemy~=2.0.36
psycopg2~=2.9.10
mongoengine
```

## 🔧 Configuration

### Database Configuration
The application uses environment variables for database connections:

**PostgreSQL:**
- Host: `POSTGRES_HOST` (default: "postgres")
- Port: `POSTGRES_PORT` (default: 5432)
- Database: `books`
- User: `postgres`
- Password: `docker`

**MongoDB:**
- Host: `MONGO_HOST` (default: "mongo")
- Port: `MONGO_PORT` (default: 27017)

### Application Settings
- **Server Host**: `0.0.0.0`
- **Server Port**: `8574`
- **Valid Year Range**: 1940-2100
- **Price Validation**: Must be non-negative

## 📝 Business Rules

### Book Creation Validation
- **Title uniqueness**: No duplicate titles allowed
- **Year range**: Must be between 1940-2100
- **Price validation**: Must be non-negative
- **Genre validation**: Must use predefined genres only

### Data Consistency
- Books are created in both PostgreSQL and MongoDB
- Updates and deletions are synchronized across both databases
- PostgreSQL is used as the primary source for conflict resolution

## 🧪 API Response Format

### Success Response
```json
{
  "result": <data>
}
```

### Error Response
```json
{
  "errorMessage": "Error description"
}
```

## 📊 HTTP Status Codes

- `200` - Success
- `404` - Resource not found / Invalid persistence method
- `409` - Conflict (duplicate title, invalid year/price)
- `400` - Bad request (invalid genres)

## 🔄 Persistence Strategy

The application implements a **dual-write pattern**:

1. **Create**: Data written to both PostgreSQL and MongoDB
2. **Read**: Configurable via `persistenceMethod` parameter
3. **Update**: Synchronized across both databases
4. **Delete**: Removed from both databases

This approach provides:
- **Flexibility**: Choose optimal database for different read patterns
- **Redundancy**: Data backup across multiple storage systems
- **Performance**: Leverage strengths of both SQL and NoSQL databases

## 🏃‍♂️ Getting Started Example

```bash
# 1. Start the services
docker-compose up

# 2. Check health
curl http://localhost:4785/books/health

# 3. Create a book
curl -X POST http://localhost:4785/book \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dune",
    "author": "Frank Herbert",
    "year": 1965,
    "price": 20,
    "genres": ["SCI_FI"]
  }'

# 4. Get all books
curl "http://localhost:4785/books?persistenceMethod=POSTGRES"

# 5. Filter books by genre
curl "http://localhost:4785/books?persistenceMethod=POSTGRES&genres=SCI_FI"
```

## 📈 Future Enhancements

- Authentication and authorization
- Book image upload support
- Inventory management (stock quantities)
- Search functionality (full-text search)
- Pagination for large datasets
- Caching layer for improved performance
- API versioning
- Comprehensive logging and monitoring