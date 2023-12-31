let authorityList = [];

// 現在ログインしているユーザーが、ユーザー追加で付与できる権限を取得する関数(/user/get-authority)
function getUserAuthority(callback)
{
    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/user/get-authority')
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) // 成功時
        {
            // select要素を取得
            const $select = document.getElementById('add-authority');

            // 選択肢を追加
            resData['data'].forEach(ele => {
                const $option = document.createElement("option");
                const authorityName = ele['name'];
                $option.text = authorityName;
                $option.value = authorityName;
                authorityList.push(authorityName);
                $select.appendChild($option);
            });

            // 選択肢の初期値を選択肢の一番最後の物にする
            $select.options[resData['data'].length - 1].selected = true;

            callback(); // 現在登録されているユーザー情報の取得
        }
        else // 失敗時
        {
            // エラーを表示
            const $userAddDetails = document.getElementById('user-add-details');
            $userAddDetails.style.display = "none";

            const $noGetUserAuthority = document.getElementById('no-get-user-authority');
            $noGetUserAuthority.innerHTML = resData['message'];
            $noGetUserAuthority.style.color = 'red';
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// ユーザーを削除する関数(管理者)(/user/delete)(ユーザーの取得を行う関数より、削除ボタンに紐づけられる)
function userDeleteAdmin(email, userName)
{
    if (!confirm(userName + 'を削除しますか？\n※削除されたユーザーはサイトにアクセスできなくなり、予約状況も削除されます。'))
    {
        return;
    }

    const EMAIL_JSON_DATA = JSON.stringify({'email' : email});

    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/user/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: EMAIL_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) // ユーザー削除成功時
        {
            location.reload(); // ページをリロード
        }
        else {alert('ユーザーを削除できませんでした\n' + resData['message']);} // エラーメッセージをメッセージエリアに表示
    }).catch((err) => console.log(err)); // エラーキャッチ
}

// ユーザーの取得を行う関数(/user/get)(現在のユーザーを確認・更新するときに実行される)
function userGet()
{
    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/user/get')
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']){ // 成功時
            if(resData['data'] <= 0) // dataが0件なら(管理者が居なくなるため、恐らくあり得ない)
            {
                // ユーザーが登録されていないことを表示
                const $noUserSentence = document.getElementById('no-user-sentence');
                $noUserSentence.innerHTML = 'ユーザーなし';
                $noUserSentence.style.color = 'black';
            }
            else // ユーザーが存在するなら
            {
                // user-list-box(tbodyタグ)を取得
                const $userListBox = document.getElementById('user-list-box');

                resData['data'].forEach(ele => {
                    // trタグのuser-list-box-rowを作成
                    const $newRow = document.createElement('tr');
                    $newRow.className = 'user-list-box-row';

                    // 各セルにデータを設定して <td> 要素を作成し、<tr> に追加
                    const $cell1 = document.createElement('td');
                    $cell1.textContent = ele['approved-user-name'];
                    $newRow.appendChild($cell1);

                    const $cell2 = document.createElement('td');
                    $cell2.textContent = ele['approved-email'];
                    $newRow.appendChild($cell2);

                    const $cell3 = document.createElement('td');
                    $cell3.textContent = ele['user-state'];
                    $newRow.appendChild($cell3);

                    if(authorityList.includes(ele['user-state']))
                    {
                        // 新しいボタン要素を作成
                        const $cancelButton = document.createElement('button');
                        $cancelButton.className = 'user-delete';
                        $cancelButton.textContent = '削除';
                        $cancelButton.addEventListener("click", function() {
                            userDeleteAdmin(ele['approved-email'], ele['approved-user-name']);
                        });
                        // // ボタンをセルに追加
                        const $cell4 = document.createElement('td');
                        $cell4.appendChild($cancelButton);
                        $newRow.appendChild($cell4);
                    }
                    else
                    {
                        const $cell4 = document.createElement('td');
                        $newRow.appendChild($cell4);
                    }

                    // セルを表に挿入
                    $userListBox.appendChild($newRow);
                });
            }
        }
        else // 失敗時
        {
            // エラーを表示
            const $noUserSentence = document.getElementById('no-user-sentence');
            $noUserSentence.innerHTML = resData['message'];
            $noUserSentence.style.color = 'red';
        }
    }).catch((err) => console.log(err)); // エラーキャッチ
}



// ユーザーを追加する関数
function userAdd()
{
    const addUserNameValue = document.getElementById('add-user-name').value;
    const addEmailValue = document.getElementById('add-email').value;
    const authorityValue = document.getElementById('add-authority').value;

    // ユーザー情報を一時保存する変数
    let userData = {};
    userData['user-name'] = addUserNameValue;
    userData['email'] = addEmailValue;
    userData['user-state'] = authorityValue;

    // ユーザー情報をjson形式にする
    const user_JSON_DATA = JSON.stringify(userData);
    // データを取得するためのAPIエンドポイントにリクエストを送信します
    fetch(LOCATION_URL + '/user/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: user_JSON_DATA
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換します
    .then(resData => {
        if(resData['result']) { // 成功時
            location.reload(); // ページをリロード
        }
        else {alert('ユーザーを追加できませんでした\n' + resData['message']);} // エラーメッセージをメッセージエリアに表示
    }).catch((err) => console.log(err)); // エラーキャッチ
}



//  user_list.htmlページを開いた瞬間に実行される部分
getUserAuthority(userGet); // ログインしているユーザーの権限を取得