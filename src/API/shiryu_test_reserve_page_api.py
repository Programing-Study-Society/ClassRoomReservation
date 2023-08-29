from flask import Flask, jsonify, redirect, request
from flask import Blueprint

testApi = Blueprint('testApi', __name__, url_prefix='/testApi')



# 'ユーザー個人の予約の取得(/reserve/get/user)'エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/reserve/get/user', methods=['GET'])
def apiTest1():
    print('/reserve/get/userにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
	    'result': True, #Bool型,
	    'message': '失敗メッセージ(理由)', #String型,
	    'data':[{
		    'reservation-id': 'rID101' , #String型,
		    'start-date': '2023-01-01 01:00:00', #Date型,
		    'end-date': '2023-01-01 02:00:00', #Date型,
		    'classroom-name': 'J101', #String型
		    },
            {
		    'reservation-id': 'rID102' , #String型,
		    'start-date': '2023-01-02 01:00:00', #Date型,
		    'end-date': '2023-01-02 02:00:00', #Date型,
		    'classroom-name': 'J102', #String型
		    },
        ]
    }
    return jsonify(response_data)



# 教室の取得(/classroom/get/date)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/classroom/get/date', methods=['POST'])
def apiTest2():
    data = request.get_json()  # JSONデータを取得
    print("/classroom/get data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
		'result': True, # Bool型,
		'message': '失敗メッセージ(理由)', # String型,
		'data': [{
            'classroom-id': 'cID201',#String型
			'classroom-name': 'J201', # String型,
			'start-date': '2023-02-01 02:00:00', # Date型,
			'end-date': '2023-02-01 03:00:00', # Date型
			},
            {
            'classroom-id': 'cID202',#String型
			'classroom-name': 'J202', # String型,
			'start-date': '2023-02-02 02:00:00', # Date型,
			'end-date': '2023-02-02 03:00:00', # Date型
			},
		]
	}
    return jsonify(response_data)



# 予約の追加(/reserve/add)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/reserve/add', methods=['POST'])
def apiTest3():
    data = request.get_json()  # JSONデータを取得
    print("/reserve/add data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
		'result': True, # Bool型,
		'message': '失敗メッセージ(理由)', # String型,
		'data': {
            'reservation-id': 'rID301',#String型
			'start-date': '2023-03-01 03:00:00', # Date型,
			'end-date': '2023-03-01 04:00:00', # Date型
			'classroom-name': 'J301', # String型,
		}
	}
    return jsonify(response_data)



# 予約の削除(/reserve/delete)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/reserve/delete', methods=['POST'])
def apiTest4():
    data = request.get_json()  # JSONデータを取得
    print("/reserve/delete data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
		'result': True, #Bool型,
		'message': '予約削除　成功：黒文字　失敗：赤文字', #String型
	}
    return jsonify(response_data)



# 'ユーザー個人の予約の取得(/reserve/get/user)'エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/reserve/get/full', methods=['GET'])
def apiTest5():
    print('/reserve/get/userにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
		'result': True, #Bool型,
		'message': 'メッセージ', #String型,
		'data':[{
			'reservation-id': 'r501', #String型
			'start-date': '2023-05-01 05:00:00', #Date型,
			'end-date': '2023-05-01 06:00:00', #Date型,
			'classroom-name': 'J501', #String型,
			'user-name': 'プログラミング研究会51号', #String型（管理者おんりー）
			'user-email': 'proken501@gmail.com', #String型（管理者おんりー）
			},
        	{
			'reservation-id': 'r502', #String型
			'start-date': '2023-05-02 05:00:00', #Date型,
			'end-date': '2023-05-02 06:00:00', #Date型,
			'classroom-name': 'J502', #String型,
			'user-name': 'プログラミング研究会52号', #String型（管理者おんりー）
			'user-email': 'proken502@gmail.com', #String型（管理者おんりー）
			},
		]
	}
    return jsonify(response_data)