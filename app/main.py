from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from sqlalchemy import Date
from flask_login import current_user
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/RecordStudio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# таблица с услугами
class Service_list(db.Model):
    tablename = 'service_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    partner_price = db.Column(db.Integer)
    img_url = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'price': self.price, 'partner_price': self.partner_price, 'img_url': self.img_url}

# таблица с администраторами
class Admin_list(db.Model):
    tablename = 'admin_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'login': self.login}
    
# таблица с партнерами
class Partner_list(db.Model):
    tablename = 'partner_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'login': self.login}

# таблица с статусами
class Status(db.Model):
    tablename = 'status'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

# таблица с пользователями
class User(UserMixin, db.Model):
    tablename = 'user'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telegram = db.Column(db.String(120), unique=True, nullable=False)
    hash_password = db.Column(db.String(60), nullable=False)

    def to_dict(self):
        return {'login': self.login, 'telegram': self.telegram}

# таблица с записями
class Reservation(db.Model):
    tablename = 'reservation'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(5000), unique=True, nullable=False)
    check_sum = db.Column(db.Integer)
    status_id = db.Column(db.Integer, nullable=False)
    date = db.Column(Date, unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'comments': self.comments, 'check_sum': self.check_sum, 'status_id': self.status_id, 'date': self.date}

# таблица с датами
class Free_date(db.Model):
    tablename = 'free_date'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    free_date = db.Column(Date, unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'free_date': self.free_date}

# Возвращает все статусы
@app.route('/api/status', methods=['GET'])
def get_status():
    status = Status.query.all()
    return jsonify([s.to_dict() for s in status])

# Возвращает статус по id
@app.route('/api/status_by_id/<int:status_id>', methods=['GET'])
def get_status_by_id(status_id):
    status = Status.query.filter_by(id=status_id).first()
    return {'status': status.name}

# список свободных дат (менее 3х записей)
@app.route('/api/free_dates', methods=['GET'])
def get_free_date():
    free_dates = Free_date.query.order_by(Free_date.free_date.asc()).all()

    # Получить все даты из таблицы Reservation
    reservations = Reservation.query.all()
    reservation_dates = [reservation.date for reservation in reservations]

    # Подсчет количества повторений дат
    date_counts = Counter(reservation_dates)

    # Фильтрация дат, которые встречаются более 3 раз
    filtered_dates = [date for date in free_dates if date.free_date not in date_counts or date_counts[date.free_date] <= 3]

    return jsonify([date.to_dict() for date in filtered_dates])

# добавление даты
@app.route('/api/dates/add', methods=['POST'])
def add_free_date():
    data = request.get_json()
    new_free_date = Free_date(
        free_date=data['free_date']
    )
    db.session.add(new_free_date)
    db.session.commit()
    if not current_user.is_authenticated or not check_admin(current_user.login):
        return jsonify({'error': 'Access denied. Only authenticated admins can access this endpoint.'}), 403
    return jsonify(new_free_date.to_dict())

# удаление даты
@app.route('/api/dates/delete/<int:date_id>', methods=['DELETE'])
def delete_date(date_id):
    date = Free_date.query.get(date_id)
    if not date:
        return jsonify({'message': 'Date not found.'}), 404
    db.session.delete(date)
    db.session.commit()
    if not current_user.is_authenticated or not check_admin(current_user.login):
        return jsonify({'error': 'Access denied. Only authenticated admins can access this endpoint.'}), 403
    return jsonify({'message': 'Date successfully deleted.'}), 200

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# проверка прав администратора
def check_admin(current_login):
    admin_list = Admin_list.query.filter_by(login=current_login).first()

    if admin_list:
        return True
    else:
        return False
        
# проверка прав партнера
def check_partner(current_login):
    partner_list = Partner_list.query.filter_by(login=current_login).first()

    if partner_list:
        return True
    else:
        return False

# регистрация
@app.route('/api/register', methods=['POST'])
def register():
    login = request.json['login']
    email = request.json['email']
    telegram = request.json['telegram']
    hash_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    user = User(login=login, email=email, hash_password=hash_password, telegram=telegram)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'})

# авторизация
@app.route('/api/login', methods=['POST'])
def login():
    login = request.json['login']
    password = request.json['password']
    
    user = User.query.filter_by(login=login).first()
    
    if user and bcrypt.check_password_hash(user.hash_password, password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully!'})
    else:
        return jsonify({'message': 'Invalid login or password!'})

# деавторизация
@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'})

# добавление резерваций
@app.route('/api/reservations/add', methods=['POST'])
def add_reservation():
    data = request.get_json()
    user_id = current_user.id
    new_reservation = Reservation(
        user_id=user_id,
        comments=data['comments'],
        check_sum=data['check_sum'],
        status_id=1,
        date = data['date']

    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify(new_reservation.to_dict())

# отображение резерваций
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    reservations = Reservation.query.all()
    results = []
    if not current_user.is_authenticated or not (check_admin(current_user.login) or check_partner(current_user.login)):
        return jsonify({'error': 'Access denied. Only authenticated admins or partners can access this endpoint.'}), 403
    for r in reservations:
        login = get_user_login(r.user_id)['login']
        status = get_status_by_id(r.status_id)['status']
        reservation_data = r.to_dict()
        reservation_data['login'] = login
        reservation_data['status'] = status
        results.append(reservation_data)
    return jsonify(results)

# найти логин по id пользователя
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_login(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return {'message': 'User not found.'}, 404
    return {'login': user.login}

# логин текущего пользователя
@app.route('/current_user_login', methods=['GET'])
@login_required
def get_current_user_login():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    return jsonify({'login': user.login})

# возвращает список пользователей
@app.route('/api/users', methods=['GET'])
def get_users():
    if not current_user.is_authenticated or not check_admin(current_user.login):
        return jsonify({'error': 'Access denied. Only authenticated admins can access this endpoint.'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# возвращает список записей
@app.route('/api/get_user_reservation', methods=['GET'])
@login_required
def get_user_reservation():
    reservation = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.date).first()
    if reservation:
        return jsonify(reservation.to_dict())
    else:
        return jsonify({})


# изменение статуса записи
@app.route('/api/change_reservation_status/<int:id>', methods=['PATCH'])
def change_reservation_status(id):
    data = request.get_json()
    check_sum = data.get('check_sum')
    status_id = data.get('status_id')

    if not current_user.is_authenticated or not check_admin(current_user.login):
        return jsonify({'error': 'Access denied. Only authenticated admins can access this endpoint.'}), 403

    if check_sum is not None and status_id is not None:
        reservation = Reservation.query.get(id)
        if reservation:
            reservation.check_sum = check_sum
            reservation.status_id = status_id
            db.session.commit()
            return jsonify({'message': 'Status and check_sum successfully updated.'})
        else:
            return jsonify({'message': 'Reservation not found.'}), 404
    else:
        return jsonify({'message': 'Invalid data provided.'}), 400

if __name__ == '__main__':
    app.run(debug=True)