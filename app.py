from flask import Flask, render_template, url_for, redirect, flash, request, abort, jsonify
from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from datetime import datetime
from pytz import timezone

import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def localize_callback(*args, **kwargs):
    return 'このページにアクセスするには、ログインが必要です。'
login_manager.localize_callback = localize_callback

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    info = db.relationship('PersonalInfo', backref='author', lazy='dynamic')

    def __init__(self, email, username, password, administrator):
        self.email = email
        self.username = username
        self.password = password
        self.administrator = administrator

    def __repr__(self):
        return f"UserName: {self.username}"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            return 0


class PersonalInfo(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone('Asia/Tokyo')))   
    time = db.Column(db.Float)
    problem = db.Column(db.String(32))
    
    def __init__(self, user_id, time, problem):
        self.time = time
        self.user_id = user_id
        self.problem = problem
        
    def __repr__(self):
        return f"<PersonalInfo user_id={self.user_id}, time={self.time}, date={self.date}>"
        


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('ログイン')


class RegistrationForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='正しいメールアドレスを入力してください')])
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo('pass_confirm', message='パスワードが一致していません')])
    pass_confirm = PasswordField('パスワード(確認)', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('入力されたユーザー名は既に使われています。')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスは既に登場されています。')

class UpdateUserForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[EqualTo('pass_confirm', message='パスワードが一致していません。')])
    pass_confirm = PasswordField('パスワード(確認)')
    submit = SubmitField('更新')

    def __init__(self, user_id, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.id = user_id

    def validate_email(self, field):
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスは既に登録されています。')

    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError('入力されたユーザー名は既に使われています。')

@app.errorhandler(403)
def error_403(error):
    return render_template('error_pages/403.html'), 403

@app.errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('user_maintenance')
                return redirect(next)
            else:
                flash('パスワードが一致しません')
        else:
            flash('入力されたユーザーは存在しません')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('お疲れ様でした。またトレーニングをがんばりましょう！！')          
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data, administrator="0")
        db.session.add(user)
        db.session.commit()
        flash('ユーザーが登録されました.どんどんトレーニングをしましょう！！')             
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/user_maintenance')
@login_required
def user_maintenance():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=10)
    return render_template('user_maintenance.html', users=users)
    

@app.route('/<int:user_id>/account', methods=['GET', 'POST'])
@login_required
def account(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id and not current_user.is_administrator():
        abort(403)
    form = UpdateUserForm(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        db.session.commit()
        flash('ユーザーアカウントが更新されました')
        return redirect(url_for('user_maintenance'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    return render_template('account.html', form=form)


@app.route('/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user =User.query.get_or_404(user_id)
    if not current_user.is_administrator():
        abort(403)
    if user.is_administrator():
        flash('管理者は削除できません')
        return redirect(url_for('account', user_id=user_id))
    db.session.delete(user)
    db.session.commit()
    flash('ユーザーアカウントが削除されました')
    return redirect(url_for('user_maintenance'))


@app.route('/setting')
@login_required
def setting():
    return render_template("setting.html")
    
        
@app.route('/training')
@login_required
def training():
    problem = request.args.get("problem")
    return render_template("training.html", problem=problem)


@app.route('/training_data')
@login_required
def training_data():
    problem = request.args.get("problem")
    file = problem + ".txt"
    with open(file, "r") as f:
        text = f.readlines()
        clear_text = [""] * len(text)
        for i, line in enumerate(text):
            clear_text[i] = line.strip()
        clear_text = jsonify(list(filter(None, clear_text)))
            
    return clear_text


@app.route('/<int:user_id>/save', methods=['POST'])
@login_required
def save(user_id):
    if user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    time = data.get('time')
    if time is None or not isinstance(time, (int, float)):
        return jsonify({"error": "Invalid or missing 'time'"}), 400
    problem = data.get('level')

    # データベースに保存
    personalinfo = PersonalInfo(user_id, time, problem)
    db.session.add(personalinfo)
    db.session.commit()
    
    return jsonify({"message": "Data saved successfully!", "event": "training-finished"})



@app.route('/')
def index():
    return render_template("index.html")
    

@app.route('/all_record')
@login_required
def all_record():
    easy_records = PersonalInfo.query.filter_by(problem='easy').order_by(PersonalInfo.time.asc()).limit(10).all()
    normal_records = PersonalInfo.query.filter_by(problem='normal').order_by(PersonalInfo.time.asc()).limit(10).all()
    hard_records = PersonalInfo.query.filter_by(problem='hard').order_by(PersonalInfo.time.asc()).limit(10).all()

    return render_template("all_record.html", easy_records=easy_records, normal_records = normal_records, hard_records = hard_records)


@app.route('/<int:user_id>/personal_record')
@login_required

def personal_record(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # 権限確認：管理者 または 自分自身でなければアクセス拒否
    if not current_user.is_administrator() and current_user.id != user_id:
        return abort(403)  
    
    easy_records = PersonalInfo.query.filter_by(problem='easy', user_id=user_id).order_by(PersonalInfo.time.asc()).limit(10).all()
    normal_records = PersonalInfo.query.filter_by(problem='normal', user_id=user_id).order_by(PersonalInfo.time.asc()).limit(10).all()
    hard_records = PersonalInfo.query.filter_by(problem='hard', user_id=user_id).order_by(PersonalInfo.time.asc()).limit(10).all()

    user = User.query.get(user_id)

    return render_template("personal_record.html", user=user, easy_records=easy_records, normal_records = normal_records, hard_records = hard_records)
    

  
@app.route('/tips')
@login_required
def tips():
    return render_template("tips.html")


@app.route("/api/data")
@login_required
def api_data():
    easy_datas = PersonalInfo.query.filter_by(problem='easy', user_id=current_user.id).order_by(PersonalInfo.date.asc())
    normal_datas = PersonalInfo.query.filter_by(problem='normal', user_id=current_user.id).order_by(PersonalInfo.date.asc())
    hard_datas = PersonalInfo.query.filter_by(problem='hard', user_id=current_user.id).order_by(PersonalInfo.date.asc())

    return jsonify({"ex": [easy_data.date.isoformat() for easy_data in easy_datas], "ey": [easy_data.time for easy_data in easy_datas],
                    "nx": [normal_data.date.isoformat() for normal_data in normal_datas], "ny": [normal_data.time for normal_data in normal_datas],
                    "hx": [hard_data.date.isoformat() for hard_data in hard_datas], "hy": [hard_data.time for hard_data in hard_datas]
                    })



if __name__ == '__main__':
    app.run(debug=True)