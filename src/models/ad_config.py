"""
CPM Artırıcı Reklam Konfigürasyon Sistemi
Bu modül reklam kodlarının kolay entegrasyonu için tasarlanmıştır.
"""

from src.models.storage import Storage
from typing import Dict, List, Optional
import json

class AdConfigManager:
    """
    Reklam konfigürasyonları için merkezi yönetim sistemi
    Kolay reklam kodu entegrasyonu ve CPM optimizasyonu
    """
    
    # Standart reklam boyutları ve konumları
    AD_POSITIONS = {
        'top_banner': {
            'name': 'Üst Banner',
            'sizes': ['970x90', '728x90', '320x50'],
            'description': 'Sayfa üstü banner reklam alanı'
        },
        'sidebar_left': {
            'name': 'Sol Yan Banner',
            'sizes': ['300x600', '160x600', '300x250'],
            'description': 'Sol yan reklam alanı (sadece desktop)'
        },
        'sidebar_right': {
            'name': 'Sağ Yan Banner', 
            'sizes': ['300x600', '160x600', '300x250'],
            'description': 'Sağ yan reklam alanı (sadece desktop)'
        },
        'content_inline': {
            'name': 'İçerik Arası',
            'sizes': ['728x90', '300x250', '320x50'],
            'description': 'İçerik arası reklam alanı'
        },
        'sticky_footer': {
            'name': 'Sticky Footer',
            'sizes': ['970x90', '728x90', '320x50'],
            'description': 'Sabit alt banner reklam'
        },
        'popup_overlay': {
            'name': 'Popup/Modal',
            'sizes': ['600x400', '500x300'],
            'description': 'Popup overlay reklam'
        },
        'interstitial': {
            'name': 'Tam Sayfa (Interstitial)',
            'sizes': ['800x600', '1024x768'],
            'description': 'Tam sayfa geçiş reklam'
        },
        'popunder': {
            'name': 'Popunder',
            'sizes': ['Tam Sayfa'],
            'description': 'Arka plan popup reklam'
        }
    }
    
    # Reklam ağları ve entegrasyon örnekleri
    AD_NETWORKS = {
        'google_adsense': {
            'name': 'Google AdSense',
            'example_code': '''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXX"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-XXXXXXXXX"
     data-ad-slot="XXXXXXXXX"
     data-ad-format="auto"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
            ''',
            'instructions': 'Google AdSense hesabınızdan aldığınız kodu buraya yapıştırın'
        },
        'media_net': {
            'name': 'Media.net',
            'example_code': '''
<div id="XXXXXXXXX">
    <script type="text/javascript">
        try {
            window._mNHandle.queue.push(function (){
                window._mNDetails.loadTag("XXXXXXXXX", "728x90", "XXXXXXXXX");
            });
        } catch (error) {}
    </script>
</div>
            ''',
            'instructions': 'Media.net panelinden aldığınız tag ID\'sini kullanın'
        },
        'propeller_ads': {
            'name': 'PropellerAds',
            'example_code': '''
<script>
(function(){
    var d = document,
    s = d.createElement('script');
    s.src = 'https://XXXXXXX.propellerads.com/xxxxxxx.js';
    d.head.appendChild(s);
})();
</script>
            ''',
            'instructions': 'PropellerAds zone kodunuzu buraya yerleştirin'
        },
        'custom': {
            'name': 'Özel Reklam Kodu',
            'example_code': '''
<!-- Özel reklam kodunuzu buraya yapıştırın -->
<div class="custom-ad">
    <!-- Reklam içeriği -->
</div>
            ''',
            'instructions': 'Herhangi bir reklam ağının kodunu buraya ekleyebilirsiniz'
        }
    }
    
    @staticmethod
    def get_ad_config() -> Dict:
        """Mevcut reklam konfigürasyonunu getir"""
        from src.models.storage import Storage
        config = Storage._read_json('data/ad_config.json', {
            'enabled': True,
            'positions': {},
            'timing': {
                'popup_delay': 5000,  # 5 saniye
                'interstitial_delay': 8000,  # 8 saniye
                'step_wait_time': 15000  # 15 saniye
            },
            'settings': {
                'show_popup': True,
                'show_interstitial': True,
                'show_popunder': True,
                'enable_ad_block_detection': True,
                'minimum_view_time': 15  # saniye
            }
        })
        return config
    
    @staticmethod
    def save_ad_config(config: Dict):
        """Reklam konfigürasyonunu kaydet"""
        from src.models.storage import Storage
        Storage._write_json('data/ad_config.json', config)
    
    @staticmethod
    def set_ad_code(position: str, network: str, code: str):
        """Belirli konuma reklam kodu ata"""
        config = AdConfigManager.get_ad_config()
        
        if position not in AdConfigManager.AD_POSITIONS:
            raise ValueError(f"Geçersiz pozisyon: {position}")
        
        config['positions'][position] = {
            'network': network,
            'code': code,
            'enabled': True,
            'position_info': AdConfigManager.AD_POSITIONS[position]
        }
        
        AdConfigManager.save_ad_config(config)
    
    @staticmethod
    def get_ad_code(position: str) -> Optional[str]:
        """Belirli konumun reklam kodunu getir"""
        config = AdConfigManager.get_ad_config()
        
        if position in config['positions'] and config['positions'][position]['enabled']:
            return config['positions'][position]['code']
        
        return None
    
    @staticmethod
    def toggle_position(position: str, enabled: bool):
        """Reklam konumunu aktif/pasif yap"""
        config = AdConfigManager.get_ad_config()
        
        if position in config['positions']:
            config['positions'][position]['enabled'] = enabled
            AdConfigManager.save_ad_config(config)
    
    @staticmethod
    def update_timing_settings(popup_delay: int = None, interstitial_delay: int = None, step_wait: int = None):
        """Reklam zamanlama ayarlarını güncelle"""
        config = AdConfigManager.get_ad_config()
        
        if popup_delay is not None:
            config['timing']['popup_delay'] = popup_delay
        if interstitial_delay is not None:
            config['timing']['interstitial_delay'] = interstitial_delay
        if step_wait is not None:
            config['timing']['step_wait_time'] = step_wait
            
        AdConfigManager.save_ad_config(config)
    
    @staticmethod
    def get_cpm_settings() -> Dict:
        """CPM artırıcı ayarları getir"""
        config = AdConfigManager.get_ad_config()
        return {
            'total_ad_positions': len([p for p in config['positions'].values() if p['enabled']]),
            'timing_optimized': config['timing']['step_wait_time'] >= 15000,
            'popup_enabled': config['settings']['show_popup'],
            'interstitial_enabled': config['settings']['show_interstitial'],
            'estimated_cpm_multiplier': AdConfigManager._calculate_cpm_multiplier(config)
        }
    
    @staticmethod
    def _calculate_cpm_multiplier(config: Dict) -> float:
        """CPM çarpanını hesapla"""
        base_multiplier = 1.0
        
        # Aktif reklam konumu sayısına göre
        active_positions = len([p for p in config['positions'].values() if p['enabled']])
        position_multiplier = 1 + (active_positions * 0.15)  # Her konum %15 artış
        
        # Popup/Interstitial bonusu
        popup_bonus = 0.3 if config['settings']['show_popup'] else 0
        interstitial_bonus = 0.4 if config['settings']['show_interstitial'] else 0
        popunder_bonus = 0.2 if config['settings']['show_popunder'] else 0
        
        # Bekleme süresi bonusu
        wait_time_bonus = 0.2 if config['timing']['step_wait_time'] >= 15000 else 0
        
        total_multiplier = position_multiplier + popup_bonus + interstitial_bonus + popunder_bonus + wait_time_bonus
        
        return round(total_multiplier, 2)
    
    @staticmethod
    def generate_config_summary() -> Dict:
        """Reklam konfigürasyon özeti oluştur"""
        config = AdConfigManager.get_ad_config()
        
        return {
            'active_positions': len([p for p in config['positions'].values() if p['enabled']]),
            'total_positions': len(config['positions']),
            'timing_settings': config['timing'],
            'cpm_optimization': AdConfigManager.get_cpm_settings(),
            'recommendations': AdConfigManager._get_optimization_recommendations(config)
        }
    
    @staticmethod
    def _get_optimization_recommendations(config: Dict) -> List[str]:
        """CPM optimizasyonu önerileri"""
        recommendations = []
        
        active_count = len([p for p in config['positions'].values() if p['enabled']])
        
        if active_count < 3:
            recommendations.append("⚡ Daha fazla reklam konumu ekleyerek CPM'i artırabilirsiniz")
        
        if not config['settings']['show_popup']:
            recommendations.append("💰 Popup reklamları aktifleştirerek %30 daha fazla gelir elde edebilirsiniz")
        
        if not config['settings']['show_interstitial']:
            recommendations.append("🎯 Interstitial reklamlar CPM'i %40 artırabilir")
        
        if config['timing']['step_wait_time'] < 15000:
            recommendations.append("⏰ Bekleme süresini 15 saniyeye çıkararak reklam görünürlüğünü artırın")
        
        if 'sidebar_left' not in config['positions'] or not config['positions']['sidebar_left']['enabled']:
            recommendations.append("📊 Sol yan banner ekleyerek desktop kullanıcılardan daha fazla gelir alın")
        
        return recommendations

