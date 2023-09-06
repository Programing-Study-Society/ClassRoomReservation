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
	    'message': '失敗メッセージ1(理由)', #String型,
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
		'message': '失敗メッセージ2(理由)', # String型,
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
		'message': '失敗メッセージ3(理由)', # String型,
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
		'message': '失敗：赤文字4', #String型
	}
    return jsonify(response_data)



# 'ユーザー個人の予約の取得(/reserve/get/user)'エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/reserve/get/full', methods=['GET'])
def apiTest5():
    print('/reserve/get/fullにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
		'result': True, #Bool型,
		'message': 'メッセージ5', #String型,
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



# 予約可能教室全ての取得(/classroom/get/full)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/classroom/get/full', methods=['GET'])
def apiTest6():
    print('/classroom/get/fullにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
		'result': True, #Bool型,
		'message': 'メッセージ6', #String型
		'data':[{
			'classroom-id': 'cID601', #String型
			'classroom-name': 'J601', #String型,
			'reservable-start-date': '2023-06-01 06:00:00', #Date型,
			'reservable-end-date': '2023-06-01 07:00:00', #Date型
			},
			{
				'classroom-id': 'cID602', #String型
				'classroom-name': 'J602', #String型,
				'reservable-start-date': '2023-06-02 06:00:00', #Date型,
				'reservable-end-date': '2023-06-02 07:00:00', #Date型
			},
            {
				'classroom-id': 'cID603', #String型
				'classroom-name': 'J603', #String型,
				'reservable-start-date': '2023-06-03 06:00:00', #Date型,
				'reservable-end-date': '2023-06-03 07:00:00', #Date型
			},
		]
	}
    return jsonify(response_data)



# クラスルームIDでの予約の取得(/reserve/get/classroom-id)
@testApi.route('/reserve/get/classroom-id', methods=['POST'])
def apiTest7():
    data = request.get_json()  # JSONデータを取得
    print("/reserve/get/classroom-id data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
	'result': True, #Bool型,
	'message': 'エラーメッセージ7', #String型,
	'data':[{
		'reservation-id': 'r701', #String型,
		'start-date': '2023-07-01 07:00:00', #Date型,
		'end-date': '2023-07-01 08:00:00', #Date型
		'classroom-name': 'J701', #String型,
		'user-name': 'プログラミング研究会71号', #String型（管理者おんりー）
		'user-email': 'proken701@gmail.com', #String型（管理者おんりー）
		},
        {
		'reservation-id': 'r702', #String型,
		'start-date': '2023-07-02 07:00:00', #Date型,
		'end-date': '2023-07-02 08:00:00', #Date型
		'classroom-name': 'J702', #String型,
		'user-name': 'プログラミング研究会72号', #String型（管理者おんりー）
		'user-email': 'proken702@gmail.com', #String型（管理者おんりー）
		},
	]
}
    return jsonify(response_data)



# 教室の削除(/classroom/delete)
@testApi.route('/classroom/delete', methods=['POST'])
def apiTest8():
    data = request.get_json()  # JSONデータを取得
    print("/classroom/delete data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
	'result': True, #Bool型,
	'message': 'メッセージ8', #String型
}
    return jsonify(response_data)



# 教室の追加(/classroom/add)
@testApi.route('/classroom/add', methods=['POST'])
def apiTest9():
    data = request.get_json()  # JSONデータを取得
    print("/classroom/add data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
		'result': True, # Bool型,
		'message': '全て失敗9', # String型(成功 : なし, 失敗（100%失敗のみ） : 理由)
		'classroom': [{
				'result': True, # Bool型,
				'message': '失敗01', # String型(成功 : なし, 失敗 : 理由),
				'data':{
					'classroom-id': 'c901', # String型 非使用,
					'classroom-name': 'J901', # String型,
					'start-date': '2023-09-01 09:00:00', # Date型,
					'end-date': '2023-09-01 10:00:00', # Date型
				}
			},
            {
				'result': True, # Bool型,
				'message': '失敗92', # String型(成功 : なし, 失敗 : 理由),
				'data':{
					'classroom-id': 'c902', # String型 非使用,
					'classroom-name': 'J902', # String型,
					'start-date': '2023-09-02 09:00:00', # Date型,
					'end-date': '2023-09-02 10:00:00', # Date型
				}
			},
            {
				'result': True, # Bool型,
				'message': '失敗93', # String型(成功 : なし, 失敗 : 理由),
				'data':{
					'classroom-id': 'c903', # String型 非使用,
					'classroom-name': 'J903', # String型,
					'start-date': '2023-09-03 09:00:00', # Date型;
					'end-date': '2023-09-03 10:00:00', # Date型
				}
			},
		]
}
    return jsonify(response_data)



# ユーザーの取得(/user/get)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/user/get', methods=['GET'])
def apiTest10():
    print('/user/getにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
	'result': True, # Bool型,
	'message': '失敗メッセージ10', # String型
	'data':[{
		'approved-user-name': 'プログラミング研究会101号', # String型,
		'approved-email': 'proken1001@gmail.com', # String型
		'user-state': 'Admin', # String型
		},
        {
		'approved-user-name': 'プログラミング研究会102号', # String型,
		'approved-email': 'proken1002@gmail.com', # String型
		'user-state': 'Moderator' # String型
		},
        {
		'approved-user-name': 'プログラミング研究会103号', # String型,
		'approved-email': 'proken1003@gmail.com', # String型
		'user-state': 'User', # String型
		},
	]
}
    return jsonify(response_data)



# ユーザー削除(/user/delete)
@testApi.route('/user/delete', methods=['POST'])
def apiTest11():
    data = request.get_json()  # JSONデータを取得
    print("/user/delete data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
	'result': True, #Bool型,
	'message': 'メッセージ11', #String型
	}
    return jsonify(response_data)



# ユーザー追加(/user/add)
@testApi.route('/user/add', methods=['POST'])
def apiTest12():
    data = request.get_json()  # JSONデータを取得
    print("/user/add data : ")
    print(data)
    # 受け取ったデータを処理するなどのロジックを実装
    response_data = {
	'result': True, #Bool型,
	'message': 'メッセージ12', #String型
	}
    return jsonify(response_data)



# 権限の種類の取得(/user/get-authority)エンドポイントにGETリクエストがあった場合に、データを返します
@testApi.route('/user/get-authority', methods=['GET'])
def apiTest13():
    print('/user/get-authorityにアクセス(API)')
    # データを処理するなどのロジックを実装
    response_data = {
	'result': True, # Bool型,
	'message': '失敗メッセージ13', # String型（失敗時のみ）
	'data':[
		{
			'name': 'Admin', # String型
			'is-edit-reserve': True, # Bool型,
			'is-edit-user': True, # Bool型,
		},
		{
			'name': 'Moderator', # String型
			'is-edit-reserve': True, # Bool型,
			'is-edit-user': True, # Bool型,
		},
		{
			'name': 'User', # String型
			'is-edit-reserve': False, # Bool型,
			'is-edit-user': False, # Bool型,
		},
	]
}
    return jsonify(response_data)