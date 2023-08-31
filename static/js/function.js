const LOCATION_URL = ''; // 本番(APIとの結合時)にtestApiを消すのを忘れずに

// 開始日時、終了日時、教室を分かりやすい形に変換する関数
function timeFormating(startDate, endDate)
{
    const days = '日月火水木金土'; // 曜日表示用の文字列
    startDate = startDate.replace(/-/g,'/'); // -を/に変更
    const day = new Date(startDate); //Date型に変換
    const reservationDateAndTime = 
        startDate.slice( 0, 10 ) + // yyyy-MM-dd
        '(' + days[day.getDay()] + ') ' + // 曜日(day)
        startDate.slice( 11, 16 ) + // HH:mm
        '  ～  ' + endDate.slice( 11, 16 ) // HH:mm
    
    return reservationDateAndTime;
}