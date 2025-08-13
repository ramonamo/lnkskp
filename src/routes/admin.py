from flask import Blueprint, jsonify, request, render_template_string, session, redirect, url_for
from src.models.link import Link, Admin, AdConfig, LinkVisit
from src.models.storage import Storage
from werkzeug.security import check_password_hash
from src.templates.admin import LOGIN_TEMPLATE, ADMIN_PANEL_TEMPLATE
import functools

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def admin_panel():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    return render_template_string(ADMIN_PANEL_TEMPLATE)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        admin = Admin.get_admin()
        
        if admin and admin['username'] == username and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = username
            if request.is_json:
                return jsonify({'success': True, 'message': 'Giriş başarılı'})
            return redirect(url_for('admin.admin_panel'))
        
        if request.is_json:
            return jsonify({'success': False, 'message': 'Geçersiz kullanıcı adı veya şifre'}), 401
        return render_template_string(LOGIN_TEMPLATE, error='Geçersiz kullanıcı adı veya şifre')
    
    return render_template_string(LOGIN_TEMPLATE)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/api/stats')
@login_required
def api_get_stats():
    return jsonify(Storage.get_stats())

@admin_bp.route('/api/links')
@login_required
def api_get_links():
    links = Link.get_all()
    return jsonify([link.to_dict() for link in links])

@admin_bp.route('/api/links/<short_code>/visits')
@login_required
def api_link_visits(short_code):
    link = Link.get_by_code(short_code)
    if not link:
        return jsonify({'error': 'Link bulunamadı'}), 404
    visits = LinkVisit.get_visits(short_code)
    return jsonify(visits)

@admin_bp.route('/api/links/<short_code>', methods=['DELETE'])
@login_required
def api_delete_link(short_code):
    link = Link.get_by_code(short_code)
    if link:
        link.delete()
        return jsonify({'success': True})
    return jsonify({'error': 'Link bulunamadı'}), 404

@admin_bp.route('/api/links/<short_code>/toggle', methods=['POST'])
@login_required
def api_toggle_link(short_code):
    link = Link.get_by_code(short_code)
    if link:
        link.toggle_active()
        return jsonify(link.to_dict())
    return jsonify({'error': 'Link bulunamadı'}), 404

@admin_bp.route('/api/ads')
@login_required
def api_get_ads():
    return jsonify(AdConfig.get_all())

@admin_bp.route('/api/ads', methods=['POST'])
@login_required
def api_create_ad():
    data = request.json
    ads = AdConfig.get_all()
    new_id = max([ad['id'] for ad in ads] + [0]) + 1
    new_ad = {
        'id': new_id,
        'ad_type': data.get('ad_type'),
        'ad_content': data.get('ad_content'),
        'position': data.get('position', 1),
        'is_active': data.get('is_active', True)
    }
    ads.append(new_ad)
    AdConfig.save_all(ads)
    return jsonify(new_ad), 201

@admin_bp.route('/api/ads/<int:ad_id>', methods=['PUT'])
@login_required
def api_update_ad(ad_id):
    data = request.json
    ads = AdConfig.get_all()
    for ad in ads:
        if ad['id'] == ad_id:
            ad['ad_type'] = data.get('ad_type', ad['ad_type'])
            ad['ad_content'] = data.get('ad_content', ad['ad_content'])
            ad['position'] = data.get('position', ad['position'])
            ad['is_active'] = data.get('is_active', ad['is_active'])
            AdConfig.save_all(ads)
            return jsonify(ad)
    return jsonify({'error': 'Reklam bulunamadı'}), 404

@admin_bp.route('/api/ads/<int:ad_id>', methods=['DELETE'])
@login_required
def api_delete_ad(ad_id):
    ads = AdConfig.get_all()
    ads = [ad for ad in ads if ad['id'] != ad_id]
    AdConfig.save_all(ads)
    return jsonify({'success': True})