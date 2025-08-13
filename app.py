from flask import Flask, render_template_string, request, jsonify, session, redirect
from flask_cors import CORS
import os
import json
import random
import string
import time
import hashlib
import validators
from datetime import datetime
from typing import List, Dict, Any

# Flask app oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)

# Data klasörleri
DATA_DIR = 'data'
LINKS_DIR = os.path.join(DATA_DIR, 'links')
VISITS_DIR = os.path.join(DATA_DIR, 'visits')
ADS_FILE = os.path.join(DATA_DIR, 'ads.json')
ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')

def ensure_dirs():
    os.makedirs(LINKS_DIR, exist_ok=True)
    os.makedirs(VISITS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

ensure_dirs()

# Storage sınıfı
class Storage:
    @staticmethod
    def _read_json(filepath: str, default_value: Any = None) -> Any:
        if not os.path.exists(filepath):
            return default_value
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_value

    @staticmethod
    def _write_json(filepath: str, data: Any):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_links() -> List[Dict]:
        links = []
        if os.path.exists(LINKS_DIR):
            for filename in os.listdir(LINKS_DIR):
                if filename.endswith('.json'):
                    link_data = Storage._read_json(os.path.join(LINKS_DIR, filename))
                    if link_data:
                        links.append(link_data)
        return sorted(links, key=lambda x: x.get('created_at', ''), reverse=True)

    @staticmethod
    def get_link(short_code: str) -> Dict | None:
        filepath = os.path.join(LINKS_DIR, f'{short_code}.json')
        return Storage._read_json(filepath)

    @staticmethod
    def save_link(link_data: Dict):
        filepath = os.path.join(LINKS_DIR, f'{link_data["short_code"]}.json')
        Storage._write_json(filepath, link_data)

    @staticmethod
    def delete_link(short_code: str):
        filepath = os.path.join(LINKS_DIR, f'{short_code}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
        visit_dir = os.path.join(VISITS_DIR, short_code)
        if os.path.exists(visit_dir):
            import shutil
            shutil.rmtree(visit_dir)

    @staticmethod
    def get_visits(link_code: str) -> List[Dict]:
        filepath = os.path.join(VISITS_DIR, link_code, 'visits.json')
        return Storage._read_json(filepath, [])

    @staticmethod
    def save_visit(link_code: str, visit_data: Dict):
        link_visits_dir = os.path.join(VISITS_DIR, link_code)
        os.makedirs(link_visits_dir, exist_ok=True)
        filepath = os.path.join(link_visits_dir, 'visits.json')
        visits = Storage._read_json(filepath, [])
        visits.append(visit_data)
        Storage._write_json(filepath, visits)

    @staticmethod
    def get_ads() -> List[Dict]:
        return Storage._read_json(ADS_FILE, [])

    @staticmethod
    def save_ads(ads_data: List[Dict]):
        Storage._write_json(ADS_FILE, ads_data)

    @staticmethod
    def get_admin_user() -> Dict | None:
        return Storage._read_json(ADMIN_FILE)

    @staticmethod
    def save_admin_user(admin_data: Dict):
        Storage._write_json(ADMIN_FILE, admin_data)

    @staticmethod
    def get_stats() -> Dict:
        return Storage._read_json(STATS_FILE, {'total_links': 0, 'active_links': 0, 'total_clicks': 0, 'total_visits': 0})

    @staticmethod
    def save_stats(stats_data: Dict):
        Storage._write_json(STATS_FILE, stats_data)

# Link sınıfı
class Link:
    def __init__(self, original_url, short_code=None):
        self.original_url = original_url
        self.short_code = short_code or self._generate_short_code()
        self.click_count = 0
        self.created_at = datetime.now().isoformat()
        self.is_active = True
        self.save()
    
    def _generate_short_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not Storage.get_link(code):
                return code
    
    def save(self):
        data = {
            'short_code': self.short_code,
            'original_url': self.original_url,
            'click_count': self.click_count,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
        Storage.save_link(data)
    
    def increment_click(self):
        self.click_count += 1
        self.save()
        stats = Storage.get_stats()
        stats['total_clicks'] += 1
        Storage.save_stats(stats)
    
    def toggle_active(self):
        self.is_active = not self.is_active
        self.save()
        stats = Storage.get_stats()
        if self.is_active:
            stats['active_links'] += 1
        else:
            stats['active_links'] -= 1
        Storage.save_stats(stats)
    
    def delete(self):
        Storage.delete_link(self.short_code)
        stats = Storage.get_stats()
        stats['total_links'] -= 1
        if self.is_active:
            stats['active_links'] -= 1
        Storage.save_stats(stats)
    
    @property
    def visits_count(self):
        visits = Storage.get_visits(self.short_code)
        return len(visits)
    
    @staticmethod
    def get_all():
        links_data = Storage.get_links()
        links = []
        for data in links_data:
            link = Link.__new__(Link)
            link.short_code = data['short_code']
            link.original_url = data['original_url']
            link.click_count = data['click_count']
            link.created_at = data['created_at']
            link.is_active = data['is_active']
            links.append(link)
        return links
    
    @staticmethod
    def get_by_code(short_code):
        data = Storage.get_link(short_code)
        if data:
            link = Link.__new__(Link)
            link.short_code = data['short_code']
            link.original_url = data['original_url']
            link.click_count = data['click_count']
            link.created_at = data['created_at']
            link.is_active = data['is_active']
            return link
        return None

# LinkVisit sınıfı
class LinkVisit:
    def __init__(self, link_code, ip_address, user_agent, referrer='', step=1):
        self.link_code = link_code
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.referrer = referrer
        self.step = step
        self.visit_time = datetime.now().isoformat()
        self.save()
    
    def save(self):
        data = {
            'link_code': self.link_code,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'step': self.step,
            'visit_time': self.visit_time
        }
        Storage.save_visit(self.link_code, data)
        stats = Storage.get_stats()
        stats['total_visits'] += 1
        Storage.save_stats(stats)
    
    @staticmethod
    def get_visits(link_code):
        return Storage.get_visits(link_code)
    
    @staticmethod
    def has_visited_today(link_code, ip_address):
        visits = Storage.get_visits(link_code)
        today = datetime.now().date()
        
        for visit in visits:
            visit_date = datetime.fromisoformat(visit['visit_time']).date()
            if visit['ip_address'] == ip_address and visit_date == today:
                return True
        return False

# Admin sınıfı
class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self._hash_password(password)
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == self._hash_password(password)
    
    def save(self):
        data = {
            'username': self.username,
            'password_hash': self.password_hash
        }
        Storage.save_admin_user(data)
    
    @staticmethod
    def get_by_username(username):
        data = Storage.get_admin_user()
        if data and data['username'] == username:
            admin = Admin.__new__(Admin)
            admin.username = data['username']
            admin.password_hash = data['password_hash']
            return admin
        return None

# Güvenlik fonksiyonları
rate_limit_data = {}

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or '127.0.0.1'

def validate_url(url):
    if not url or len(url) > 2048:
        return False, "URL çok uzun"
    
    if not validators.url(url):
        return False, "Geçersiz URL formatı"
    
    if not url.startswith(('http://', 'https://')):
        return False, "Sadece HTTP/HTTPS protokolleri desteklenir"
    
    return True, "OK"

def is_bot_request():
    user_agent = request.headers.get('User-Agent', '').lower()
    bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'requests']
    return any(pattern in user_agent for pattern in bot_patterns)

# Ana sayfa
@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

# URL kısaltma
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL gerekli'}), 400
    
    if is_bot_request():
        return jsonify({'error': 'Bot istekleri kabul edilmiyor'}), 403
    
    is_valid, message = validate_url(original_url)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    link = Link(original_url)
    
    stats = Storage.get_stats()
    stats['total_links'] += 1
    stats['active_links'] += 1
    Storage.save_stats(stats)
    
    return jsonify({
        'short_code': link.short_code,
        'short_url': f'/l/{link.short_code}',
        'original_url': link.original_url
    }), 201

# Link yönlendirme
@app.route('/l/<short_code>')
def redirect_link(short_code):
    link = Link.get_by_code(short_code)
    
    if not link or not link.is_active:
        return "Link bulunamadı", 404
    
    session[f'link_{short_code}_step'] = 1
    session[f'link_{short_code}_start_time'] = time.time()
    session[f'link_{short_code}_ip'] = get_client_ip()
    
    client_ip = get_client_ip()
    if not LinkVisit.has_visited_today(short_code, client_ip):
        LinkVisit(
            link_code=short_code,
            ip_address=client_ip,
            user_agent=request.headers.get('User-Agent', ''),
            referrer=request.headers.get('Referer', ''),
            step=1
        )
    
    return render_template_string(REDIRECT_TEMPLATE, short_code=short_code, step=1)

@app.route('/l/<short_code>/step/<int:step>')
def redirect_step(short_code, step):
    link = Link.get_by_code(short_code)
    
    if not link or not link.is_active:
        return "Link bulunamadı", 404
    
    session_step_key = f'link_{short_code}_step'
    session_time_key = f'link_{short_code}_start_time'
    session_ip_key = f'link_{short_code}_ip'
    
    if session_step_key not in session:
        return redirect(f'/l/{short_code}')
    
    current_session_step = session.get(session_step_key, 0)
    session_ip = session.get(session_ip_key, '')
    current_ip = get_client_ip()
    
    if session_ip != current_ip:
        return redirect(f'/l/{short_code}')
    
    if step != current_session_step + 1:
        return redirect(f'/l/{short_code}')
    
    start_time = session.get(session_time_key, 0)
    if time.time() - start_time < (current_session_step * 15):
        return "Çok hızlı! Biraz bekleyin.", 400
    
    session[session_step_key] = step
    
    if step == 2:
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=2
            )
        return render_template_string(REDIRECT_TEMPLATE, short_code=short_code, step=2)
    elif step == 3:
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=3
            )
        return render_template_string(REDIRECT_TEMPLATE, short_code=short_code, step=3)
    elif step == 4:
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=4
            )
            link.increment_click()
        
        session.pop(session_step_key, None)
        session.pop(session_time_key, None)
        session.pop(session_ip_key, None)
        
        return redirect(link.original_url)
    
    return "Geçersiz adım", 400

