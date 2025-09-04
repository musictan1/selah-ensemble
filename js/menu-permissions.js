/**
 * 메뉴 권한 관리 JavaScript
 * 모든 HTML 페이지에 포함되어 사용자 역할에 따라 메뉴 항목을 표시하거나 숨깁니다.
 */

console.log('menu-permissions.js loaded!');

// 전역 변수
let userRole = null;
let menuPermissions = [];

// 메뉴 권한 체크 활성화
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOMContentLoaded - Starting menu permission check');
    
    // 모든 메뉴 표시
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        const menuItems = navMenu.querySelectorAll('li');
        menuItems.forEach(menuItem => {
            menuItem.style.display = 'block';
        });
    }
    
    // 로그인 링크는 기본적으로 표시 (마지막 3개 li 요소)
    const menuItems = document.querySelectorAll('.nav-menu li');
    if (menuItems.length >= 3) {
        // 로그인 링크 (마지막에서 3번째)
        menuItems[menuItems.length - 3].style.display = 'block';
        menuItems[menuItems.length - 3].style.visibility = 'visible';
        menuItems[menuItems.length - 3].style.opacity = '1';
        console.log('Login link displayed by default');
    }
    
    try {
        // 사용자 인증 상태 확인
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        console.log('Auth check response:', data);
        
        if (data.is_authenticated) {
            userRole = data.user.role;
            console.log('User authenticated:', data.user);
            await loadMenuPermissions();
            applyMenuPermissions();
            checkCurrentPagePermission();
            updateAuthMenu(true, data.user);
        } else {
            console.log('User not authenticated');
            applyDefaultMenuPermissions();
            updateAuthMenu(false);
        }
    } catch (error) {
        console.error('메뉴 권한 로드 오류:', error);
        applyDefaultMenuPermissions();
        updateAuthMenu(false);
    }
});

// URL에서 메뉴 ID 추출 함수 (현재는 사용하지 않지만 남겨둠)
function getMenuIdFromHref(href) {
    if (!href) return null;
    let path = href.replace(/^https?:\/\/[^\/]+/, '');
    path = path.split('#')[0];
    if (path.endsWith('/')) path = path.slice(0, -1);
    path = path.toLowerCase();

    if (path === '/' || path === '' || path === 'index.html') return 'about';
    if (path === 'index.html' || path === '/index.html') return 'about';
    if (path === 'join.html' || path === '/join.html') return 'join';
    if (path === 'login.html' || path === '/login.html') return 'login';
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
    if (href.includes('index.html#about') || href === '#about') return 'about';
    return null;
}

// 메뉴 권한 로드 함수
async function loadMenuPermissions() {
    try {
        const response = await fetch('/api/menu-permissions');
        const data = await response.json();
        menuPermissions = data.role_permissions[userRole] || [];
    } catch (error) {
        console.error('메뉴 권한 로드 실패:', error);
        menuPermissions = [];
    }
}

// 메뉴 권한 적용 함수
function applyMenuPermissions() {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    // 관리자는 모든 메뉴 표시
    if (userRole === 'admin') {
        const menuItems = navMenu.querySelectorAll('li');
        menuItems.forEach(menuItem => {
            menuItem.style.display = 'block';
        });
        return;
    }
    
    const menuItems = navMenu.querySelectorAll('li');
    menuItems.forEach(menuItem => {
        const link = menuItem.querySelector('a');
        if (!link) return;
        
        const menuId = getMenuIdFromHref(link.getAttribute('href'));
        if (menuId && !menuPermissions.includes(menuId)) {
            menuItem.style.display = 'none';
        } else {
            menuItem.style.display = 'block';
        }
    });
}

// 기본 메뉴 권한 적용 (로그인하지 않은 사용자)
function applyDefaultMenuPermissions() {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    const menuItems = navMenu.querySelectorAll('li');
    menuItems.forEach(menuItem => {
        const link = menuItem.querySelector('a');
        if (!link) return;
        
        const menuId = getMenuIdFromHref(link.getAttribute('href'));
        // 로그인하지 않은 사용자는 기본 메뉴만 표시
        if (menuId && !['about', 'join', 'performances', 'board', 'inquiry', 'login'].includes(menuId)) {
            menuItem.style.display = 'none';
        } else {
            menuItem.style.display = 'block';
        }
    });
}

// 로그인/로그아웃 메뉴 업데이트
function updateAuthMenu(isLoggedIn, user = null) {
    console.log('updateAuthMenu called:', { isLoggedIn, user });
    
    const menuItems = document.querySelectorAll('.nav-menu li');
    if (menuItems.length < 3) return;
    
    const loginItem = menuItems[menuItems.length - 3]; // 로그인
    const logoutItem = menuItems[menuItems.length - 2]; // 로그아웃
    const userInfoItem = menuItems[menuItems.length - 1]; // 사용자 정보
    
    console.log('Elements found:', { loginItem, logoutItem, userInfoItem });
    
    if (isLoggedIn && user) {
        // 로그인된 상태 - 로그아웃과 사용자 정보 표시
        console.log('Setting logged in state');
        loginItem.style.display = 'none';
        logoutItem.style.display = 'block';
        logoutItem.style.visibility = 'visible';
        logoutItem.style.opacity = '1';
        userInfoItem.style.display = 'block';
        userInfoItem.style.visibility = 'visible';
        userInfoItem.style.opacity = '1';
        userInfoItem.innerHTML = `👤 ${user.username} (${getRoleDisplayName(user.role)})`;
        console.log('User info shown:', user.username, user.role);
    } else {
        // 로그인되지 않은 상태 - 로그인 표시
        console.log('Setting logged out state');
        loginItem.style.display = 'block';
        loginItem.style.visibility = 'visible';
        loginItem.style.opacity = '1';
        logoutItem.style.display = 'none';
        userInfoItem.style.display = 'none';
        console.log('Login link shown');
    }
}

// 역할 표시명 변환
function getRoleDisplayName(role) {
    const roleNames = {
        'admin': '관리자',
        'special': '특별회원',
        'regular': '일반회원',
        'new': '신입회원'
    };
    return roleNames[role] || role;
}

// 로그아웃 함수 (전역 함수로 등록)
window.logout = function() {
    if (confirm('로그아웃 하시겠습니까?')) {
        // 서버에 로그아웃 요청
        fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('로그아웃 응답:', data);
            // 로그아웃 후 메뉴 업데이트
            updateAuthMenu(false);
            userRole = null;
            alert('로그아웃되었습니다.');
        })
        .catch(error => {
            console.error('로그아웃 오류:', error);
            // 오류가 발생해도 메뉴 업데이트
            updateAuthMenu(false);
            userRole = null;
            alert('로그아웃되었습니다.');
        });
    }
}

// 현재 페이지 접근 권한 확인
function checkCurrentPagePermission() {
    // 로그인하지 않은 사용자는 권한 체크 건너뛰기
    if (!userRole) {
        return;
    }
    
    // 관리자는 모든 페이지 접근 가능
    if (userRole === 'admin') {
        return;
    }
    
    const currentPath = window.location.pathname;
    const currentMenuId = getMenuIdFromHref(currentPath);
    
    // 메인 페이지(about)는 모든 사용자 접근 가능
    if (currentMenuId === 'about') {
        return;
    }
    
    if (currentMenuId && !menuPermissions.includes(currentMenuId)) {
        alert('접근 권한이 없습니다.');
        window.location.href = 'index.html';
        return;
    }
}