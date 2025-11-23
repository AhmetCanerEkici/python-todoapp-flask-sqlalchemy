"""
A1 - OOP Tabanlı To-Do Uygulaması
Tek dosya olarak çalışacak: çalıştırıldığında gerekli `templates/` klasörünü
ve HTML şablonlarını oluşturur ve Flask uygulamasını başlatır.

Gereksinimler:
- Python 3.8+
- pip install Flask Flask_SQLAlchemy

Çalıştırma:
$ python A1_Todo_App_Flask_SQLAlchemy.py
Uygulama http://127.0.0.1:5000 üzerinde çalışır.

Dosya yapısı (otomatik oluşturulur):
- templates/index.html
- templates/edit.html
- app.db (SQLite, çalışma dizininde)

Kısa açıklama:
- OOP: Task sınıfı (başlık, açıklama, tamamlandı)
- Flask-SQLAlchemy: görevleri kalıcı saklama (SQLite)
- Web: görev ekleme, listeleme, durum güncelleme, silme, düzenleme
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# --- Dosyaları/şablonları oluştur (ilk çalıştırma için) ---
TEMPLATES_DIR = 'templates'
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

INDEX_HTML = '''<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>To-Do Uygulaması</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-4">
      <h1 class="mb-4">Görev Listesi</h1>

      {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for msg in messages %}
          <div class="alert alert-info">{{ msg }}</div>
        {% endfor %}
      {% endif %}
      {% endwith %}

      <form method="POST" action="/add" class="row g-2 mb-4">
        <div class="col-md-5">
          <input name="title" class="form-control" placeholder="Görev başlığı" required>
        </div>
        <div class="col-md-5">
          <input name="description" class="form-control" placeholder="Kısa açıklama">
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary w-100">Ekle</button>
        </div>
      </form>

      <table class="table table-striped table-bordered bg-white">
        <thead>
          <tr>
            <th>#</th>
            <th>Başlık</th>
            <th>Açıklama</th>
            <th>Durum</th>
            <th>Oluşturulma</th>
            <th>İşlemler</th>
          </tr>
        </thead>
        <tbody>
          {% for t in tasks %}
          <tr>
            <td>{{ loop.index }}</td>
            <td>{{ t.title }}</td>
            <td>{{ t.description or '-' }}</td>
            <td>
              {% if t.completed %}
                <span class="badge bg-success">Tamamlandı</span>
              {% else %}
                <span class="badge bg-warning text-dark">Beklemede</span>
              {% endif %}
            </td>
            <td>{{ t.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
            <td>
              <a href="/toggle/{{ t.id }}" class="btn btn-sm btn-outline-success">Durum Değiştir</a>
              <a href="/edit/{{ t.id }}" class="btn btn-sm btn-outline-primary">Düzenle</a>
              <a href="/delete/{{ t.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Silinsin mi?');">Sil</a>
            </td>
          </tr>
          {% else %}
          <tr><td colspan="6" class="text-center">Henüz görev yok. Ekleyin!</td></tr>
          {% endfor %}
        </tbody>
      </table>

    </div>
  </body>
</html>
'''

EDIT_HTML = '''<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Görevi Düzenle</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-4">
      <h1 class="mb-4">Görevi Düzenle</h1>

      <form method="POST" action="/edit/{{ task.id }}">
        <div class="mb-3">
          <label class="form-label">Başlık</label>
          <input name="title" class="form-control" value="{{ task.title }}" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Açıklama</label>
          <input name="description" class="form-control" value="{{ task.description }}">
        </div>
        <div class="mb-3 form-check">
          <input type="checkbox" name="completed" class="form-check-input" id="completed" {% if task.completed %}checked{% endif %}>
          <label class="form-check-label" for="completed">Tamamlandı</label>
        </div>
        <button class="btn btn-primary">Güncelle</button>
        <a href="/" class="btn btn-secondary">Geri</a>
      </form>
    </div>
  </body>
</html>
'''

# Yazılmamışsa şablon dosyalarını oluştur
index_path = os.path.join(TEMPLATES_DIR, 'index.html')
edit_path = os.path.join(TEMPLATES_DIR, 'edit.html')
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(INDEX_HTML)
if not os.path.exists(edit_path):
    with open(edit_path, 'w', encoding='utf-8') as f:
        f.write(EDIT_HTML)

# --- Flask Uygulaması ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gizli-anahtar-orn'  # production için çevresel değişkene taşı

db = SQLAlchemy(app)

# OOP: Task sınıfı (hem SQLAlchemy model hem de programatik kullanım için)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id} - {self.title}>"

# DB'yi ilk çalıştırmada oluştur
with app.app_context():
    db.create_all()

# Anasayfa - görevleri listeleme
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

# Görev ekleme
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    description = request.form.get('description')
    if not title:
        flash('Başlık boş olamaz.')
        return redirect(url_for('index'))
    t = Task(title=title, description=description)
    db.session.add(t)
    db.session.commit()
    flash('Görev eklendi.')
    return redirect(url_for('index'))

# Görev silme
@app.route('/delete/<int:id>')
def delete(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Görev silindi.')
    return redirect(url_for('index'))

# Durum değiştir
@app.route('/toggle/<int:id>')
def toggle(id):
    t = Task.query.get_or_404(id)
    t.completed = not t.completed
    db.session.commit()
    flash('Görev durumu güncellendi.')
    return redirect(url_for('index'))

# Düzenleme (GET formu + POST güncelleme)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    t = Task.query.get_or_404(id)
    if request.method == 'POST':
        t.title = request.form.get('title')
        t.description = request.form.get('description')
        t.completed = bool(request.form.get('completed'))
        db.session.commit()
        flash('Görev güncellendi.')
        return redirect(url_for('index'))
    return render_template('edit.html', task=t)

if __name__ == '__main__':
    app.run(debug=True)
