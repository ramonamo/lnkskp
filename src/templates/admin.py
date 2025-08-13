LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Girişi - LinkGeç</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .error {
            color: #e74c3c;
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🔗 LinkGeç</div>
        <form method="POST">
            <div class="form-group">
                <label for="username">Kullanıcı Adı:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Şifre:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Giriş Yap</button>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

ADMIN_PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Paneli - LinkGeç</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: #667eea;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 1.5em;
            font-weight: bold;
        }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .tabs {
            display: flex;
            background: white;
            border-radius: 10px 10px 0 0;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .tab {
            flex: 1;
            padding: 15px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            background: white;
            padding: 20px;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .tab-pane {
            display: none;
        }
        .tab-pane.active {
            display: block;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        .btn-success {
            background: #27ae60;
        }
        .btn-success:hover {
            background: #229954;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: bold;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 15% auto;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 500px;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: black;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🔗 LinkGeç Admin</div>
        <a href="/admin/logout" class="logout-btn">Çıkış Yap</a>
    </div>
    
    <div class="container">
        <div class="stats" id="stats">
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
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('links')">Linkler</button>
            <button class="tab" onclick="showTab('ads')">Reklamlar</button>
            <button class="tab" onclick="showTab('shorten')">Link Kısalt</button>
        </div>
        
        <div class="tab-content">
            <div id="links" class="tab-pane active">
                <h3>Link Yönetimi</h3>
                <table id="linksTable">
                    <thead>
                        <tr>
                            <th>Kısa Link</th>
                            <th>Orijinal URL</th>
                            <th>Tıklama</th>
                            <th>Ziyaret</th>
                            <th>Durum</th>
                            <th>Tarih</th>
                            <th>İşlemler</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div id="ads" class="tab-pane">
                <h3>Reklam Yönetimi</h3>
                <button class="btn" onclick="showAddAdModal()">Yeni Reklam Ekle</button>
                <table id="adsTable">
                    <thead>
                        <tr>
                            <th>Tip</th>
                            <th>Pozisyon</th>
                            <th>Durum</th>
                            <th>İşlemler</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div id="shorten" class="tab-pane">
                <h3>Link Kısalt</h3>
                <div class="form-group">
                    <label for="urlInput">URL:</label>
                    <input type="url" id="urlInput" placeholder="https://example.com">
                </div>
                <button class="btn" onclick="shortenUrl()">Kısalt</button>
                <div id="shortenResult" style="margin-top: 20px;"></div>
            </div>
        </div>
    </div>
    
    <!-- Reklam Ekleme Modal -->
    <div id="adModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAdModal()">&times;</span>
            <h3>Reklam Ekle/Düzenle</h3>
            <form id="adForm">
                <div class="form-group">
                    <label for="adType">Reklam Tipi:</label>
                    <select id="adType">
                        <option value="banner">Banner</option>
                        <option value="popup">Popup</option>
                        <option value="redirect">Yönlendirme</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="adPosition">Pozisyon:</label>
                    <select id="adPosition">
                        <option value="1">1. Adım</option>
                        <option value="2">2. Adım</option>
                        <option value="3">3. Adım</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="adContent">İçerik (HTML/URL):</label>
                    <textarea id="adContent" rows="4"></textarea>
                </div>
                <button type="submit" class="btn">Kaydet</button>
            </form>
        </div>
    </div>

    <script>
        let currentAdId = null;
        
        // Sayfa yüklendiğinde verileri getir
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadLinks();
            loadAds();
        });
        
        function showTab(tabName) {
            // Tüm tab'ları gizle
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Seçili tab'ı göster
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/admin/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalLinks').textContent = stats.total_links;
                document.getElementById('activeLinks').textContent = stats.active_links;
                document.getElementById('totalClicks').textContent = stats.total_clicks;
                document.getElementById('totalVisits').textContent = stats.total_visits;
            } catch (error) {
                console.error('İstatistikler yüklenemedi:', error);
            }
        }
        
        async function loadLinks() {
            try {
                const response = await fetch('/admin/api/links');
                const links = await response.json();
                
                const tbody = document.querySelector('#linksTable tbody');
                tbody.innerHTML = '';
                
                links.forEach(link => {
                    const shortUrl = `${window.location.origin}/api/l/${link.short_code}`;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><a href="${shortUrl}" target="_blank" style="color: #667eea; font-weight: bold;">${shortUrl}</a></td>
                        <td><a href="${link.original_url}" target="_blank">${link.original_url.substring(0, 50)}...</a></td>
                        <td>${link.click_count}</td>
                        <td>${link.visits_count}</td>
                        <td>${link.is_active ? '<span style="color: green;">Aktif</span>' : '<span style="color: red;">Pasif</span>'}</td>
                        <td>${new Date(link.created_at).toLocaleDateString('tr-TR')}</td>
                        <td>
                            <button class="btn ${link.is_active ? 'btn-danger' : 'btn-success'}" onclick="toggleLink('${link.short_code}')">
                                ${link.is_active ? 'Pasifleştir' : 'Aktifleştir'}
                            </button>
                            <button class="btn" onclick="showVisits('${link.short_code}')">Ziyaretler</button>
                            <button class="btn btn-danger" onclick="deleteLink('${link.short_code}')">Sil</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (error) {
                console.error('Linkler yüklenemedi:', error);
            }
        }
        
        async function loadAds() {
            try {
                const response = await fetch('/admin/api/ads');
                const ads = await response.json();
                
                const tbody = document.querySelector('#adsTable tbody');
                tbody.innerHTML = '';
                
                ads.forEach(ad => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${ad.ad_type}</td>
                        <td>${ad.position}. Adım</td>
                        <td>${ad.is_active ? '<span style="color: green;">Aktif</span>' : '<span style="color: red;">Pasif</span>'}</td>
                        <td>
                            <button class="btn" onclick="editAd(${ad.id})">Düzenle</button>
                            <button class="btn btn-danger" onclick="deleteAd(${ad.id})">Sil</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (error) {
                console.error('Reklamlar yüklenemedi:', error);
            }
        }
        
        async function toggleLink(shortCode) {
            try {
                const response = await fetch(`/admin/api/links/${shortCode}/toggle`, { method: 'POST' });
                if (response.ok) {
                    loadLinks();
                    loadStats();
                } else {
                    console.error('Link durumu değiştirilemedi:', response.status);
                }
            } catch (error) {
                console.error('Link durumu değiştirilemedi:', error);
            }
        }
        
        async function deleteLink(shortCode) {
            if (confirm('Bu linki silmek istediğinizden emin misiniz?')) {
                try {
                    await fetch(`/admin/api/links/${shortCode}`, { method: 'DELETE' });
                    loadLinks();
                    loadStats();
                } catch (error) {
                    console.error('Link silinemedi:', error);
                }
            }
        }
        
        async function showVisits(shortCode) {
            try {
                const response = await fetch(`/admin/api/links/${shortCode}/visits`);
                const visits = await response.json();
                const modal = document.getElementById('adModal');
                const content = modal.querySelector('.modal-content');
                content.innerHTML = `
                    <span class="close" onclick="closeAdModal()">&times;</span>
                    <h3>${shortCode} - Ziyaret Kayıtları</h3>
                    <div style="max-height: 60vh; overflow: auto;">
                        <table style="width:100%; border-collapse: collapse;">
                            <thead>
                                <tr>
                                    <th style="text-align:left; padding:8px; border-bottom:1px solid #eee;">Zaman</th>
                                    <th style="text-align:left; padding:8px; border-bottom:1px solid #eee;">IP</th>
                                    <th style="text-align:left; padding:8px; border-bottom:1px solid #eee;">Adım</th>
                                    <th style="text-align:left; padding:8px; border-bottom:1px solid #eee;">Referrer</th>
                                    <th style="text-align:left; padding:8px; border-bottom:1px solid #eee;">Kullanıcı Aracısı</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${visits.map(v => `
                                    <tr>
                                        <td style="padding:8px; border-bottom:1px solid #f2f2f2;">${new Date(v.visited_at).toLocaleString('tr-TR')}</td>
                                        <td style="padding:8px; border-bottom:1px solid #f2f2f2;">${v.ip_address || '-'}</td>
                                        <td style="padding:8px; border-bottom:1px solid #f2f2f2;">${v.step}</td>
                                        <td style="padding:8px; border-bottom:1px solid #f2f2f2;">${v.referrer || '-'}</td>
                                        <td style="padding:8px; border-bottom:1px solid #f2f2f2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:260px;" title="${v.user_agent || ''}">${v.user_agent || '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
                modal.style.display = 'block';
            } catch (error) {
                console.error('Ziyaret kayıtları yüklenemedi:', error);
            }
        }
        
        async function shortenUrl() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                alert('Lütfen bir URL girin');
                return;
            }
            
            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('shortenResult').innerHTML = `
                        <div style="background: #d4edda; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb;">
                            <strong>Başarılı!</strong><br>
                            Kısa Link: <a href="${result.short_url}" target="_blank">${window.location.origin}${result.short_url}</a><br>
                            Kısa Kod: ${result.short_code}
                        </div>
                    `;
                    document.getElementById('urlInput').value = '';
                    loadLinks();
                    loadStats();
                } else {
                    document.getElementById('shortenResult').innerHTML = `
                        <div style="background: #f8d7da; padding: 15px; border-radius: 5px; border: 1px solid #f5c6cb;">
                            <strong>Hata:</strong> ${result.error}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('URL kısaltılamadı:', error);
            }
        }
        
        function showAddAdModal() {
            currentAdId = null;
            document.getElementById('adForm').reset();
            document.getElementById('adModal').style.display = 'block';
        }
        
        function closeAdModal() {
            document.getElementById('adModal').style.display = 'none';
        }
        
        async function editAd(adId) {
            try {
                const response = await fetch('/admin/api/ads');
                const ads = await response.json();
                const ad = ads.find(a => a.id === adId);
                
                if (ad) {
                    currentAdId = adId;
                    document.getElementById('adType').value = ad.ad_type;
                    document.getElementById('adPosition').value = ad.position;
                    document.getElementById('adContent').value = ad.ad_content;
                    document.getElementById('adModal').style.display = 'block';
                }
            } catch (error) {
                console.error('Reklam bilgileri alınamadı:', error);
            }
        }
        
        async function deleteAd(adId) {
            if (confirm('Bu reklamı silmek istediğinizden emin misiniz?')) {
                try {
                    await fetch(`/admin/api/ads/${adId}`, { method: 'DELETE' });
                    loadAds();
                } catch (error) {
                    console.error('Reklam silinemedi:', error);
                }
            }
        }
        
        document.getElementById('adForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const adData = {
                ad_type: document.getElementById('adType').value,
                position: parseInt(document.getElementById('adPosition').value),
                ad_content: document.getElementById('adContent').value,
                is_active: true
            };
            
            try {
                let response;
                if (currentAdId) {
                    response = await fetch(`/admin/api/ads/${currentAdId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(adData)
                    });
                } else {
                    response = await fetch('/admin/api/ads', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(adData)
                    });
                }
                
                if (response.ok) {
                    closeAdModal();
                    loadAds();
                } else {
                    alert('Reklam kaydedilemedi');
                }
            } catch (error) {
                console.error('Reklam kaydedilemedi:', error);
            }
        });
        
        // Modal dışına tıklandığında kapat
        window.onclick = function(event) {
            const modal = document.getElementById('adModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''
