fetch('/user/get')
.then(response => {
    if(response['status'] !== 200) {
        console.log('エラー : ');
        location.href = '/';
    }
})