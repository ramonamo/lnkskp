import string
import random
from datetime import datetime
from typing import Dict, List, Optional
from .storage import Storage

class Link:
    def __init__(self, original_url: str, short_code: str = None):
        self.original_url = original_url
        self.short_code = short_code or self.generate_short_code()
        self.created_at = datetime.utcnow()
        self.click_count = 0
        self.is_active = True
        self.save()
    
    def to_dict(self) -> Dict:
        visits = Storage.get_visits(self.short_code)
        return {
            'original_url': self.original_url,
            'short_code': self.short_code,
            'created_at': self.created_at.isoformat(),
            'click_count': self.click_count,
            'is_active': self.is_active,
            'visits_count': len(visits)
        }
    
    def save(self):
        """Linki kaydet"""
        Storage.save_link(self.to_dict())
    
    def delete(self):
        """Linki sil"""
        Storage.delete_link(self.short_code)
    
    def increment_click(self):
        """Tıklama sayısını artır"""
        self.click_count += 1
        self.save()
    
    def toggle_active(self):
        """Aktif/pasif durumunu değiştir"""
        self.is_active = not self.is_active
        self.save()
        return self
    
    @staticmethod
    def get_all() -> List['Link']:
        """Tüm linkleri getir"""
        links = []
        for data in Storage.get_all_links():
            link = Link(data['original_url'], data['short_code'])
            link.created_at = datetime.fromisoformat(data['created_at'])
            link.click_count = data['click_count']
            link.is_active = data['is_active']
            links.append(link)
        return links
    
    @staticmethod
    def get_by_code(short_code: str) -> Optional['Link']:
        """Kısa kod ile link getir"""
        data = Storage.get_link(short_code)
        if data:
            link = Link(data['original_url'], data['short_code'])
            link.created_at = datetime.fromisoformat(data['created_at'])
            link.click_count = data['click_count']
            link.is_active = data['is_active']
            return link
        return None
    
    @staticmethod
    def generate_short_code(length=6) -> str:
        """Benzersiz kısa kod oluştur"""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not Storage.get_link(code):
                return code

class LinkVisit:
    def __init__(self, link_code: str, ip_address: str, user_agent: str, referrer: str, step: int):
        self.link_code = link_code
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.referrer = referrer
        self.step = step
        self.visited_at = datetime.utcnow()
        self.save()
    
    def to_dict(self) -> Dict:
        return {
            'link_code': self.link_code,
            'visited_at': self.visited_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'step': self.step
        }
    
    def save(self):
        """Ziyareti kaydet"""
        Storage.save_visit(self.link_code, self.to_dict())
    
    @staticmethod
    def has_visited_today(link_code: str, ip_address: str) -> bool:
        """Bugün aynı IP'den ziyaret var mı kontrol et"""
        from datetime import datetime, timedelta
        visits = Storage.get_visits(link_code)
        today = datetime.utcnow().date()
        
        for visit in visits:
            visit_date = datetime.fromisoformat(visit['visited_at']).date()
            if visit_date == today and visit['ip_address'] == ip_address:
                return True
        return False
    
    @staticmethod
    def get_visits(link_code: str) -> List[Dict]:
        """Link'in ziyaret kayıtlarını getir"""
        return Storage.get_visits(link_code)

class Admin:
    @staticmethod
    def get_admin() -> Optional[Dict]:
        """Admin bilgilerini getir"""
        return Storage.get_admin()
    
    @staticmethod
    def save_admin(username: str, password_hash: str):
        """Admin bilgilerini kaydet"""
        admin = {
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat()
        }
        Storage.save_admin(admin)

class AdConfig:
    @staticmethod
    def get_all() -> List[Dict]:
        """Tüm reklam ayarlarını getir"""
        return Storage.get_ads()
    
    @staticmethod
    def save_all(ads: List[Dict]):
        """Reklam ayarlarını kaydet"""
        Storage.save_ads(ads)
    
    @staticmethod
    def get_by_position(position: int) -> Optional[Dict]:
        """Pozisyona göre aktif reklam getir"""
        ads = Storage.get_ads()
        for ad in ads:
            if ad['position'] == position and ad.get('is_active', True):
                return ad
        return None