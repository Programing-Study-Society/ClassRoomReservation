fetch('/user/current-user')
.then(response => {
    if(response['status'] !== 200) {
        console.log('エラー : ');
        location.href = '/';
    }
})