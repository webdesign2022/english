document.addEventListener('DOMContentLoaded', function() {
    // ------------------------------------------
    // 1. 導航欄 active 狀態處理
    // ------------------------------------------
    const currentPath = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-links a:not(.inquiry-btn)');

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        // 檢查連結是否匹配當前頁面檔案名稱
        if (linkPath === currentPath || 
            (currentPath === '' && linkPath === 'index.html')) {
            link.classList.add('active');
        }
    });

    // ------------------------------------------
    // 2. 詢問單表單提交處理 (僅在 inquiry.html 執行)
    // ------------------------------------------
    const inquiryForm = document.getElementById('inquiryForm');
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function(event) {
            event.preventDefault(); 
            
            const form = event.target;
            const formData = new FormData(form);
            const messageDiv = document.getElementById('form-message');

            messageDiv.style.display = 'block';
            messageDiv.style.backgroundColor = '#fff3cd'; 
            messageDiv.style.color = '#856404';
            messageDiv.innerHTML = '正在發送中，請稍候...';

            // 實際提交到後端 (例如 send_mail.php)
            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                // 這裡假設後端會返回一個 JSON 狀態
                // 實際開發中需要確保後端腳本（如 send_mail.php）能正確處理並返回狀態碼
                if (response.ok) {
                    return response.text(); // 或 response.json()
                }
                throw new Error('Server returned error status.');
            })
            .then(result => {
                // 成功返回
                messageDiv.style.backgroundColor = '#d4edda'; 
                messageDiv.style.color = '#155724';
                messageDiv.innerHTML = '✅ 感謝您的詢問！您的訊息已成功發送。';
                form.reset(); 
            })
            .catch(error => {
                // 失敗處理
                console.error('Submission Error:', error);
                messageDiv.style.backgroundColor = '#f8d7da'; 
                messageDiv.style.color = '#721c24';
                messageDiv.innerHTML = '❌ 抱歉，發送失敗！請檢查網路或直接發送郵件到您的信箱。';
            });
        });
    }

    // ------------------------------------------
    // 3. 預留：圖片燈箱效果 (僅為未來擴充示範)
    // ------------------------------------------
    // const photoGrid = document.querySelector('.photo-grid');
    // if (photoGrid) {
    //     photoGrid.addEventListener('click', function(e) {
    //         if (e.target.tagName === 'IMG') {
    //             // 實作燈箱 (Lightbox) 邏輯
    //             console.log('Open Lightbox for:', e.target.alt);
    //         }
    //     });
    // }
});