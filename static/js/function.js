const LOCATION_URL = '';

function reserveationApplication(classroomId, reserveationData)
{
    if (!confirm('この時間・教室で予約を確定しますか？'))
    {
        alert('予約をキャンセルしました');
        return 0;
    }

    //教室idを含めたjsonを作成
    reserveationData["classroom_id"] = classroomId;
    const reserveATION_JSON_DATA = JSON.stringify(reserveationData);
    console.log("json:" + reserveATION_JSON_DATA);

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/reserve/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: reserveATION_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(data => {
        if(data.result)
        {
            alert('予約が完了しました');
            location = LOCATION_URL + '/html/reserve_success.html?reservation_id=' + data.reservation_id;
        }
        else
        {
            alert('予約に失敗しました');
            errorMessageArea.innerHTML = data.message;
        }
    })
}

function getData()
{
    
    // 予約ボタンを初期化
    document.getElementById('classroom-box').innerHTML = '';

    const errorMessageArea = document.getElementById('errorMessageArea');
    // エラーメッセージの初期化
    errorMessageArea.innerHTML = '';

    //予約時間を一時保存する変数
    let reserveationData = {};
    //予約する日にちを取得
    const reserveATION_DATE = document.getElementById('reserveation-date').value;
    console.log(reserveATION_DATE);
    //予約日 + 空白 + 予約時間で結合する
    reserveationData["start_time"] = reserveATION_DATE + ' ' + document.getElementById('start-time').value + ':00';
    reserveationData["end_time"] = reserveATION_DATE + ' ' +document.getElementById('end-time').value + ':00';
    //予約日時をjson形式にする
    const reserveATION_JSON_DATA = JSON.stringify(reserveationData);

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/classroom/get', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: reserveATION_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(data => {
        if(data.result) {
            let classrooms = data.classrooms;
            console.log(classrooms);// 取得したデータをコンソールに表示します
            //ボタンの設置
            for (var i = 0; i < classrooms.length; i++) {
                let button = document.createElement("input"); // ボタン要素を作成
                button.setAttribute('type', 'button');// ボタンの値を設定
                button.setAttribute('value', classrooms[i].classroom_name);// ボタンの値を設定
                button.className = 'classroom-button btn_08';
                // クリックイベントを追加
                (function(index) {
                    button.addEventListener("click", function() {
                        reserveationApplication(classrooms[index].classroom_id, reserveationData);
                    });
                })(i);// 関数スコープ内でiの値を保存する
                document.getElementById('classroom-box').appendChild(button); // ボタンをHTMLのbody要素に追加
            }
        } else {
            errorMessageArea.innerHTML = data.message;
        }
    })
    .catch(error => {
        console.log('エラーが発生しました:', error); // エラーが発生した場合にエラーメッセージをコンソールに表示します
    });
}