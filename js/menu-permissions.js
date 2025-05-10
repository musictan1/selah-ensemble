/**
 * 메뉴 권한 관리 JavaScript
 * 모든 HTML 페이지에 포함되어 사용자 역할에 따라 메뉴 항목을 표시하거나 숨깁니다.
 */

console.log('menu-permissions.js loaded!');

// 전역 변수
let userRole = null;
let menuPermissions = [];

// 메뉴 권한과 상관없이 항상 모든 메뉴가 보이게 하는 최소 코드

document.addEventListener('DOMContentLoaded', function() {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    const menuItems = navMenu.querySelectorAll('li');
    menuItems.forEach(menuItem => {
        menuItem.style.display = '';
    });
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

// 아래 함수들은 현재 메뉴 숨김/권한 체크를 하지 않으므로 남겨두기만 합니다.
function addLoginMenuItem() {}
function applyDefaultMenuPermissions() {}
function checkCurrentPagePermission() {}
async function checkCurrentPagePermission() {}