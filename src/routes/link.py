from flask import Blueprint, jsonify, request, redirect, render_template_string
from src.models.link import Link, LinkVisit, AdConfig
from src.models.storage import Storage
from src.utils.security import rate_limit, validate_url, anti_spam_check, get_client_ip, is_bot_request
import validators

link_bp = Blueprint('link', __name__)

@link_bp.route('/shorten', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)  # Dakikada 5 istek
def shorten_url():
    """URL kısaltma endpoint'i"""
    data = request.json
    original_url = data.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL gerekli'}), 400
    
    # Bot kontrolü
    if is_bot_request():
        return jsonify({'error': 'Bot istekleri kabul edilmiyor'}), 403
    
    # URL güvenlik kontrolü
    is_valid, message = validate_url(original_url)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # URL geçerliliğini kontrol et
    if not validators.url(original_url):
        return jsonify({'error': 'Geçersiz URL formatı'}), 400
    
    # Spam kontrolü
    client_ip = get_client_ip()
    is_spam_free, spam_message = anti_spam_check(client_ip, original_url)
    if not is_spam_free:
        return jsonify({'error': spam_message}), 429
    
    # Link oluştur ve kaydet
    link = Link(original_url)
    
    return jsonify({
        'short_code': link.short_code,
        'short_url': f'/api/l/{link.short_code}',
        'original_url': link.original_url
    }), 201

@link_bp.route('/l/<short_code>')
def redirect_link(short_code):
    """Link yönlendirme sayfası - ilk adım"""
    link = Link.get_by_code(short_code)
    
    if not link or not link.is_active:
        return "Link bulunamadı", 404
    
    # Session'da adım takibi başlat
    from flask import session
    import time
    session[f'link_{short_code}_step'] = 1
    session[f'link_{short_code}_start_time'] = time.time()
    session[f'link_{short_code}_ip'] = get_client_ip()
    
    # Ziyareti kaydet (adım 1) - Aynı IP'den bugün ziyaret yoksa
    client_ip = get_client_ip()
    if not LinkVisit.has_visited_today(short_code, client_ip):
        LinkVisit(
            link_code=short_code,
            ip_address=client_ip,
            user_agent=request.headers.get('User-Agent', ''),
            referrer=request.headers.get('Referer', ''),
            step=1
        )
    
    # İlk reklam konfigürasyonunu al
    ad_config = AdConfig.get_by_position(1)
    
    return render_template_string(REDIRECT_TEMPLATE, 
                                short_code=short_code,
                                step=1,
                                ad_config=ad_config)

@link_bp.route('/l/<short_code>/step/<int:step>')
def redirect_step(short_code, step):
    """Link yönlendirme adımları"""
    link = Link.get_by_code(short_code)
    
    if not link or not link.is_active:
        return "Link bulunamadı", 404
    
    # Session kontrolü - Bypass engelleme
    from flask import session
    import time
    
    session_step_key = f'link_{short_code}_step'
    session_time_key = f'link_{short_code}_start_time'
    session_ip_key = f'link_{short_code}_ip'
    
    # Session kontrolleri
    if session_step_key not in session:
        return redirect(f'/api/l/{short_code}')  # Baştan başlat
    
    current_session_step = session.get(session_step_key, 0)
    session_ip = session.get(session_ip_key, '')
    current_ip = get_client_ip()
    
    # IP değişmiş mi kontrol et
    if session_ip != current_ip:
        return redirect(f'/api/l/{short_code}')  # Baştan başlat
    
    # Sıralı adım kontrolü - Atlama yasak
    if step != current_session_step + 1:
        return redirect(f'/api/l/{short_code}')  # Baştan başlat
    
    # Minimum süre kontrolü (her adım min 15 saniye)
    start_time = session.get(session_time_key, 0)
    if time.time() - start_time < (current_session_step * 15):
        return render_template_string(ERROR_TEMPLATE, 
                                    error_title="⏰ Çok Hızlı İlerliyorsunuz!",
                                    error_message="Reklam süresi henüz tamamlanmadı. Lütfen bekleyin ve tekrar deneyin.",
                                    redirect_url=f"/api/l/{short_code}",
                                    redirect_text="Başa Dön")
    
    # Session'ı güncelle
    session[session_step_key] = step
    
    if step == 2:
        # İkinci adım - ikinci reklam
        ad_config = AdConfig.get_by_position(2)
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=2
            )
        return render_template_string(REDIRECT_TEMPLATE, 
                                    short_code=short_code,
                                    step=2,
                                    ad_config=ad_config)
    elif step == 3:
        # Üçüncü adım - son reklam
        ad_config = AdConfig.get_by_position(3)
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=3
            )
        return render_template_string(REDIRECT_TEMPLATE, 
                                    short_code=short_code,
                                    step=3,
                                    ad_config=ad_config)
    elif step == 4:
        # Son adım - asıl linke yönlendir
        client_ip = get_client_ip()
        if not LinkVisit.has_visited_today(short_code, client_ip):
            LinkVisit(
                link_code=short_code,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.headers.get('Referer', ''),
                step=4
            )
            # Yalnızca yeni ziyaretçiler için tıklama sayısını artır
            link.increment_click()
        
        # Session'ı temizle
        session.pop(session_step_key, None)
        session.pop(session_time_key, None)
        session.pop(session_ip_key, None)
        
        return redirect(link.original_url)
    
    return "Geçersiz adım", 400

