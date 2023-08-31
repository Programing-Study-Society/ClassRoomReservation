from flask import Flask
from src.API.reserve import reserve
from src.API.classroom import classroom
from src.API.shiryu_test_reserve_page_api import testApi


app = Flask(__name__, static_folder='./static', static_url_path='/')


app.register_blueprint(reserve)
app.register_blueprint(classroom)
app.register_blueprint(testApi)


@app.errorhandler(404)
def not_found(e):
    print(f'httpステータス:{e.code}, メッセージ:{e.name}, 詳細:{e.description}')
    return app.send_static_file('html/notfound.html')


@app.route('/')
def default_route():
    return app.send_static_file('html/login_page.html')