# Admin routes
@app.route('/admin')
@app.route('/admin/')
def admin_login_get():
    if session.get('admin_logged_in'):
        return redirect('/admin/panel')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/admin', methods=['POST'])
def admin_login_post():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.get_by_username(username)
    if admin and admin.check_password(password):
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    return render_template_string(ADMIN_PANEL_TEMPLATE)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/admin')

@app.route('/admin/api/links', methods=['GET'])
def api_get_links():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    links = Link.get_all()
    links_data = []
    
    for link in links:
        links_data.append({
            'short_code': link.short_code,
            'original_url': link.original_url,
            'click_count': link.click_count,
            'visits_count': link.visits_count,
            'created_at': link.created_at,
            'is_active': link.is_active
        })
    
    return jsonify(links_data)

@app.route('/admin/api/links/<short_code>', methods=['DELETE'])
def api_delete_link(short_code):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    link = Link.get_by_code(short_code)
    if link:
        link.delete()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Link bulunamadı'}), 404

@app.route('/admin/api/links/<short_code>/toggle', methods=['POST'])
def api_toggle_link(short_code):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    link = Link.get_by_code(short_code)
    if link:
        link.toggle_active()
        return jsonify({'success': True, 'is_active': link.is_active})
    else:
        return jsonify({'error': 'Link bulunamadı'}), 404

