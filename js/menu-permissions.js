/**
 * 메뉴 권한 관리 JavaScript
 * 모든 HTML 페이지에 포함되어 사용자 역할에 따라 메뉴 항목을 표시하거나 숨깁니다.
 */

// 전역 변수
let userRole = null;
let menuPermissions = [];

// 사용자 로그인 상태와 권한에 따라 메뉴 접근 제어
document.addEventListener('DOMContentLoaded', function() {
    // 인증 상태 확인
    fetch('/api/check-auth')
        .then(response => response.json())
        .then(data => {
            // 인증되지 않은 경우 로그인 링크 추가
            if (!data.authenticated && !data.is_authenticated) {
                addLoginMenuItem();
            }
            
            // 권한 설정 적용
            const currentMenuPermissions = (data.menu_permissions && data.user && data.menu_permissions[data.user.role]) || [];
            applyMenuPermissions(currentMenuPermissions);
        })
        .catch(error => {
            console.error('인증 확인 오류:', error);
            applyDefaultMenuPermissions();
        });
    
    // 오류 발생 시 기본 권한 적용
    setTimeout(() => {
        applyDefaultMenuPermissions();
        addLoginMenuItem();
    }, 3000);
});

// 메뉴 권한 적용 함수
function applyMenuPermissions(menuPermissions) {
    // 네비게이션 메뉴 선택
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    // 각 메뉴 항목 순회
    const menuItems = navMenu.querySelectorAll('li');
    menuItems.forEach(menuItem => {
        // 인증 상태와 사용자 정보 메뉴는 제외
        if (menuItem.id === 'auth-status' || menuItem.id === 'user-info') return;
        
        // 링크 선택
        const link = menuItem.querySelector('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        
        // 메뉴 ID 추출
        const menuId = getMenuIdFromHref(href);
        
        // 로그인 메뉴는 항상 표시
        if (menuId === 'login') {
            menuItem.style.display = '';
            return;
        }
        
        // 권한에 없는 메뉴 숨기기
        if (menuId && !menuPermissions.includes(menuId)) {
            menuItem.style.display = 'none';
        } else {
            menuItem.style.display = '';
        }
    });
}

// 기본 메뉴 권한 적용 함수
function applyDefaultMenuPermissions() {
    // 네비게이션 메뉴 선택
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    // 기본적으로 접근 가능한 메뉴 정의
    const defaultMenus = ['about', 'join', 'inquiry'];
    
    // 각 메뉴 항목 순회
    const menuItems = navMenu.querySelectorAll('li');
    menuItems.forEach(menuItem => {
        // 인증 상태와 사용자 정보 메뉴는 제외
        if (menuItem.id === 'auth-status' || menuItem.id === 'user-info') return;
        
        // 링크 선택
        const link = menuItem.querySelector('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        
        // 메뉴 ID 추출
        const menuId = getMenuIdFromHref(href);
        
        // 로그인 메뉴는 항상 표시
        if (menuId === 'login') {
            menuItem.style.display = '';
            return;
        }
        
        // 기본 메뉴 이외의 메뉴 숨기기
        if (menuId && !defaultMenus.includes(menuId) && menuId !== 'login') {
            menuItem.style.display = 'none';
        } else {
            menuItem.style.display = '';
        }
    });
}

// URL에서 메뉴 ID 추출 함수
function getMenuIdFromHref(href) {
    if (!href) return null;
    // 절대 경로에서 상대 경로로 변환
    let path = href.replace(/^https?:\/\/[^\/]+/, '');
    // 해시 제거
    path = path.split('#')[0];
    // 마지막 / 제거
    if (path.endsWith('/')) path = path.slice(0, -1);
    // 소문자 변환
    path = path.toLowerCase();

    if (path === '/' || path === '' || path === 'index.html') return 'about';
    if (path === 'index.html' || path === '/index.html') return 'about';
    if (path === 'join.html' || path === '/join.html') return 'join';
    if (path === 'performances.html' || path === '/performances.html') return 'performances';
    if (path === 'music.html' || path === '/music.html') return 'music';
    if (path === 'scores.html' || path === '/scores.html') return 'scores';
    if (path === 'board.html' || path === '/board.html') return 'board';
    if (path === 'schedule.html' || path === '/schedule.html') return 'schedule';
    if (path === 'inquiry.html' || path === '/inquiry.html') return 'inquiry';
    if (path === 'sponsor.html' || path === '/sponsor.html') return 'sponsor';
    if (path === 'youtube.html' || path === '/youtube.html') return 'youtube';
    if (path.includes('instagram.com')) return 'instagram';
    if (path === 'admin.html' || path === '/admin.html') return 'admin';
    if (path === 'login.html' || path === '/login.html') return 'login';
    // index.html#about 등 해시 포함도 'about' 처리
    if (href.includes('index.html#about') || href === '#about') return 'about';
    return null;
}

// 현재 페이지의 접근 권한 확인
function checkCurrentPagePermission() {
    fetch('/api/check-auth')
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated && !data.is_authenticated) {
                if (!isPublicPage()) {
                    window.location.href = '/login.html';
                }
                return;
            }
            
            const menuPermissions = data.menu_permissions || [];
            const pageName = getPageNameFromUrl(window.location.pathname);
            
            if (pageName && pageName !== 'login' && !menuPermissions.includes(pageName) && !isPublicPage()) {
                window.location.href = '/index.html';
            }
        })
        .catch(error => {
            console.error('페이지 권한 확인 오류:', error);
        });
}