@link_bp.route('/public-stats', methods=['GET'])
def public_stats():
    """Herkese açık istatistikler"""
    return jsonify(Storage.get_stats())

# HTML Templates
ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ error_title }} - LinkGeç</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
            width: 100%;
            transform: translateY(0);
            transition: transform 0.3s ease;
        }
        .container:hover {
            transform: translateY(-5px);
        }
        .logo {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 30px;
        }
        .error-icon {
            font-size: 4em;
            margin-bottom: 20px;
            display: block;
            animation: pulse 2s infinite;
        }
        .error-title {
            font-size: 1.8em;
            font-weight: 600;
            color: #e74c3c;
            margin-bottom: 20px;
        }
        .error-message {
            font-size: 1.1em;
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .countdown {
            font-size: 1.2em;
            color: #667eea;
            margin-top: 20px;
            font-weight: 600;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔗 LinkGeç</div>
        <div class="error-icon">⏰</div>
        <div class="error-title">Çok Hızlı İlerliyorsunuz!</div>
        <div class="error-message">{{ error_message }}</div>
        
        <a href="{{ redirect_url }}" class="btn">{{ redirect_text }}</a>
        
        <div class="countdown" id="countdown">
            Otomatik yönlendirme: <span id="timer">10</span> saniye
        </div>
    </div>

    <script>
        let timeLeft = 10;
        const timerElement = document.getElementById('timer');
        
        const countdown = setInterval(() => {
            timeLeft--;
            timerElement.textContent = timeLeft;
            
            if (timeLeft <= 0) {
                clearInterval(countdown);
                window.location.href = "{{ redirect_url }}";
            }
        }, 1000);
        
        // Sayfa yüklendiğinde odaklan
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelector('.btn').focus();
        });
    </script>
</body>
</html>
'''

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
        
        /* Mobil First - Minimal Container */
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
        
        /* Minimal Reklam Alanı */
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
        
        /* Mobil için footer reklam */
        .ad-footer {
            background: #f8f9fa;
            border-top: 2px dashed #dee2e6;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <!-- Minimal Mobil Container -->
    <div class="container">
        <div class="logo">🔗 LinkGeç</div>
        
        <div class="step-indicator">
            <div class="step {% if step >= 1 %}{% if step == 1 %}active{% else %}completed{% endif %}{% endif %}">1</div>
            <div class="step {% if step >= 2 %}{% if step == 2 %}active{% else %}completed{% endif %}{% endif %}">2</div>
            <div class="step {% if step >= 3 %}{% if step == 3 %}active{% else %}completed{% endif %}{% endif %}">3</div>
        </div>
        
        {% if step < 4 %}
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
        
        <!-- Gerçek Reklam Alanı -->
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
        
        <!-- Mobil Footer Reklam -->
        <div class="ad-footer">
            <iframe data-aa='2406589' src='//acceptable.a-ads.com/2406589' style='border:0px; padding:0; width:100%; height:60px; overflow:hidden; background-color: transparent;'></iframe>
        </div>
        {% endif %}
    </div>

    <script>
        // Mobil Optimized Timer
        let timeLeft = 15;
        let stepStartTime = Date.now();
        
        const timer = document.getElementById('timer');
        const btn = document.getElementById('continueBtn');
        
        // Timer başlat
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
                window.location.href = `/api/l/${shortCode}/step/${currentStep + 1}`;
            } else {
                window.location.href = `/api/l/${shortCode}/step/4`;
            }
        }
    </script>
</body>
</html>
'''