import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Veri dizinleri
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
LINKS_DIR = os.path.join(DATA_DIR, 'links')
VISITS_DIR = os.path.join(DATA_DIR, 'visits')
ADS_FILE = os.path.join(DATA_DIR, 'ads.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')
ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')

# Dizinleri oluştur
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LINKS_DIR, exist_ok=True)
os.makedirs(VISITS_DIR, exist_ok=True)

class Storage:
    @staticmethod
    def save_link(data: Dict) -> None:
        """Link verisini kaydet"""
        code = data['short_code']
        file_path = os.path.join(LINKS_DIR, f"{code}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_link(code: str) -> Optional[Dict]:
        """Link verisini getir"""
        file_path = os.path.join(LINKS_DIR, f"{code}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def get_all_links() -> List[Dict]:
        """Tüm linkleri getir"""
        links = []
        for file_name in os.listdir(LINKS_DIR):
            if file_name.endswith('.json'):
                with open(os.path.join(LINKS_DIR, file_name), 'r', encoding='utf-8') as f:
                    links.append(json.load(f))
        return sorted(links, key=lambda x: x['created_at'], reverse=True)
    
    @staticmethod
    def delete_link(code: str) -> bool:
        """Link verisini sil"""
        file_path = os.path.join(LINKS_DIR, f"{code}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            # Ziyaret kayıtlarını da sil
            visit_dir = os.path.join(VISITS_DIR, code)
            if os.path.exists(visit_dir):
                for f in os.listdir(visit_dir):
                    os.remove(os.path.join(visit_dir, f))
                os.rmdir(visit_dir)
            return True
        return False
    
    @staticmethod
    def save_visit(code: str, visit_data: Dict) -> None:
        """Ziyaret kaydı ekle"""
        visit_dir = os.path.join(VISITS_DIR, code)
        os.makedirs(visit_dir, exist_ok=True)
        visits_file = os.path.join(visit_dir, 'visits.json')
        
        visits = []
        if os.path.exists(visits_file):
            with open(visits_file, 'r', encoding='utf-8') as f:
                visits = json.load(f)
        
        visits.append(visit_data)
        
        with open(visits_file, 'w', encoding='utf-8') as f:
            json.dump(visits, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_visits(code: str) -> List[Dict]:
        """Link'in ziyaret kayıtlarını getir"""
        visits_file = os.path.join(VISITS_DIR, code, 'visits.json')
        if os.path.exists(visits_file):
            with open(visits_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def get_ads() -> List[Dict]:
        """Reklam ayarlarını getir"""
        if os.path.exists(ADS_FILE):
            with open(ADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def save_ads(ads: List[Dict]) -> None:
        """Reklam ayarlarını kaydet"""
        with open(ADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ads, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_admin() -> Optional[Dict]:
        """Admin bilgilerini getir"""
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def save_admin(admin_data: Dict) -> None:
        """Admin bilgilerini kaydet"""
        with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_stats() -> Dict:
        """İstatistikleri hesapla"""
        links = Storage.get_all_links()
        total_links = len(links)
        active_links = sum(1 for link in links if link.get('is_active', True))
        total_clicks = sum(link.get('click_count', 0) for link in links)
        
        stats = {
            'total_links': total_links,
            'active_links': active_links,
            'total_clicks': total_clicks,
            'total_visits': sum(len(Storage.get_visits(link['short_code'])) for link in links)
        }
        
        # İstatistikleri dosyaya da kaydedelim
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        return stats

# İlk çalıştırmada varsayılan verileri oluştur
if not os.path.exists(ADMIN_FILE):
    from werkzeug.security import generate_password_hash
    Storage.save_admin({
        'username': 'admin',
        'password_hash': generate_password_hash('admin123'),
        'created_at': datetime.utcnow().isoformat()
    })

if not os.path.exists(ADS_FILE):
    default_ads = [
        {
            'id': 1,
            'ad_type': 'banner',
            'ad_content': '<div style="padding:10px;">728x90 Banner Alanı (Örnek)</div>',
            'position': 1,
            'is_active': True
        },
        {
            'id': 2,
            'ad_type': 'popup',
            'ad_content': '',
            'position': 2,
            'is_active': True
        },
        {
            'id': 3,
            'ad_type': 'banner',
            'ad_content': '<div style="padding:10px;">300x250 Banner Alanı (Örnek)</div>',
            'position': 3,
            'is_active': True
        }
    ]
    Storage.save_ads(default_ads)