@app.route('/admin/api/stats', methods=['GET'])
def api_get_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    stats = Storage.get_stats()
    return jsonify(stats)

@app.route('/admin/api/links/<short_code>/visits', methods=['GET'])
def api_get_link_visits(short_code):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    visits = LinkVisit.get_visits(short_code)
    return jsonify(visits)

# İlk kurulum
def init_app():
    if not Storage.get_admin_user():
        admin = Admin('admin', 'admin123')
        admin.save()
    
    if not Storage.get_ads():
        ads = [
            {'position': 1, 'ad_type': 'banner', 'ad_content': 'Reklam Alanı 1'},
            {'position': 2, 'ad_type': 'banner', 'ad_content': 'Reklam Alanı 2'},
            {'position': 3, 'ad_type': 'banner', 'ad_content': 'Reklam Alanı 3'}
        ]
        Storage.save_ads(ads)

# HTML Templates - Ana sayfa
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkGeç - URL Kısaltma Servisi</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            width: 100%;
            max-width: 600px;
        }
        .logo {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.2em;
        }
        .url-form {
            margin-bottom: 30px;
        }
        .url-input {
            width: 70%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            margin-right: 10px;
        }
        .shorten-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
        }
        .result {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        .short-link {
            font-size: 18px;
            color: #667eea;
            font-weight: bold;
            word-break: break-all;
        }
        .ad-banner {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .admin-link {
            margin-top: 20px;
        }
        .admin-link a {
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔗 LinkGeç</div>
        <div class="subtitle">Hızlı ve Güvenli URL Kısaltma</div>
        
        <div class="ad-banner">
            <iframe data-aa='2406589' src='//acceptable.a-ads.com/2406589' style='border:0px; padding:0; width:100%; height:100%; overflow:hidden; background-color: transparent;'></iframe>
        </div>
        
        <div class="url-form">
            <input type="url" id="urlInput" class="url-input" placeholder="Kısaltmak istediğiniz URL'yi girin..." required>
            <button onclick="shortenUrl()" class="shorten-btn">Kısalt</button>
        </div>
        
        <div id="result" class="result">
            <div>Kısa Linkiniz:</div>
            <div class="short-link" id="shortLink"></div>
        </div>
        
        <div class="admin-link">
            <a href="/admin">Admin Panel</a>
        </div>
    </div>

    <script>
        async function shortenUrl() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                alert('Lütfen bir URL girin');
                return;
            }
            
            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const fullUrl = window.location.origin + data.short_url;
                    document.getElementById('shortLink').innerHTML = `<a href="${fullUrl}" target="_blank">${fullUrl}</a>`;
                    document.getElementById('result').style.display = 'block';
                } else {
                    alert(data.error || 'Bir hata oluştu');
                }
            } catch (error) {
                alert('Bağlantı hatası');
            }
        }
        
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                shortenUrl();
            }
        });
    </script>
