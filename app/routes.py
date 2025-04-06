from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        # Обработка формы создания профиля
        pass
    return render_template('create_profile.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Обработка формы поиска
        return redirect(url_for('main.result'))
    return render_template('search.html')

@main.route('/result')
def result():
    # Показать результаты поиска
    return render_template('result.html')

@main.route('/dialog/<int:user_id>')
def dialog(user_id):
    # Показать диалог с пользователем
    return render_template('dialog.html', user_id=user_id)
