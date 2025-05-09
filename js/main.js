// 스크롤 시 헤더 스타일 변경
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
    } else {
        header.style.background = '#fff';
    }
});

// 모바일 메뉴 토글
document.addEventListener('DOMContentLoaded', function() {
    // 모바일 메뉴 버튼이 이미 존재하는지 확인
    let menuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.nav-menu');
    
    if (!menuBtn) {
        // 버튼이 없으면 생성
        menuBtn = document.createElement('button');
        menuBtn.className = 'mobile-menu-btn';
        menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        const navContainer = document.querySelector('nav');
        if (navContainer) {
            navContainer.appendChild(menuBtn);
        }
    }

    // 메뉴 버튼 클릭 이벤트
    menuBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // 클래스 토글
        if (nav) {
            nav.classList.toggle('active');
            
            // 아이콘 변경
            if (nav.classList.contains('active')) {
                menuBtn.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }
        }
    });
    
    // 화면 크기 변경 시 모바일 메뉴 처리
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && nav) {
            nav.classList.remove('active');
            menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        }
    });
    
    // 메뉴 항목 클릭 시 모바일 메뉴 닫기
    if (nav) {
        nav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    nav.classList.remove('active');
                    menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
                }
            });
        });
    }
    
    // 문서 클릭 시 메뉴 닫기
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && nav && nav.classList.contains('active')) {
            // 클릭된 요소가 메뉴나 메뉴 버튼이 아닌 경우 메뉴 닫기
            if (!nav.contains(e.target) && e.target !== menuBtn && !menuBtn.contains(e.target)) {
                nav.classList.remove('active');
                menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }
        }
    });
    
    // 모바일 화면에서 로그인 링크 확인
    if (window.innerWidth <= 768) {
        ensureLoginLink();
    }
});

// 로그인 링크 확인 및 추가
function ensureLoginLink() {
    const nav = document.querySelector('.nav-menu');
    if (!nav) return;
    
    // 로그인 링크가 있는지 확인
    const loginLink = Array.from(nav.querySelectorAll('a')).find(link => 
        link.href.includes('login.html')
    );
    
    if (!loginLink) {
        // 로그인 링크가 없으면 추가
        const loginItem = document.createElement('li');
        const newLoginLink = document.createElement('a');
        newLoginLink.href = 'login.html';
        newLoginLink.textContent = '로그인';
        loginItem.appendChild(newLoginLink);
        nav.appendChild(loginItem);
    }
}

// 스무스 스크롤
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 이미지 로드 시 애니메이션
const images = document.querySelectorAll('img');
images.forEach(img => {
    img.addEventListener('load', function() {
        this.style.opacity = '1';
    });
    img.style.opacity = '0';
    img.style.transition = 'opacity 0.5s ease-in-out';
});

// 파일 목록 업데이트 함수
function updateFileList() {
    fetch('/check_files')
        .then(response => response.json())
        .then(data => {
            // 음악 파일 업데이트
            if (data.music) {
                Object.entries(data.music).forEach(([genre, file]) => {
                    if (file) {
                        const item = document.querySelector(`[data-genre="${genre}"]`);
                        if (item) {
                            item.querySelector('.no-file').style.display = 'none';
                            const downloadBtn = item.querySelector('.download-btn');
                            downloadBtn.style.display = 'block';
                            downloadBtn.href = `/download/music?genre=${genre}`;
                        }
                    }
                });
            }

            // 악보 파일 업데이트
            if (data.scores) {
                const item = document.querySelector('[data-type="scores"]');
                if (item) {
                    item.querySelector('.no-file').style.display = 'none';
                    const downloadBtn = item.querySelector('.download-btn');
                    downloadBtn.style.display = 'block';
                    downloadBtn.href = '/download/scores';
                }
            }

            // 영상 파일 업데이트
            if (data.videos) {
                const item = document.querySelector('[data-type="videos"]');
                if (item) {
                    item.querySelector('.no-video').style.display = 'none';
                    const downloadBtn = item.querySelector('.download-btn');
                    downloadBtn.style.display = 'block';
                    downloadBtn.href = '/download/videos';
                }
            }
        });
}

// 페이지 로드 시 파일 목록 업데이트
document.addEventListener('DOMContentLoaded', function() {
    updateFileList();
    // 5초마다 파일 목록 업데이트
    setInterval(updateFileList, 5000);
}); 