</body>
</html>
'''

# Yönlendirme sayfası
REDIRECT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkGeç - Adım {{ step }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            width: 100%;
            max-width: 400px;
        }
        
        .logo {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .step-indicator {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            gap: 8px;
        }
        .step {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: #dee2e6;
            color: #6c757d;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        .step.active {
            background: #667eea;
            color: white;
        }
        .step.completed {
            background: #28a745;
            color: white;
        }
        
        .timer {
            font-size: 3em;
            font-weight: bold;
            color: #e74c3c;
            margin: 25px 0;
        }
        
        .message {
            font-size: 16px;
            color: #555;
            margin-bottom: 20px;
            line-height: 1.4;
        }
        
        .ad-banner {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            color: #6c757d;
            font-size: 14px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            opacity: 0.5;
            pointer-events: none;
            margin: 20px 0;
            width: 100%;
        }
        .btn.active {
            opacity: 1;
            pointer-events: auto;
            background: #28a745;
        }
        .btn:hover.active {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔗 LinkGeç</div>
        
        <div class="step-indicator">
            <div class="step {% if step >= 1 %}{% if step == 1 %}active{% else %}completed{% endif %}{% endif %}">1</div>
            <div class="step {% if step >= 2 %}{% if step == 2 %}active{% else %}completed{% endif %}{% endif %}">2</div>
            <div class="step {% if step >= 3 %}{% if step == 3 %}active{% else %}completed{% endif %}{% endif %}">3</div>
        </div>
        
        <div class="timer" id="timer">15</div>
        <div class="message">
            {% if step == 1 %}
                Linkiniz hazırlanıyor...
            {% elif step == 2 %}
                Güvenlik kontrolü yapılıyor...
            {% elif step == 3 %}
                Son kontroller...
            {% endif %}
        </div>
        
        <div class="ad-banner">
            <iframe data-aa='2406589' src='//acceptable.a-ads.com/2406589' style='border:0px; padding:0; width:100%; height:100%; overflow:hidden; background-color: transparent;'></iframe>
        </div>
        
        <button class="btn" id="continueBtn" onclick="continueToNext()">
            {% if step == 3 %}
                Linke Git
            {% else %}
                Devam Et
            {% endif %}
        </button>
    </div>

    <script>
        let timeLeft = 15;
        let stepStartTime = Date.now();
        
        const timer = document.getElementById('timer');
        const btn = document.getElementById('continueBtn');
        
        const countdown = setInterval(() => {
            timeLeft--;
            timer.textContent = timeLeft;
            
            if (timeLeft <= 0) {
                clearInterval(countdown);
                timer.textContent = '✓';
                timer.style.color = '#28a745';
                btn.classList.add('active');
            }
        }, 1000);
        
        function continueToNext() {
            if (timeLeft > 0) {
                alert('Lütfen bekleyin: ' + timeLeft + ' saniye');
                return;
            }
            
            const elapsed = Date.now() - stepStartTime;
            if (elapsed < 15000) {
                alert('Çok hızlı! Biraz daha bekleyin.');
                return;
            }
            
            const currentStep = {{ step }};
            const shortCode = "{{ short_code }}";
            
            if (currentStep < 3) {
                window.location.href = `/l/${shortCode}/step/${currentStep + 1}`;
            } else {
                window.location.href = `/l/${shortCode}/step/4`;
            }
        }
    </script>
</body>
</html>
'''

