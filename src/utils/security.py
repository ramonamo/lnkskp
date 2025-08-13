import time
import hashlib
from collections import defaultdict
from flask import request, jsonify
import functools

# Rate limiting için basit in-memory store
rate_limit_store = defaultdict(list)
failed_attempts = defaultdict(int)

def rate_limit(max_requests=10, window_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # IP adresini al
            ip = get_client_ip()
            current_time = time.time()
            
            # Eski istekleri temizle
            rate_limit_store[ip] = [
                timestamp for timestamp in rate_limit_store[ip]
                if current_time - timestamp < window_seconds
            ]
            
            # Rate limit kontrolü
            if len(rate_limit_store[ip]) >= max_requests:
                return jsonify({
                    'error': 'Çok fazla istek. Lütfen biraz bekleyin.',
                    'retry_after': window_seconds
                }), 429
            
            # İsteği kaydet
            rate_limit_store[ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_client_ip():
    """Gerçek client IP adresini al"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def is_bot_request():
    """Bot isteği kontrolü"""
    user_agent = request.headers.get('User-Agent', '').lower()
    
    bot_indicators = [
        'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
        'python-requests', 'http', 'automated', 'script'
    ]
    
    return any(indicator in user_agent for indicator in bot_indicators)

def validate_url(url):
    """URL güvenlik kontrolü"""
    if not url:
        return False, "URL boş olamaz"
    
    # Kötü amaçlı URL kontrolü
    dangerous_domains = [
        'malware.com', 'phishing.com', 'spam.com'
        # Gerçek uygulamada daha kapsamlı bir liste kullanılmalı
    ]
    
    url_lower = url.lower()
    for domain in dangerous_domains:
        if domain in url_lower:
            return False, "Güvenlik nedeniyle bu URL kısaltılamaz"
    
    # Yasaklı protokoller
    if url_lower.startswith(('javascript:', 'data:', 'file:', 'ftp:')):
        return False, "Bu protokol desteklenmiyor"
    
    return True, "OK"

def anti_spam_check(ip, url):
    """Spam kontrolü"""
    current_time = time.time()
    
    # Aynı IP'den çok hızlı istek kontrolü
    if ip in rate_limit_store:
        recent_requests = [
            timestamp for timestamp in rate_limit_store[ip]
            if current_time - timestamp < 10  # Son 10 saniye
        ]
        if len(recent_requests) > 3:
            return False, "Çok hızlı istek gönderiyorsunuz"
    
    # Aynı URL'yi tekrar kısaltma kontrolü (basit)
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_key = f"{ip}_{url_hash}"
    
    # Bu kontrolü gerçek uygulamada veritabanında yapmalısınız
    return True, "OK"

def security_headers(response):
    """Güvenlik başlıklarını ekle"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

def clean_old_data():
    """Eski rate limit verilerini temizle"""
    current_time = time.time()
    for ip in list(rate_limit_store.keys()):
        rate_limit_store[ip] = [
            timestamp for timestamp in rate_limit_store[ip]
            if current_time - timestamp < 3600  # 1 saat
        ]
        if not rate_limit_store[ip]:
            del rate_limit_store[ip]

