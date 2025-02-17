from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/article"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Model `Posts`
class Posts(db.Model):
  id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  category = db.Column(db.String(100), nullable=False)
  created_date = db.Column(db.DateTime, default=datetime.utcnow)
  updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  status = db.Column(db.String(100), nullable=False, comment="Publish | Draft | Stash")

# Buat tabel jika belum ada
with app.app_context():
  db.create_all()

# Tambah Artikel
@app.post("/posts/")
def create_posts():
  data = request.json

  if "title" not in data or len(data["title"]) < 20:
    return jsonify({"error": "Title is required and must be at least 20 characters."}), 400
  
  if "content" not in data or len(data["content"]) < 200:
    return jsonify({"error": "Content is required and must be at least 200 characters."}), 400
  
  if "category" not in data or len(data["category"]) < 3:
    return jsonify({"error": "Category is required and must be at least 3 characters."}), 400
  
  if "status" not in data or data["status"].lower() not in ["publish", "draft", "thrash"]:
    return jsonify({"error": "Status is required and must be 'publish', 'draft', or 'thrash'."}), 400

  new_posts = Posts(
    title=data["title"],
    content=data["content"],
    category=data["category"],
    status=data["status"]
  )

  db.session.add(new_posts)
  db.session.commit()
  return jsonify({}), 201

# Index
@app.get("/posts/<int:limit>/<int:offset>")
def get_posts(limit, offset):
  posts = Posts.query.offset(offset).limit(limit).all()
  result = [{
    "id": a.id,
    "title": a.title,
    "content": a.content,
    "category": a.category,
    "created_date": a.created_date.strftime('%Y-%m-%d %H:%M:%S'),
    "updated_date": a.updated_date.strftime('%Y-%m-%d %H:%M:%S'),
    "status": a.status
  } for a in posts]

  return jsonify(result)

# Detail
@app.get("/posts/<int:id>")
def detail_posts(id):
  posts = Posts.query.get(id)
  if not posts:
    return jsonify({"error": "Posts not found"}), 404
  return jsonify({
    "id": posts.id,
    "title": posts.title,
    "content": posts.content,
    "category": posts.category,
    "created_date": posts.created_date.strftime('%Y-%m-%d %H:%M:%S'),
    "updated_date": posts.updated_date.strftime('%Y-%m-%d %H:%M:%S'),
    "status": posts.status
  })

# Update
@app.put("/posts/<int:id>")
def update_posts(id):
  posts = Posts.query.get(id)
  if not posts:
    return jsonify({"error": "Posts not found"}), 404

  data = request.json

  if "title" in data and len(data["title"]) < 20:
    return jsonify({"error": "Title must be at least 20 characters."}), 400

  if "content" in data and len(data["content"]) < 200:
    return jsonify({"error": "Content must be at least 200 characters."}), 400

  if "category" in data and len(data["category"]) < 3:
    return jsonify({"error": "Category must be at least 3 characters."}), 400

  if "status" in data and data["status"].lower() not in ["publish", "draft", "thrash"]:
    return jsonify({"error": "Status must be 'publish', 'draft', or 'thrash'."}), 400

  posts.title = data.get("title", posts.title)
  posts.content = data.get("content", posts.content)
  posts.category = data.get("category", posts.category)
  posts.status = data.get("status", posts.status)

  db.session.commit()

  return jsonify({"message": "Posts updated successfully!"})

# delete
@app.delete("/posts/<int:id>")
def delete_posts(id):
  posts = Posts.query.get(id)
  if not posts:
    return jsonify({"error": "Posts not found"}), 404

  db.session.delete(posts)
  db.session.commit()

  return jsonify({"message": "Posts deleted successfully!"})

@app.route('/allpost', methods=["GET"])
def all_posts():
  published_posts = Posts.query.filter_by(status='publish').all()
  draft_posts = Posts.query.filter_by(status='draft').all()
  trashed_posts = Posts.query.filter_by(status='trash').all()

  return render_template('all_posts.html', published=published_posts, draft=draft_posts, trashed=trashed_posts)

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_posts(id):
  posts = Posts.query.get_or_404(id)

  if request.method == "POST":
    # Update artikel berdasarkan form
    posts.title = request.form['title']
    posts.content = request.form['content']
    posts.category = request.form['category']
    posts.status = request.form['status']
    db.session.commit()

    return redirect(url_for('all_posts'))

  return render_template('edit_posts.html', posts=posts)

@app.route('/addnew', methods=["GET", "POST"])
def addnew():
  if request.method == "POST":
    # Create artikel baru
    new_posts = Posts(
      title=request.form['title'],
      content=request.form['content'],
      category=request.form['category'],
      status=request.form['status']
    )
    db.session.add(new_posts)
    db.session.commit()

    return redirect(url_for('all_posts'))

  return render_template('add_new.html')

@app.route('/preview', methods=["GET"])
def preview_posts():
  page = request.args.get('page', 1, type=int)
  posts = Posts.query.filter_by(status='publish').paginate(page=page, per_page=5)
  return render_template('preview.html', posts=posts)



@app.route('/trash/<int:id>', methods=["GET"])
def trash_posts(id):
  posts = Posts.query.get_or_404(id)
  posts.status = 'trash'
  db.session.commit()
  return redirect(url_for('all_posts'))


if __name__ == "__main__":
  app.run(debug=True)