# Admin login template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Giriş - LinkGeç</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .logo {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .login-btn:hover {
            transform: translateY(-2px);
        }
        .login-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            display: none;
        }
        .back-link {
            margin-top: 20px;
        }
        .back-link a {
            color: #667eea;
            text-decoration: none;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🔗 LinkGeç</div>
        <div class="subtitle">Admin Paneli</div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Kullanıcı Adı</label>
                <input type="text" id="username" name="username" value="admin" required>
            </div>
            
            <div class="form-group">
                <label for="password">Şifre</label>
                <input type="password" id="password" name="password" value="admin123" required>
            </div>
            
            <button type="submit" class="login-btn" id="loginBtn">Giriş Yap</button>
            
            <div class="error-message" id="errorMessage"></div>
        </form>
        
        <div class="back-link">
            <a href="/">← Ana Sayfaya Dön</a>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            const errorMessage = document.getElementById('errorMessage');
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Giriş yapılıyor...';
            errorMessage.style.display = 'none';
            
            try {
                const response = await fetch('/admin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    window.location.href = '/admin/panel';
                } else {
                    errorMessage.textContent = data.error || 'Giriş başarısız';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                errorMessage.textContent = 'Bağlantı hatası';
                errorMessage.style.display = 'block';
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Giriş Yap';
            }
        });
    </script>
