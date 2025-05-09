/**
 * 모바일 화면에서 로그인 버튼을 쉽게 접근할 수 있도록 
 * 플로팅 로그인 버튼을 추가하는 스크립트
 */
document.addEventListener('DOMContentLoaded', function() {
    // 현재 페이지가 로그인 페이지인지 확인
    const isLoginPage = window.location.pathname.includes('login.html');
    
    // 이미 로그인되어 있는지 확인
    fetch('/api/check-auth')
        .then(response => response.json())
        .then(data => {
            const isLoggedIn = data.authenticated || data.is_authenticated;
            
            // 로그인 페이지가 아니고, 로그인되지 않은 경우에만 버튼 추가
            if (!isLoginPage && !isLoggedIn && window.innerWidth <= 768) {
                addLoginButton();
            }
        })
        .catch(error => {
            console.error('인증 확인 오류:', error);
            // 오류 발생 시, 로그인 페이지가 아닌 경우 버튼 추가
            if (!isLoginPage && window.innerWidth <= 768) {
                addLoginButton();
            }
        });
});

// 플로팅 로그인 버튼 추가 함수
function addLoginButton() {
    // 이미 있는지 확인
    if (document.querySelector('.floating-login-btn')) {
        return;
    }
    
    // 버튼 생성
    const loginBtn = document.createElement('a');
    loginBtn.href = 'login.html';
    loginBtn.className = 'floating-login-btn';
    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i>';
    loginBtn.style.position = 'fixed';
    loginBtn.style.bottom = '20px';
    loginBtn.style.right = '20px';
    loginBtn.style.backgroundColor = '#4CAF50';
    loginBtn.style.color = 'white';
    loginBtn.style.borderRadius = '50%';
    loginBtn.style.width = '60px';
    loginBtn.style.height = '60px';
    loginBtn.style.display = 'flex';
    loginBtn.style.alignItems = 'center';
    loginBtn.style.justifyContent = 'center';
    loginBtn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    loginBtn.style.zIndex = '9999';
    loginBtn.style.fontSize = '24px';
    
    // 문서에 추가
    document.body.appendChild(loginBtn);
} 