# Kolay kullanım için yardımcı fonksiyonlar
def setup_google_adsense(client_id: str, slot_ids: Dict[str, str]):
    """Google AdSense hızlı kurulum"""
    for position, slot_id in slot_ids.items():
        code = f'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client_id}"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{client_id}"
     data-ad-slot="{slot_id}"
     data-ad-format="auto"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
        '''
        AdConfigManager.set_ad_code(position, 'google_adsense', code)

def setup_media_net(site_id: str, tag_ids: Dict[str, str]):
    """Media.net hızlı kurulum"""
    for position, tag_id in tag_ids.items():
        size = AdConfigManager.AD_POSITIONS[position]['sizes'][0]
        code = f'''
<div id="{tag_id}">
    <script type="text/javascript">
        try {{
            window._mNHandle.queue.push(function (){{
                window._mNDetails.loadTag("{tag_id}", "{size}", "{site_id}");
            }});
        }} catch (error) {{}}
    </script>
</div>
        '''
        AdConfigManager.set_ad_code(position, 'media_net', code)

def optimize_for_maximum_cpm():
    """Maksimum CPM için otomatik optimizasyon"""
    # Tüm ana konumları aktifleştir
    key_positions = ['top_banner', 'sidebar_left', 'sidebar_right', 'sticky_footer', 'popup_overlay', 'interstitial']
    
    config = AdConfigManager.get_ad_config()
    config['settings'].update({
        'show_popup': True,
        'show_interstitial': True,
        'show_popunder': True,
        'minimum_view_time': 15
    })
    
    config['timing'].update({
        'popup_delay': 5000,
        'interstitial_delay': 8000,
        'step_wait_time': 15000
    })
    
    AdConfigManager.save_ad_config(config)
    return "✅ CPM maksimum optimizasyon ayarları uygulandı!"
