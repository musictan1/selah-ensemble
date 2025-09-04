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
    // 일시적으로 모든 메뉴 표시 (문제 해결을 위해)
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        const menuItems = navMenu.querySelectorAll('li');
        menuItems.forEach(menuItem => {
            menuItem.style.display = 'block';
        });
    }
    
    try {
        // 사용자 인증 상태 확인
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        
        if (data.is_authenticated) {
            userRole = data.user.role;
            await loadMenuPermissions();
            applyMenuPermissions();
            checkCurrentPagePermission();
        } else {
            applyDefaultMenuPermissions();
        }
    } catch (error) {
        console.error('메뉴 권한 로드 오류:', error);
        applyDefaultMenuPermissions();
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
        menuPermissions = data.permissions[userRole] || [];
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
        if (menuId && !['about', 'performances', 'board', 'inquiry'].includes(menuId)) {
            menuItem.style.display = 'none';
        } else {
            menuItem.style.display = 'block';
        }
    });
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