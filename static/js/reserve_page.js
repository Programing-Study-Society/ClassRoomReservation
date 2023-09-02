// メッセージをメッセージエリアに表示する関数
function showMessageArea(message, color)
{
    const messageAreaSentence = document.getElementById('message-area-sentence');
    messageAreaSentence.innerHTML = message;
    messageAreaSentence.style.color = color;
}

// 日時を、画面サイズによって自動で改行される文章に成形させる関数
function createFormattedMessage(startDate, endDate, classroomName)
{
    const days = '日月火水木金土'; // 曜日表示用の文字列

    // const data = resData["data"]; // json内のdataを取り出してdataに格納
    const newStartDate = startDate.replace(/-/g,'/'); // -を/に変更
    const day = new Date(newStartDate); //Date型に変換

    const date = newStartDate.slice( 0, 10 ) + '(' + days[day.getDay()] + ') ' // yyyy-MM-dd + 曜日(day)
    const time = newStartDate.slice( 11, 16 ) + '  ～  ' + endDate.slice( 11, 16 ); // HH:mm + ～ + HH:mm
    const room = classroomName; // 教室

    console.log(date);
    console.log(time);
    console.log(room);
    
    return `${date}<span class="break"></span>${time}<br>${room}`;
}



// 予約を削除する関数(ユーザー側)(/reserve/delete)(ユーザー個人の予約を取得する関数より、予約削除ボタンに紐づけられる)
function reserveDeleteUser(reservationId, reservationDateAndTimeConfirm, reservationDateAndTimeMessage)
{

    if (!confirm(reservationDateAndTimeConfirm + 'の予約を削除しますか？'))
    {
        return;
    }

    // //教室idを含めたjsonを作成
    const RESERVATION_ID_JSON_DATA = JSON.stringify({'reservation-id' : reservationId});

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/reserve/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: RESERVATION_ID_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) // 予約削除成功時
        {
            reserveGetUser() // 予約済み教室を更新
            showMessageArea(reservationDateAndTimeMessage + 'の予約を削除しました', 'black'); // メッセージを表示
        }
        else {showMessageArea(resData['message'], 'red')} // エラーメッセージをメッセージエリアに表示
    }).catch((err) => console.log(err)); // エラーキャッチ
}

// ユーザー個人の予約を取得する関数(/reserve/get/user)(現在の予約状況を確認・更新するときに実行される)
function reserveGetUser()
{
    fetch(LOCATION_URL + '/reserve/get/user')
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {

        // reservedClassroomPrintAreaの取得と初期化
        const reservedClassroomPrintArea = document.getElementById('reserved-classroom-print-area');
        reservedClassroomPrintArea.innerHTML = '';

        if(resData['result']) { // 成功時
            if(resData['data'].length <= 0) // dataが0件なら
            {
                // 予約が無いことを表示
                reservedClassroomPrintArea.innerHTML = 'なし';
            }
            else // 予約が存在するなら
            {
                // 予約済み教室(data)の数だけ繰り返して予約済み教室を表示する
                resData['data'].forEach((ele) => {

                    // 予約されている日時をわかりやすい形に加工
                    const reservationDateAndTimeConfirm = timeFormating(ele['start-date'], ele['end-date']) + '　' + ele['classroom-name'];
                    const reservationDateAndTimeMessage = createFormattedMessage(ele['start-date'], ele['end-date'], ele['classroom-name']);
                    // messageに挿入
                    const message = document.createTextNode(reservationDateAndTimeConfirm);

                    // 予約削除ボタンの作成
                    const button = document.createElement("button"); // 予約削除ボタン要素を作成
                    button.classList.add("fas", "fa-trash"); // ボタンの値(ゴミ箱マーク)を設定
                    /*button.className = ''; // ボタンのクラスを設定(現状クラス無し) */
                    // クリックイベントを追加
                    button.addEventListener("click", function() {
                        reserveDeleteUser(ele['reservation-id'], reservationDateAndTimeConfirm, reservationDateAndTimeMessage);
                    });

                    reserveList = document.createElement('li'); // li要素を作成
                    reserveList.appendChild(message); // li要素にmessageを入れる
                    reserveList.appendChild(button); // li要素にbuttonを入れる
                    reservedClassroomPrintArea.appendChild(reserveList); // li要素をHTMLのbody要素に追加
                });
            }
        }
        else // 失敗時
        {
            // エラーメッセージを表示
            reservedClassroomPrintArea.innerHTML = resData['message'];
            reservedClassroomPrintArea.style.color = 'red';
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// 教室の予約機能
// 教室ボタンに付与する関数(/reserve/add)(日時を送り、空き教室を検索する関数より、クリックイベントの追加で紐づけられる)
function reserveationApplication(classroomId, classroomName, reserveationData)
{
    const alertMessage = timeFormating(reserveationData['start-date'], reserveationData['end-date']) + '　' + classroomName;
    if (!confirm(alertMessage + 'で予約を確定しますか？'))
    {
        return;
    }

    //教室idを含めたjsonを作成
    reserveationData["classroom-id"] = classroomId;
    const reserveATION_JSON_DATA = JSON.stringify(reserveationData);
    // console.log("json:" + reserveATION_JSON_DATA);

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/reserve/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: reserveATION_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result'])
        {
            const data = resData["data"]; // json内のdataを取り出してdataに格納

            // 予約されている日時をわかりやすい形に加工
            const message = createFormattedMessage(data['start-date'], data['end-date'], data['classroom-name']);
            showMessageArea(message + 'を予約しました', 'black'); // メッセージを表示

            reserveGetUser(); // 予約済み教室を更新
        }
        else
        {
            // エラーメッセージを表示
            showMessageArea(resData['message'], 'red');
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}

// 日時を送り、空き教室を検索する関数(/classroom/get/date)(reserve_page.htmlで検索ボタンを押したときに実行される)
function getData()
{
    
    // 予約ボタンの取得・初期化
    const classroomBox =  document.getElementById('classroom-box');
    classroomBox.innerHTML = '';

    // 予約時間を一時保存する変数
    let reserveationData = {};
    // 予約する日にちを取得
    const reserveATION_DATE = document.getElementById('reserveation-date').value;
    // console.log(reserveATION_DATE);
    // 予約日 + 空白 + 予約時間で結合する
    reserveationData['start-date'] = reserveATION_DATE + ' ' + document.getElementById('start-time').value + ':00';
    reserveationData['end-date'] = reserveATION_DATE + ' ' +document.getElementById('end-time').value + ':00';
    // 予約日時をjson形式にする
    const reserveATION_JSON_DATA = JSON.stringify(reserveationData);

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/classroom/get/date', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: reserveATION_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) {
            // let classrooms = resData['data'];
            // console.log(classrooms);

            if(resData['data'].length <= 0) // 予約できる教室が0なら
            {
                
            }

            // ボタンの設置
            resData['data'].forEach((ele) => {
                const button = document.createElement("button"); // ボタン要素を作成
                button.textContent = ele['classroom-name']; // ボタンの値を設定
                button.className = 'classroom-button btn_08'; // ボタンのクラスを設定
                // クリックイベントを追加
                button.addEventListener("click", function() {
                        reserveationApplication(ele['classroom-id'], ele['classroom-name'], reserveationData);
                });
                classroomBox.appendChild(button); // ボタンをHTMLのbody要素に追加
            })
        } else {
            // エラーメッセージを表示
            showMessageArea(resData['message'], 'red');
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// reserve_page.htmlページを開いた瞬間に実行される部分
reserveGetUser();