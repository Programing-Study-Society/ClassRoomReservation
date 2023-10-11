const modal = document.getElementById('js-modal'),
              open = document.getElementById('js-modal-open'),
              close = document.getElementById('js-modal-close');
    
            function modalOpen() {
            modal.classList.add('is-active');
            }
            open.addEventListener('click', modalOpen);
    
            function modalClose() {
            modal.classList.remove('is-active');
            }
            close.addEventListener('click', modalClose);
    
            function modalOut(e) {
            if (e.target == modal) {
                    modal.classList.remove('is-active');
                }
            }
                
            addEventListener('click', modalOut);

            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('js-modal').style.display = 'flex';
            });