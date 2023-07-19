# 教室予約システム
## APIリスト
### /reserve/register

<sub> 
予約をするエンドポイントです。

ここにjsonを以下の形式でPOSTすると予約をし、結果を返します。

```
{
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: {
        'start_time':'<開始時間>',
        'end_time':'<終了時間>',
        'classroom_id':'<部屋ID>'
    }
}
```

</sub>

### /reserve/get/full

<sub>

全ての予約状況を返却するエンドポイントです。

GETで全て返します

</sub>

### /reserve/get/id

<sub>

指定したIDの予約状況を返却するエンドポイントです。

ここにjsonを以下の形式でPOSTすると予約状況を返却します。

```
{
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: {
        'reservation_id':'<予約ID>',
    }
}
```

</sub>

### /reserve/get/date

<sub>

指定した日付の予約状況を返却するエンドポイントです。

ここにjsonを以下の形式でPOSTすると予約状況を返却します。

```
{
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: {
        'date':'<日付(format : yyyy-mm-dd)>',
    }
}
```

</sub>