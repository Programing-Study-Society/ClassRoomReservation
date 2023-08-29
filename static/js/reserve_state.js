// 予約を削除する関数(管理者側)(/reserve/delete)(全ての予約の取得する関数より、予約取消ボタンに紐づけられる)
function reserveDeleteAdmin(reservationId, reservationDateAndTime, userName)
{

    if (!confirm(reservationDateAndTime + '　' + userName + 'の予約を削除しますか？\n' + '※予約が削除された旨のメールが予約者に自動送信されます。'))
    {
        alert('削除をキャンセルしました');
        return 0;
    }

    // //教室idを含めたjsonを作成
    const RESERVATION_ID_JSON_DATA = JSON.stringify(reservationId);

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/reserve/delete', {
        method: 'POST',
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
            showMessageArea(resData['message'], 'black') // メッセージをメッセージエリアに表示
        }
        else {showMessageArea(resData['message'], 'red')} // エラーメッセージをメッセージエリアに表示
    }).catch((err) => console.log(err)); // エラーキャッチ
}

// 全ての予約の取得する関数(/reserve/get/full)(現在の予約状況を確認・更新するときに実行される)
function reserveGetFull()
{
    fetch(LOCATION_URL + '/reserve/get/full')
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']){ // 成功時
            if(resData['data'].length <= 0) // dataが0件なら
            {
                // 予約が無いことを表示
                reservedClassroomPrintArea.innerHTML = 'なし';
            }
            else // 予約が存在するなら
            {
                resData['data'].forEach((ele) => {
                    const reservationDateAndTime = timeFormating(ele['start-date'], ele['end-date']);

                    const $tableBody = document.getElementById('reservation-list-box');
                    const $newRow = document.getElementById('reservation-list-box-row').cloneNode(true);

                    // 各セルにデータを設定して <td> 要素を作成し、<tr> に追加
                    const $cell1 = document.createElement('td');
                    $cell1.textContent = reservationDateAndTime;
                    $newRow.appendChild($cell1);

                    const $cell2 = document.createElement('td');
                    $cell2.textContent = ele['classroom-name'];
                    $newRow.appendChild($cell2);

                    const $cell3 = document.createElement('td');
                    $cell3.textContent = ele['user-name'];
                    $newRow.appendChild($cell3);

                    const $cell4 = document.createElement('td');
                    $cell4.textContent = ele['user-email'];
                    $newRow.appendChild($cell4);
        
                    // 新しいボタン要素を作成
                    const $cancelButton = document.createElement('button');
                    $cancelButton.className = 'reserve-delete';
                    $cancelButton.textContent = '取消';
                    $cancelButton.addEventListener("click", function() {
                        reserveDeleteAdmin(ele['reservation-id'], reservationDateAndTime + '　' + ele['classroom-name'], ele['user-name']);
                    });
                    // // ボタンをセルに追加
                    const $cell5 = document.createElement('td');
                    $cell5.appendChild($cancelButton);
                    $newRow.appendChild($cell5);
    
                    // セルを表に挿入
                    $tableBody.appendChild($newRow);
                });
            }
        }
        else
        {

        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// reserve_state.htmlページを開いた瞬間に実行される部分
reserveGetFull();