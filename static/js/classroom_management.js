// 入力欄を追加する関数
function addInputField()
{
    const $addformParent = document.getElementById('addform-parent');
    const $addformChild = document.getElementById("addform-child-template").content.cloneNode(true);
    $addformParent.appendChild($addformChild);
}

// form削除機能
function formDeleteButton(button) {
    // ボタンの親要素を取得し、削除します。
    let parentDiv = button.parentNode;
    parentDiv.parentNode.removeChild(parentDiv);
}

// 予約可能教室一覧の各要素を削除する関数
function deleteTableRow() {
    // 指定したidの要素を取得
    var rows = document.getElementsByClassName('classroom-list-box-row');

    // 各行を順番に削除
    const len = rows.length;
    for (let i = 0; i < len; i++) {
        rows[0].remove();
    }
}



// 教室を削除する関数(管理者側)(/classroom/delete)(教室の全ての取得をする関数より、削除ボタンに紐づけられる)
function classroomDeleteAdmin(classroomId, reservationDateAndTime, reservationStatus)
{
    // confirmで表示するメッセージを格納する変数
    let confirmMessage = reservationDateAndTime + '　' +'の予約可能教室を削除しますか？';
    if(reservationStatus == 1) confirmMessage += '\n※予約が削除された旨のメールが予約者に自動送信されます。';
    if(reservationStatus == -1) confirmMessage += '\n※予約状況が取得できていません。\n※予約者がいる場合、予約が削除された旨のメールが予約者に自動送信されます。';

    if (!confirm(confirmMessage))
    {
        return;
    }

    const CLASSROOM_ID_JSON_DATA = JSON.stringify({'classroom-id':classroomId});

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/classroom/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: CLASSROOM_ID_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) // 予約削除成功時
        {
            location.reload(); // ページをリロード
        }
        else {alert('予約を削除できませんでした\n' + resData['message']);} // エラーメッセージをメッセージエリアに表示
    }).catch((err) => console.log(err)); // エラーキャッチ
}

