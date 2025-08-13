from flask import Blueprint

user_bp = Blueprint('user', __name__)

# Not: Şu an için kullanıcı işlemleri devre dışı
# Tüm işlemler anonim olarak yapılıyor ve veriler dosyalarda saklanıyor