from flask import Flask
from flask import render_template , request, redirect ,abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os
import pytz

from linebot import ( WebhookHandler, LineBotApi)
from linebot.exceptions import ( InvalidSignatureError)

from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton,MessageAction
import threading
from datetime import datetime
# import schedule
# from apscheduler.schedulers.background import BackgroundScheduler  
# import time
# ,timedelta
# import requests
# from apscheduler.schedulers.background import BackgroundScheduler
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# import atexit



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

# DATABASE_URL = "sqlite:///inventory.db"
# Model = declarative_base()
# engine = create_engine(DATABASE_URL, echo=True)
# Session = sessionmaker(bind=engine)
# db_session = Session()

# line_bot_api = Configuration(access_token='xokdBq0CmJtxoMSem0dlbgunl1P8tM5yqsqLPr3iY7mZA2eF/rX8/ekiCqBVNwJNbrgK/HYtId9vQaC4EwweVVgBkSmKMe19RjnvscnGDjK7k3edLGNppoFebBZAJLVSERuSIW9S0mJ7UikZMaQmLQdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('454ddcb8ac16d11aeb1bd72b2ff31254')

line_bot_api = LineBotApi("xokdBq0CmJtxoMSem0dlbgunl1P8tM5yqsqLPr3iY7mZA2eF/rX8/ekiCqBVNwJNbrgK/HYtId9vQaC4EwweVVgBkSmKMe19RjnvscnGDjK7k3edLGNppoFebBZAJLVSERuSIW9S0mJ7UikZMaQmLQdB04t89/1O/w1cDnyilFU=")    
handler = WebhookHandler("454ddcb8ac16d11aeb1bd72b2ff31254")    


# login_manager = LoginManager()
# login_manager.init_app(app)

# テーブル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    expiry = db.Column(db.String, nullable=False)
    body = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo")))

# データベースモデル
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    storage = db.Column(db.String(30), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  

    def __repr__(self):
        return f"<Inventory {self.name}>"

# Base.metadata.create_all(engine)

# class User(UserMixin , db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(30) , unique=True)
#     password = db.Column(db.String(12))
   
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

@app.route("/", methods=["GET" , "POST"])
# @login_required
def index():
    if request.method == "GET":
       posts = Post.query.all()
       return render_template("tester.html" , posts=posts)


# @app.route("/signup", methods=["GET" , "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
       
#         user = User(username=username, password=generate_password_hash(password, method="pbkdf2:sha256"))

#         db.session.add(user)
#         db.session.commit()
#         return redirect("/login")
#     else: 
#        return render_template( "signup.html")

# @app.route("/login", methods=["GET" , "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
       
#         user = User.query.filter_by(username=username).first() 
#         if check_password_hash(user.password , password):
#             login_user(user)
#             return redirect("/")
#     else: 
#        return render_template( "login.html")

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect("/login")
  

@app.route("/create", methods=["GET" , "POST"])
# @login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")
        expiry = request.form.get("expiry")
 
        post = Post(title=title, body=body , expiry=expiry )

        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else: 
       return render_template( "create.html")
    
@app.route("/<int:id>/update", methods=["GET" , "POST"])
# @login_required
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        return render_template( "update.html" , post=post)
    else: 
        post.title = request.form.get("title")
        post.body = request.form.get("body")
        post.expiry = request.form.get("expiry")
 

        db.session.commit()
        return redirect("/")

@app.route("/<int:id>/delete", methods=["GET"])
# @login_required
def delete(id):
    post = Post.query.get(id)
   
    db.session.delete(post)
    db.session.commit()
    return redirect("/")


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'
    
# メッセージイベントの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # コマンド処理
    if text == "食材登録":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="食材名を送ってください。例: りんご")        
        )
        UserState.set_state(user_id, "waiting_for_item_name")

    elif text == "レシピ検索":
        # レシピサイトのURLを返信
        recipe_url = "https://www.kurashiru.com/"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"レシピはこちらをご覧ください:\n{recipe_url}")
        )
    elif text == "在庫リスト":
        # データベースから現在の在庫リストを取得
        inventory_items = Inventory.query.filter_by(user_id=user_id).all()
        if inventory_items:
            inventory_list = "\n".join(
                [f" ○品名:{item.name} (保存場所:{item.storage}, 期限:{item.expiration_date}, 在庫数:{item.quantity})" for item in inventory_items]
            )
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"現在の在庫:\n{inventory_list}")
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="現在、在庫はありません。")
            )

    elif text == "食材削除":
        inventory_items = Inventory.query.filter_by(user_id=user_id).all()
        if inventory_items:
            quick_reply_items = [
                QuickReplyButton(action=MessageAction(label=f"{item.name}", text=f"食材削除:{item.id}"))
                for item in inventory_items
            ]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="削除する食材を選択してください。",
                    quick_reply=QuickReply(items=quick_reply_items)
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="現在、削除できる在庫はありません。")
            )
    elif text.startswith("食材削除:"):
        try:
            item_id = int(text.split(":")[1])
            item_to_delete = Inventory.query.filter_by(id=item_id, user_id=user_id).first()
            if item_to_delete:
                db.session.delete(item_to_delete)
                db.session.commit()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{item_to_delete.name} を削除しました。")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="指定された食材が見つかりませんでした。")
                )
        except Exception as e:
            db.session.rollback()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"削除中にエラーが発生しました: {e}")
            )
    
    elif UserState.get_state(user_id) == "waiting_for_item_name":
         UserState.set_data(user_id, "item_name", text)
         UserState.set_state(user_id, "waiting_for_storage_location")
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="保存場所を選んでください。",
                quick_reply=QuickReply(
                    items=[
                         QuickReplyButton(action=MessageAction(label="冷蔵室", text="1")),
                         QuickReplyButton(action=MessageAction(label="冷凍室", text="2")),
                         QuickReplyButton(action=MessageAction(label="野菜室", text="3")),
                         QuickReplyButton(action=MessageAction(label="その他", text="4"))
                    ]
                )
            )
        )
    elif UserState.get_state(user_id) == "waiting_for_storage_location":
        storage_map = {"1": "冷蔵室", "2": "冷凍室", "3": "野菜室" , "4":"その他"}
        if text not in storage_map:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="1, 2, 3 ,4のいずれかを選択してください。")
            )
            return
        UserState.set_data(user_id, "storage", storage_map[text])
        UserState.set_state(user_id, "waiting_for_quantity")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="個数を入力してください (例: 3)")
        )
    elif UserState.get_state(user_id) == "waiting_for_quantity":
        try:
            quantity = int(text)
            if quantity <= 0:
                raise ValueError
            UserState.set_data(user_id, "quantity", quantity)
            UserState.set_state(user_id, "waiting_for_expiration_date")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="期限を入力してください (例: 20240101)")
            )
        except ValueError:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="有効な個数を入力してください (例: 3)")
            )
    elif UserState.get_state(user_id) == "waiting_for_expiration_date":
        try:
            expiration_date = datetime.strptime(text, "%Y%m%d").date()
            item_name = UserState.get_data(user_id, "item_name")
            storage = UserState.get_data(user_id, "storage")
            quantity = UserState.get_data(user_id, "quantity")
            # データベースに保存
            new_item = Inventory(
                user_id=user_id,
                name=item_name,
                storage=storage,
                expiration_date=expiration_date,
                quantity=quantity
            )
            db.session.add(new_item)
            db.session.commit()
            UserState.clear_state(user_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"品名:{item_name} (保存場所:{storage}, 期限:{expiration_date}, 在庫数:{quantity}) を登録しました！"
                )
            )
        except ValueError:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="日付形式が正しくありません。例: 20240101 のように入力してください。")
            )
        except Exception as e:
            db.session.rollback()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"エラーが発生しました: {e}")
            )
    else:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="申し訳ありません。理解できませんでした。")
        )            
    pass       