// 教室の全ての取得をする関数(/classroom/get/full)(/reserve/get/classroom-id)(現在の予約可能な教室を確認・更新するときに実行される)
function classroomGetFull()
{
    deleteTableRow(); // 予約可能教室一覧の要素を初期化

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/classroom/get/full')
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']){ // 成功時
            const $noClassroomSentence = document.getElementById('no-classroom-sentence');
            if(resData['data'] <= 0) // dataが0件なら
            {
                // 予約可能教室が無いことを表示
                $noClassroomSentence.innerHTML = '予約可能教室なし';
                $noClassroomSentence.style.color = 'black';
            }
            else // 予約可能教室が存在するなら
            {
                $noClassroomSentence.innerHTML = '';
                $noClassroomSentence.style.color = 'black';

                // classroom-list-box(tbodyタグ)を取得
                const $tableBody = document.getElementById('classroom-list-box');

                resData['data'].forEach(ele => {

                    // 予約可能日時を見やすい形に加工する
                    const reservationDateAndTime = timeFormating(ele['reservable-start-date'], ele['reservable-end-date']);

                    // trタグのclassroom-list-box-rowを作成
                    const $newRow = document.createElement('tr');
                    $newRow.className = 'classroom-list-box-row';

                    // 各セルにデータを設定して <td> 要素を作成し、<tr> に追加
                    const $cell1 = document.createElement('td');
                    $cell1.textContent = reservationDateAndTime;
                    $newRow.appendChild($cell1);

                    const $cell2 = document.createElement('td');
                    $cell2.textContent = ele['classroom-name'];
                    $newRow.appendChild($cell2);

                    const $cell3 = document.createElement('td');
                    $cell3.textContent = ele['is_reserved'] ? 'あり' : 'なし';
                    $cell3.style.color = ele['is_reserved'] ? 'red' : 'black';
                    $newRow.appendChild($cell3);

                    // 新しいボタン要素を作成
                    const $cancelButton = document.createElement('button');
                    $cancelButton.className = 'classroom-delete';
                    $cancelButton.textContent = '削除';
                    $cancelButton.addEventListener("click", function() {
                        classroomDeleteAdmin(ele['classroom-id'], reservationDateAndTime + '　' + ele['classroom-name'], ele['is_reserved']);
                    });
                    // // ボタンをセルに追加
                    const $cell4 = document.createElement('td');
                    $cell4.appendChild($cancelButton);
                    $newRow.appendChild($cell4);

                    // セルを表に挿入
                    $tableBody.appendChild($newRow);
                });
            }
        }
        else
        {
            // エラーを表示
            const $noClassroomSentence = document.getElementById('no-classroom-sentence');
            $noClassroomSentence.innerHTML = resData['message'];
            $noClassroomSentence.style.color = 'red';
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// 予約可能教室を追加する関数(/classroom/add)
function classroomAdd()
{
    if (!confirm('予約可能な教室を送信しますか？'))
    {
        return;
    }

    // メッセージエリア(主にエラーメッセージを表示するエリア)を取得
    const messageAreaSentence = document.getElementById('message-area-sentence');
    messageAreaSentence.innerHTML = '';

    console.log('classroomAdd run');
    // 追加分の予約可能教室を取得
    // .addform-form要素を取得
    const addformElements = document.querySelectorAll('.addform-child');
    console.log(addformElements);

    // 予約可能教室のデータを格納する配列
    const roomDatas = [];

    // 各 .addform 要素に対してループ処理を行う
    addformElements.forEach(addform => {
        // 各要素から値を取得
        const dateValue = addform.querySelector('.addform-today').value;
        const startTimeValue = addform.querySelector('.addform-start-time').value;
        const endTimeValue = addform.querySelector('.addform-end-time').value;
        const roomNameValue = addform.querySelector('.addform-roomname').value;

        //予約時間を一時保存する変数
        let roomData = {};
        //日付 + 空白 + 予約時間で結合する
        roomData['start-date'] = dateValue + ' ' + startTimeValue + ':00';
        roomData['end-date'] = dateValue + ' ' + endTimeValue + ':00';
        roomData['classroom-name'] = roomNameValue;
        roomDatas.push(roomData);
    });

    // 送信するデータが0件のときの処理
    if(roomDatas.length <= 0)
    {
        messageAreaSentence.innerHTML = '送信するデータがありません';
        return;
    }


    // 追加分の予約可能教室をjson形式にする
    const room_JSON_DATA = JSON.stringify(roomDatas);
    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/classroom/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: room_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {

        if(resData['result']) { // 成功時
            let isAllOk = true; // 追加が失敗した件数を格納する変数
            // 予約可能な教室追加欄の一番上の要素をそれぞれ取得
            const $date = addformElements[0].querySelector('.addform-today');
            const $startTime = addformElements[0].querySelector('.addform-start-time');
            const $endTime = addformElements[0].querySelector('.addform-end-time');
            const $roomName = addformElements[0].querySelector('.addform-roomname');

            resData['classroom'].forEach((ele, index) =>{

                if(ele['result']) // 予約可能教室の追加が成功していたら
                {
                    if(index == 0) // 予約可能教室の追加の一番上(削除ボタン無しver)の処理
                    {
                        $date.value = '';
                        $startTime.value = '';
                        $endTime.value = '';
                        $roomName.value = '';
                    }
                    else
                    {
                        // 追加が成功した入力欄を削除する
                        addformElements[index].remove();
                    }
                }
                else // 予約可能教室の追加が失敗していたら
                {
                    if(isAllOk && index != 0) // isAllOkがtrue → 予約可能な教室追加欄の一番上が空なので、そこに値追加
                    {
                        $date.value = addformElements[index].querySelector('.addform-today').value;
                        $startTime.value = addformElements[index].querySelector('.addform-start-time').value;
                        $endTime.value = addformElements[index].querySelector('.addform-end-time').value;
                        $roomName.value = addformElements[index].querySelector('.addform-roomname').value;
                        addformElements[index].remove();
                    }
                    // 追加が失敗したメッセージを表示する
                    const reservationDateAndTime = timeFormating(ele['data']['start-date'], ele['data']['end-date']);
                    messageAreaSentence.innerHTML += reservationDateAndTime + '　' + ele['data']['classroom-name'] + 'の登録が失敗しました：' + ele['message'] + '<br>';

                    isAllOk = false; // 失敗を記録する
                }
            });

            classroomGetFull() // 現在の予約可能教室を更新する

        }
        else // 失敗時(全ての教室の追加が失敗時)
        {
            messageAreaSentence.innerHTML = resData['message'] + '<br>';

            resData['errors'].forEach(ele => {
                const reservationDateAndTime = timeFormating(ele['data']['start-date'], ele['data']['end-date']);
                messageAreaSentence.innerHTML += reservationDateAndTime + '　' + ele['data']['classroom-name'] + 'の登録が失敗しました：' + ele['message'] + '<br>';
            });
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}


// classroom_management.htmlページを開いた瞬間に実行される部分
classroomGetFull();