// 로그인 메뉴 항목 추가 함수
function addLoginMenuItem() {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;

    // 이미 로그인 메뉴가 있는지 확인
    const existingLoginItem = Array.from(navMenu.querySelectorAll('li a')).find(a => 
        a.getAttribute('href') === 'login.html' || a.getAttribute('href') === '/login.html'
    );
    
    if (existingLoginItem) return; // 이미 있으면 추가하지 않음
    
    // 로그인 메뉴 항목 생성
    const loginItem = document.createElement('li');
    const loginLink = document.createElement('a');
    loginLink.href = 'login.html';
    loginLink.textContent = '로그인';
    loginItem.appendChild(loginLink);
    
    // 메뉴 끝에 추가
    navMenu.appendChild(loginItem);
}

// 현재 페이지 접근 권한 확인
async function checkCurrentPagePermission() {
    try {
        // 현재 페이지 URL에서 페이지 ID 추출
        const currentPath = window.location.pathname;
        const pageName = currentPath.split('/').pop().replace('.html', '');
        
        // 로그인 페이지는 항상 접근 가능
        if (pageName === 'login' || pageName === 'index' || pageName === '') {
            return true;
        }
        
        // 인증 상태 확인
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        
        if (data.authenticated || data.is_authenticated) {
            const menuPermissions = data.menu_permissions || [];
            
            // 관리자는 모든 페이지 접근 가능
            if (data.user.role === 'admin') {
                return true;
            }
            
            // 권한 확인
            return menuPermissions.includes(pageName);
        } else {
            // 비로그인 사용자는 기본 페이지만 접근 가능
            const defaultPages = ['index', 'login', 'join', 'inquiry', 'about'];
            return defaultPages.includes(pageName);
        }
    } catch (error) {
        console.error('페이지 권한 확인 중 오류 발생:', error);
        return false;
    }
}

// 페이지 로드 시 현재 페이지 접근 권한 확인
document.addEventListener('DOMContentLoaded', async function() {
    const hasPermission = await checkCurrentPagePermission();
    
    if (!hasPermission) {
        // 접근 권한이 없는 경우 메인 페이지로 리디렉션
        alert('이 페이지에 접근할 권한이 없습니다.');
        window.location.href = 'index.html';
    }
}); 