</body>
</html>
'''

# Admin panel template
ADMIN_PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - LinkGeç</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 1.8em;
            font-weight: bold;
        }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.3s;
        }
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .section {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }
        .links-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .links-table th,
        .links-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .links-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
            margin: 0 2px;
            transition: background-color 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-warning {
            background: #ffc107;
            color: #212529;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .status-active { color: #28a745; font-weight: 600; }
        .status-inactive { color: #dc3545; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">🔗 LinkGeç Admin</div>
            <a href="/admin/logout" class="logout-btn">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="totalLinks">-</div>
                <div class="stat-label">Toplam Link</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="activeLinks">-</div>
                <div class="stat-label">Aktif Link</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalClicks">-</div>
                <div class="stat-label">Toplam Tıklama</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalVisits">-</div>
                <div class="stat-label">Toplam Ziyaret</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Link Yönetimi</div>
            <table class="links-table">
                <thead>
                    <tr>
                        <th>Kısa Link</th>
                        <th>Hedef URL</th>
                        <th>Tıklama</th>
                        <th>Ziyaret</th>
                        <th>Durum</th>
                        <th>Oluşturulma</th>
                        <th>İşlemler</th>
                    </tr>
                </thead>
                <tbody id="linksTableBody">
                    <!-- Links will be loaded here -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadLinks();
        });

        async function loadStats() {
            try {
                const response = await fetch('/admin/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalLinks').textContent = stats.total_links.toLocaleString();
                document.getElementById('activeLinks').textContent = stats.active_links.toLocaleString();
                document.getElementById('totalClicks').textContent = stats.total_clicks.toLocaleString();
                document.getElementById('totalVisits').textContent = stats.total_visits.toLocaleString();
            } catch (error) {
                console.error('İstatistikler yüklenemedi:', error);
            }
        }

        async function loadLinks() {
            try {
                const response = await fetch('/admin/api/links');
                const links = await response.json();
                
                const tbody = document.getElementById('linksTableBody');
                tbody.innerHTML = '';
                
                links.forEach(link => {
                    const row = document.createElement('tr');
                    const shortUrl = `${window.location.origin}/l/${link.short_code}`;
                    const createdDate = new Date(link.created_at).toLocaleDateString('tr-TR');
                    
                    row.innerHTML = `
                        <td>
                            <a href="${shortUrl}" target="_blank" style="color: #667eea; text-decoration: none;">
                                ${shortUrl}
                            </a>
                        </td>
                        <td>
                            <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${link.original_url}">
                                ${link.original_url}
                            </div>
                        </td>
                        <td>${link.click_count}</td>
                        <td>${link.visits_count}</td>
                        <td>
                            <span class="${link.is_active ? 'status-active' : 'status-inactive'}">
                                ${link.is_active ? 'Aktif' : 'Pasif'}
                            </span>
                        </td>
                        <td>${createdDate}</td>
                        <td>
                            <button class="btn ${link.is_active ? 'btn-warning' : 'btn-success'}" 
                                    onclick="toggleLink('${link.short_code}')">
                                ${link.is_active ? 'Pasifleştir' : 'Aktifleştir'}
                            </button>
                            <button class="btn btn-danger" onclick="deleteLink('${link.short_code}')">
                                Sil
                            </button>
                        </td>
                    `;
                    
                    tbody.appendChild(row);
                });
            } catch (error) {
                console.error('Linkler yüklenemedi:', error);
            }
        }

        async function toggleLink(shortCode) {
            try {
                const response = await fetch(`/admin/api/links/${shortCode}/toggle`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    await loadLinks();
                    await loadStats();
                }
            } catch (error) {
                console.error('Link durumu değiştirilemedi:', error);
            }
        }

        async function deleteLink(shortCode) {
            if (!confirm('Bu linki silmek istediğinizden emin misiniz?')) {
                return;
            }
            
            try {
                const response = await fetch(`/admin/api/links/${shortCode}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    await loadLinks();
                    await loadStats();
                }
            } catch (error) {
                console.error('Link silinemedi:', error);
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
