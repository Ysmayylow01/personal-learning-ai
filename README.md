# Oguz AI Academy - AI Öwreniş Web Platformasy

Professional we doly işleýän AI öwreniş platformasy. Flask backend, SQLite database we modern HTML/CSS/JS frontend bilen.

## 🎯 Aýratynlyklar

- ✅ Ulanyjy hasaba alnyş we giriş ulgamy
- 📚 6 sany doly AI kursy (Machine Learning, Deep Learning, NLP, Computer Vision, Reinforcement Learning, AI Ethics)
- 📊 Progress tracking - Okuwyň yzarlamak
- 🎯 Interactive quiz ulgamy
- 💾 SQLite database
- 🎨 Owadan, responsive dizaýn
- 📱 Mobile-friendly
- 🔒 Secure password hashing

## 📋 Talap edilýän programmalar

```
Python 3.8+
pip (Python package manager)
```

## 🚀 Gurnamak

### 1. Proýekti göçüriň

```bash
git clone <your-repo-url>
cd oguz-ai-academy
```

### 2. Folder gurluşyny dörediň

```
oguz-ai-academy/
│
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
│
└── templates/            # HTML sahypalar
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── courses.html
    ├── course_detail.html
    ├── quiz.html
    ├── about.html
    └── contact.html
```

### 3. requirements.txt faýlyny dörediň

```bash
touch requirements.txt
```

requirements.txt-e şulary ýazyň:

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
```

### 4. Virtual environment dörediň (optional, ýöne maslahat berilýär)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. Dependencies gurnań

```bash
pip install -r requirements.txt
```

### 6. Aplikasiýany işe giriziň

```bash
python app.py
```

Server başlanyňdan soň, browserda açyň:
```
http://127.0.0.1:5000
```

## 📁 Faýl gurluşy düşündirişi

### Backend (app.py)
- Flask server
- Database models (User, Course, Progress, QuizResult)
- Authentication ulgamy
- Routes we endpoints
- Kurs mazmunlary

### Frontend (templates/)
- **index.html** - Baş sahypa, hero section, features
- **courses.html** - Ähli kurslar, filtering
- **course_detail.html** - Aýratyn kurs maglumatlar
- **login.html** - Giriş sahypasy
- **register.html** - Hasaba alnyş sahypasy
- **dashboard.html** - Ulanyjy dashboard, progress tracking
- **quiz.html** - Interactive quiz ulgamy
- **about.html** - Barada maglumat
- **contact.html** - Aragatnaşyk sahypasy

## 💾 Database

SQLite database awtomatik döredilýär ilkinji işletmede:

```
oguz_ai_academy.db
```

Database-de şular bar:
- **users** - Ulanyjylar
- **course** - Kurslar
- **lesson** - Dersler
- **progress** - Ulanyjy progressi
- **quiz_result** - Quiz netijeleri

## 👤 Test hasaby döretmek

1. Browserda `/register` sahypasyna gidiň
2. Username, email we password giriziň
3. "Create Account" basyň
4. `/login` bilen giriň

## 🎓 Kurslar

Platform 6 sany doly kursy öz içine alýar:

1. **Machine Learning Fundamentals** - 8 hepde, Beginner
2. **Deep Learning & Neural Networks** - 10 hepde, Intermediate
3. **Natural Language Processing** - 8 hepde, Intermediate
4. **Computer Vision** - 9 hepde, Intermediate
5. **Reinforcement Learning** - 10 hepde, Advanced
6. **AI Ethics & Responsible AI** - 4 hepde, Beginner

Her kurs:
- Doly mazmunly
- Week-by-week curriculum
- Practical projects
- Prerequisites
- Tools & technologies

## 🎯 Ulanmak

### Kursa ýazylmak
1. Login ediň
2. Kurs saýlaň
3. "Enroll Now" basyň

### Progress tracking
1. Dashboard-a gidiň
2. Enrolled kurslar görnükli
3. Progress bar-lar bilen %

### Quiz almak
1. Kursy tamamlaň
2. Dashboard-dan "Take Quiz" basyň
3. 10 sorag jogap beriň
4. Netijäňizi görüň

## 🔧 Customization

### Täze kurs goşmak

`app.py`-de `init_db()` funksiýasyna täze kurs goşuň:

```python
new_course = {
    'title': 'Your Course Title',
    'slug': 'your-course-slug',
    'description': 'Short description',
    'category': 'Category Name',
    'difficulty': 'Beginner/Intermediate/Advanced',
    'duration': 'X weeks',
    'image': '🎯',  # Emoji
    'content': '''
        <h2>Course content here</h2>
        <p>Full HTML content...</p>
    '''
}
```

### Dizaýny üýtgetmek

Her HTML faýlda `<style>` tag-yň içinde CSS bar. Reňkleri, şriftleri we ş.m. üýtgedip bilersiňiz.

### Database pozulmak

Täzeden başlamak üçin:

```bash
# Delete database
rm oguz_ai_academy.db

# Restart app (creates new database)
python app.py
```

## 🔐 Howpsuzlyk

- Passwordlar Werkzeug bilen hash edilýär (pbkdf2:sha256)
- Session-based authentication
- CSRF protection (Flask-WTF bilen goşmaly)
- Input validation

## 📱 Responsive Design

Platforma ähli devices-de işleýär:
- Desktop computers
- Tablets
- Mobile phones

## 🐛 Debugging

Ýalňyşlyk bar bolsa:

```bash
# Check Flask version
python -c "import flask; print(flask.__version__)"

# Check database
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

## 📝 Production üçin

Production-da ulanmak üçin:

1. `app.config['SECRET_KEY']` üýtgediň
2. `debug=False` daliň
3. Gunicorn ýa-da uWSGI ulanyň:

```bash
pip install gunicorn
gunicorn app:app
```

4. Environment variables ulanyň:

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

## 🎨 Diplomat işi üçin taýýar

Bu proýekt diplom işi üçin:
- ✅ Professional görünýär
- ✅ Doly işleýän features
- ✅ Uly database
- ✅ Köp sahypalar
- ✅ Modern dizaýn
- ✅ Responsive
- ✅ Good code structure

## 📞 Kömek

Sorag bar bolsa, `contact.html` sahypasyndaky forma ulanyň!

## 📄 License

MIT License - Free to use for educational purposes

---

**Oguz AI Academy** - Empowering the next generation of AI innovators! 🎓🚀