# def check_expiring_items():
#     today = datetime.date.today()
#     three_days_later = today + datetime.timedelta(days=3)

#     expiring_items = (
#         db.session.query(Inventory)
#         .filter(Inventory.expiration_date <= three_days_later)
#         .filter(Inventory.expiration_date >= today)
#         .all()
#     )

#     for item in expiring_items:
#         try:
#             message = f"【期限間近】\n食材: {item.name}\n保管場所: {item.storage}\n期限: {item.expiration_date}在庫数:\n{item.quantity}"
#             line_bot_api.push_message(item.user_id, TextSendMessage(text=message))
#         except Exception as e:
#             print(f"通知エラー: {e}")





# def notify_expiring_items():
#     while True:
#         now = datetime.now()
#         notify_date = now + timedelta(days=10)  # 3日以内に期限が切れる食材をチェック

#         # items = db_session.query(Inventory).filter(Inventory.expiration_date <= notify_date).all()
#         items = Inventory.query.filter(Inventory.expiration_date <= notify_date).all()
#         for item in items:
#             # 通知メッセージを送信
#             line_bot_api.push_message(
#                 item.user_id,
#                 TextSendMessage(
#                     text=f"食材 '{item.name}' の期限が近づいています！（期限: {item.expiration_date}）"
#                 )
#             )

#         time.sleep(60)  # 毎日チェック（24時間 = 86400秒）

# # 通知スレッドの起動
# def start_notification_thread():
#     thread = threading.Thread(target=notify_expiring_items, daemon=True)
#     thread.start()

# 定期実行のスケジュール設定
# def schedule_tasks():
    # schedule.every().day.at("09:00").do(check_expiring_items)  # 毎朝9時に期限チェック
    # schedule.every(1).minutes.do(check_expiring_items)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# ユーザー状態管理用クラス
class UserState:
    states = {}
    data = {}

    @staticmethod
    def set_state(user_id, state):
        UserState.states[user_id] = state

    @staticmethod
    def get_state(user_id):
        return UserState.states.get(user_id)

    @staticmethod
    def set_data(user_id, key, value):
        if user_id not in UserState.data:
            UserState.data[user_id] = {}
        UserState.data[user_id][key] = value

    @staticmethod
    def get_data(user_id, key):
        return UserState.data.get(user_id, {}).get(key)

    @staticmethod
    def clear_state(user_id):
        UserState.states.pop(user_id, None)
        UserState.data.pop(user_id, None)


if __name__ == '__main__' :
   
    # start_scheduler()
    # threading.Thread(target=lambda: app.run(debug=True, host='0.0.0.0' , port = 8080,use_reloader=False)).start()
    app.debug = True
    app.run(host='0.0.0.0' , port = 8080) 
 
    
