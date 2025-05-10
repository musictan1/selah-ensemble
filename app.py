import os
import json
import shutil
import uuid
import random
import string
import urllib.parse
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from flask import Flask, request, session, jsonify, send_from_directory, send_file, redirect, url_for, render_template
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_cors import CORS

# 앱 초기화
app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# 설정 로드
class Config:
    SECRET_KEY = 'Sela-Ensemble-Secret-Key-2024'  # 안전한 키로 변경
    SESSION_COOKIE_SECURE = False  # HTTPS 사용 시 True로 변경
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {
        'music': {'mp3', 'wav', 'm4a', 'ogg', 'aac'},
        'scores': {'pdf', 'jpg', 'jpeg', 'png'},
        'videos': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}
    }
    
# 설정 적용
app.config.from_object(Config)

# 추가 세션 설정
app.config.update(
    SESSION_COOKIE_NAME="sela_session",
    JSONIFY_PRETTYPRINT_REGULAR=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),  # 세션 만료 시간을 30일로 설정
    SESSION_TYPE='filesystem'  # 세션을 파일 시스템에 저장
)

# 세션 초기화
Session(app)

# 디버깅 모드 활성화
app.debug = True

# 상수 정의
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
POSTS_FILE = os.path.join(DATA_FOLDER, 'posts.json')
INQUIRIES_FILE = os.path.join(DATA_FOLDER, 'inquiries.json')
SCHEDULES_FILE = os.path.join(DATA_FOLDER, 'schedules.json')

# 사용자 역할 및 권한 정의
USER_ROLES = {
    'admin': '운영자',
    'special': '특별회원',
    'regular': '일반회원',
    'new': '신입회원'
}

# 권한 정의 
USER_PERMISSIONS = {
    'admin': ['manage_users', 'delete_posts', 'manage_files', 'view_all'],
    'special': ['delete_posts', 'manage_files', 'view_all'],
    'regular': ['view_all'],
    'new': ['view_basic']
}

# 메뉴 접근 권한 정의
MENU_PERMISSIONS = {
    'admin': ['about', 'join', 'performances', 'music', 'scores', 'board', 'schedule', 'inquiry', 'sponsor', 'youtube', 'admin'],
    'special': ['about', 'performances', 'music', 'scores', 'board', 'schedule', 'inquiry', 'sponsor', 'youtube'],
    'regular': ['about', 'performances', 'music', 'scores', 'board', 'schedule', 'inquiry', 'youtube'],
    'new': ['about', 'performances', 'board', 'inquiry']
}

# 메뉴 아이템 정의
MENU_ITEMS = [
    {'id': 'about', 'name': '소개', 'url': 'index.html#about'},
    {'id': 'join', 'name': '회원가입', 'url': 'join.html'},
    {'id': 'performances', 'name': '찬양사역영상', 'url': 'performances.html'},
    {'id': 'music', 'name': '음악파일', 'url': 'music.html'},
    {'id': 'scores', 'name': '악보파일', 'url': 'scores.html'},
    {'id': 'board', 'name': '게시판', 'url': 'board.html'},
    {'id': 'schedule', 'name': '일정관리', 'url': 'schedule.html'},
    {'id': 'inquiry', 'name': '찬양사역문의', 'url': 'inquiry.html'},
    {'id': 'sponsor', 'name': '후원계좌', 'url': 'sponsor.html'},
    {'id': 'youtube', 'name': '유튜브', 'url': 'youtube.html'},
    {'id': 'instagram', 'name': '인스타그램', 'url': 'https://www.instagram.com/selahensemble1/'},
    {'id': 'admin', 'name': '회원관리', 'url': 'admin.html'}
]

# 필요한 디렉토리 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music', 'ai'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music', 'mr'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music', 'live'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'scores'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

print("Flask 애플리케이션 설정 완료:")
print(f"세션 타입: {app.config['SESSION_TYPE']}")
print(f"세션 파일 디렉토리: {app.config['SESSION_FILE_DIR']}")
print(f"세션 쿠키 설정: 보안={app.config['SESSION_COOKIE_SECURE']}, HttpOnly={app.config['SESSION_COOKIE_HTTPONLY']}")
print(f"업로드 폴더: {UPLOAD_FOLDER}")
print(f"데이터 폴더: {DATA_FOLDER}")
print(f"허용된 파일 확장자: {app.config['ALLOWED_EXTENSIONS']}")

# 파일 경로 설정
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
MUSIC_FOLDER = os.path.join(UPLOAD_FOLDER, 'music')
SCORES_FOLDER = os.path.join(UPLOAD_FOLDER, 'scores')
VIDEOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
DATA_FOLDER = 'data'
POSTS_FILE = os.path.join(DATA_FOLDER, 'posts.json')
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
INQUIRIES_FILE = os.path.join(DATA_FOLDER, 'inquiries.json')
SCHEDULES_FILE = os.path.join(DATA_FOLDER, 'schedules.json')

# 파일 시스템과 data.json 동기화
def sync_data_with_filesystem():
    try:
        # 기본 데이터 구조
        data = {
            "music": {
                "ai": [],
                "mr": [],
                "live": []
            },
            "scores": [],
            "videos": []
        }
        
        print("\n파일 시스템 동기화 시작...")
        
        # 기존 데이터 파일이 있으면 읽기
        data_file_path = os.path.join(DATA_FOLDER, 'data.json')
        existing_data = None
        
        if os.path.exists(data_file_path):
            try:
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"기존 data.json 파일 로드 성공")
            except Exception as e:
                print(f"기존 data.json 파일 로드 실패: {e}")
                # 로드 실패 시 백업 생성
                backup_path = data_file_path + '.bak.' + datetime.now().strftime('%Y%m%d%H%M%S')
                try:
                    shutil.copy2(data_file_path, backup_path)
                    print(f"손상된 data.json 백업 생성: {backup_path}")
                except Exception as backup_error:
                    print(f"백업 생성 실패: {backup_error}")
        
        # 음악 파일 확인
        for category in ['ai', 'mr', 'live']:
            category_path = os.path.join(MUSIC_FOLDER, category)
            print(f"카테고리 경로 확인: {category_path}")
            
            if os.path.exists(category_path):
                try:
                    file_list = os.listdir(category_path)
                    print(f"{category} 카테고리 파일 수: {len(file_list)}")
                    if file_list:
                        print(f"{category} 카테고리 파일 목록 샘플: {', '.join(file_list[:5])}" + 
                              (f"... 외 {len(file_list)-5}개" if len(file_list) > 5 else ""))
                    
                    # 파일 시스템에서 파일 추가
                    for filename in file_list:
                        file_path = os.path.join(category_path, filename)
                        if os.path.isfile(file_path):
                            if filename not in data['music'][category]:
                                data['music'][category].append(filename)
                    
                    # 기존 데이터에서 있었지만 파일 시스템에 없는 파일 처리
                    if existing_data and 'music' in existing_data and category in existing_data['music']:
                        for filename in existing_data['music'][category]:
                            file_path = os.path.join(category_path, filename)
                            if not os.path.isfile(file_path) and filename not in data['music'][category]:
                                print(f"주의: 파일 시스템에 없는 파일이지만 기존 데이터에 있던 파일 추가: {filename}")
                                data['music'][category].append(filename)
                    
                    # 정렬
                    data['music'][category].sort()
                except Exception as e:
                    print(f"{category} 카테고리 처리 중 오류 발생: {str(e)}")
            else:
                print(f"카테고리 경로가 존재하지 않음: {category_path}")
                try:
                    os.makedirs(category_path, exist_ok=True)
                    print(f"카테고리 경로 생성: {category_path}")
                except Exception as e:
                    print(f"카테고리 경로 생성 중 오류 발생: {str(e)}")
        
        # 악보 파일 확인
        if os.path.exists(SCORES_FOLDER):
            try:
                files_on_disk = set()
                # 기본 디렉토리의 파일 확인
                for f in os.listdir(SCORES_FOLDER):
                    if os.path.isfile(os.path.join(SCORES_FOLDER, f)):
                        files_on_disk.add(f)
                    
                # 하위 디렉토리 확인 (예: scores/default)
                for subdir in os.listdir(SCORES_FOLDER):
                    subdir_path = os.path.join(SCORES_FOLDER, subdir)
                    if os.path.isdir(subdir_path):
                        print(f"악보 하위 디렉토리 확인: {subdir}")
                        for f in os.listdir(subdir_path):
                            if os.path.isfile(os.path.join(subdir_path, f)):
                                files_on_disk.add(f)
                                print(f"하위 디렉토리 '{subdir}'에서 파일 '{f}' 발견")
                
                # 실제 존재하는 파일만 유지하고 누락된 파일 추가
                data['scores'] = [f for f in data['scores'] if f in files_on_disk]
                for f in files_on_disk:
                    if f not in data['scores']:
                        data['scores'].append(f)
                        print(f"악보 파일 '{f}' 추가됨")
                
                data['scores'].sort()
                print(f"악보: 파일 시스템 {len(files_on_disk)}개, 데이터 {len(data['scores'])}개")
            except Exception as e:
                print(f"악보 파일 검증 중 오류: {e}")
        else:
            print(f"악보 폴더가 존재하지 않음: {SCORES_FOLDER}")
            try:
                os.makedirs(SCORES_FOLDER, exist_ok=True)
                print(f"악보 폴더 생성: {SCORES_FOLDER}")
            except Exception as e:
                print(f"악보 폴더 생성 중 오류 발생: {str(e)}")
        
        # 영상 파일 확인
        if os.path.exists(VIDEOS_FOLDER):
            try:
                files_on_disk = set()
                # 기본 디렉토리의 파일 확인
                for f in os.listdir(VIDEOS_FOLDER):
                    if os.path.isfile(os.path.join(VIDEOS_FOLDER, f)):
                        files_on_disk.add(f)
                    
                # 하위 디렉토리 확인 (예: videos/default)
                default_dir = os.path.join(VIDEOS_FOLDER, 'default')
                if os.path.exists(default_dir):
                    print(f"비디오 하위 디렉토리 확인: default")
                    for f in os.listdir(default_dir):
                        if os.path.isfile(os.path.join(default_dir, f)):
                            files_on_disk.add(f)
                
                # 데이터 파일과 실제 파일 동기화
                data['videos'] = [f for f in data['videos'] if f in files_on_disk]
                
                # 파일 시스템에 있지만 데이터에 없는 파일 추가
                for f in files_on_disk:
                    if f not in data['videos']:
                        data['videos'].append(f)
                
                # 알파벳 순으로 정렬
                data['videos'].sort()
                
                print(f"비디오: 파일 시스템 {len(files_on_disk)}개, 데이터 {len(data['videos'])}개")
            except Exception as e:
                print(f"비디오 파일 검증 중 오류: {e}")
        else:
            print(f"영상 폴더가 존재하지 않음: {VIDEOS_FOLDER}")
            try:
                os.makedirs(VIDEOS_FOLDER, exist_ok=True)
                print(f"영상 폴더 생성: {VIDEOS_FOLDER}")
            except Exception as e:
                print(f"영상 폴더 생성 중 오류 발생: {str(e)}")
        
        # 데이터 저장 전 카테고리별 파일 개수 출력
        print(f"AI 카테고리 파일 개수: {len(data['music']['ai'])}")
        print(f"MR 카테고리 파일 개수: {len(data['music']['mr'])}")
        print(f"Live 카테고리 파일 개수: {len(data['music']['live'])}")
        print(f"악보 파일 개수: {len(data['scores'])}")
        print(f"영상 파일 개수: {len(data['videos'])}")
        
        # 데이터 저장
        print("데이터 파일 저장 중...")
        with open(data_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("파일 시스템과 데이터 파일이 동기화되었습니다.")
        return True
    except Exception as e:
        print(f"파일 시스템 동기화 중 오류 발생: {e}")
        return False

# 필요한 디렉토리 생성
def create_directories():
    directories = [
        MUSIC_FOLDER,
        SCORES_FOLDER,
        VIDEOS_FOLDER,
        DATA_FOLDER,
        os.path.join(UPLOAD_FOLDER, 'posts')
    ]
    
    # 음악 카테고리 디렉토리 생성
    for category in ['ai', 'mr', 'live']:
        directories.append(os.path.join(MUSIC_FOLDER, category))
    
    # 모든 디렉토리 생성
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"디렉토리 생성 또는 확인됨: {directory}")
        except Exception as e:
            print(f"디렉토리 생성 중 오류 발생: {directory} - {e}")
    
    # 기본 데이터 파일 생성
    try:
        data_json_path = os.path.join(DATA_FOLDER, 'data.json')
        if not os.path.exists(data_json_path):
            with open(data_json_path, 'w', encoding='utf-8') as f:
                json.dump({"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}, f, ensure_ascii=False)
            print(f"기본 데이터 파일 생성됨: {data_json_path}")
        
        # 기본 일정 파일 생성
        schedules_json_path = os.path.join(DATA_FOLDER, 'schedules.json')
        if not os.path.exists(schedules_json_path):
            with open(schedules_json_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            print(f"기본 일정 파일 생성됨: {schedules_json_path}")
    except Exception as e:
        print(f"기본 데이터 파일 생성 중 오류 발생: {e}")

create_directories()
sync_data_with_filesystem()

# 유틸리티 함수
def allowed_file(filename, category):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS[category]

def custom_secure_filename(filename):
    """한글 파일명을 유지하면서 안전한 파일명으로 변환합니다."""
    if not filename:
        return ""
    
    # 파일 확장자 추출
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        # 기본적인 필터링 - 경로 구분자와 일부 위험한 문자 제거
        name = name.replace('/', '').replace('\\', '').replace('..', '').replace('&', '_')
        name = name.replace('?', '').replace('*', '').replace(':', '_').replace('|', '_')
        # 파일명 앞뒤 공백 제거
        name = name.strip()
        # 수정된 이름과 확장자 결합
        return f"{name}.{ext.lower()}"
    
    # 확장자가 없는 경우
    return filename.replace('/', '').replace('\\', '').strip()

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# 데이터 관리 함수
def load_users():
    try:
        if not os.path.exists(USERS_FILE):
            # 파일이 없으면 빈 리스트로 초기화
            save_users([])
            return []
            
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return users if isinstance(users, list) else []
    except Exception as e:
        print(f"사용자 데이터 로드 중 오류 발생: {e}")
        return []

def save_users(users):
    try:
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        
        # 임시 파일에 먼저 저장
        temp_file = USERS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
            
        # 임시 파일을 실제 파일로 이동 (원자적 연산)
        os.replace(temp_file, USERS_FILE)
    except Exception as e:
        print(f"사용자 데이터 저장 중 오류 발생: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

def load_posts():
    try:
        if not os.path.exists(POSTS_FILE):
            return []
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            return posts if isinstance(posts, list) else []
    except Exception as e:
        print(f"게시글 데이터 로드 중 오류 발생: {e}")
        return []

def save_posts(posts):
    try:
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"게시글 데이터 저장 중 오류 발생: {e}")

# 문의 관련 함수
def load_inquiries():
    try:
        if os.path.exists(INQUIRIES_FILE):
            with open(INQUIRIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_inquiries(inquiries):
    try:
        with open(INQUIRIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(inquiries, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"문의 데이터 저장 중 오류 발생: {e}")
        return False

# 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 라우트
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        # HTML 파일 요청 처리
        if path.endswith('.html'):
            return send_from_directory('.', path)
        
        # 정적 파일 요청 처리 - 대소문자 구분 없이 처리
        if (path.lower().startswith('css/') or 
            path.lower().startswith('js/') or 
            path.lower().startswith('images/') or 
            path.lower().startswith('imgs/') or
            path.lower().startswith('img/')):
            return send_from_directory('.', path)
            
        # 특수 대문자 경로 처리
        if path.startswith('IMAGES/'):
            return send_from_directory('.', path)
            
        # API 요청 처리
        if path.startswith('api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
            
        # 기본적으로 index.html 반환
        return send_from_directory('.', 'index.html')
    except Exception as e:
        print(f"Error serving {path}: {e}")
        return "File not found", 404

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자 이름과 비밀번호를 입력해주세요.'}), 400
            
        users = load_users()
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        
        if user:
            # 세션을 영구적으로 설정
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # 사용자 정보에서 비밀번호 제외
            safe_user = user.copy()
            if 'password' in safe_user:
                del safe_user['password']
                
            return jsonify({
                'message': '로그인 성공',
                'user': safe_user
            })
        else:
            return jsonify({'error': '잘못된 사용자 이름 또는 비밀번호입니다.'}), 401
            
    except Exception as e:
        print(f"로그인 처리 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        # 세션에서 사용자 정보 가져오기 (디버깅용)
        user_id = session.get('user_id')
        username = session.get('username')
        print(f"로그아웃 시도 - 사용자: {username}(ID: {user_id})")
        
        # 세션 초기화
        session.clear()
        
        # 성공 응답 반환
        response = jsonify({
            'message': '로그아웃되었습니다.',
            'redirect': 'index.html'
        })
        
        print("로그아웃 성공")
        return response
    except Exception as e:
        print(f"로그아웃 중 오류 발생: {str(e)}")
        return jsonify({'error': f'로그아웃 처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/check-auth')
def check_auth():
    try:
        user_id = session.get('user_id')
        if user_id:
            users = load_users()
            user = next((u for u in users if u['id'] == user_id), None)
            
            if user:
                # 사용자 정보에서 비밀번호 제외
                safe_user = user.copy()
                if 'password' in safe_user:
                    del safe_user['password']
                    
                return jsonify({
                    'authenticated': True,
                    'is_authenticated': True,
                    'user': safe_user
                })
                
        return jsonify({
            'authenticated': False,
            'is_authenticated': False
        })
    except Exception as e:
        print(f"인증 확인 중 오류 발생: {e}")
        return jsonify({
            'authenticated': False,
            'is_authenticated': False,
            'error': str(e)
        }), 500

# 서버 시작 시 초기화
@app.before_request
def initialize():
    try:
        # 기본 관리자 계정 설정
        users = load_users()
        print(f"초기화 - 현재 사용자 수: {len(users)}")  # 디버깅용 로그
        
        # 관리자 계정이 없으면 생성
        if not any(u['username'] == 'gofly4u' for u in users):
            print("기본 관리자 계정 생성")  # 디버깅용 로그
            admin_user = {
                'id': 1,  # ID를 1로 고정
                'username': 'gofly4u',
                'password': 'admin123',
                'name': '관리자',
                'email': 'gofly4u@gmail.com',
                'role': 'admin',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            users = [admin_user]  # 기존 사용자 목록을 초기화하고 관리자만 추가
            save_users(users)
            print(f"관리자 계정 생성 완료: {admin_user}")  # 디버깅용 로그
    except Exception as e:
        print(f"초기화 중 오류 발생: {str(e)}")  # 디버깅용 로그

# 파일 관련 API 추가
@app.route('/check_files', methods=['GET'])
def check_files():
    try:
        print("\n==== 파일 목록 요청 수신됨 ====")
        
        # 요청 정보 로깅
        timestamp = request.args.get('t', 'none')
        print(f"타임스탬프: {timestamp}")
        
        # 항상 파일 시스템과 데이터 동기화 수행
        sync_result = sync_data_with_filesystem()
        if not sync_result:
            print("동기화 과정에서 오류가 발생했지만, 계속 진행합니다")
        
        # 데이터 파일 읽기 시도
        data_file_path = os.path.join(DATA_FOLDER, 'data.json')
        print(f"데이터 파일 읽기 시도: {data_file_path}")
        
        if not os.path.exists(data_file_path):
            print(f"데이터 파일이 존재하지 않음: {data_file_path}, 기본 데이터 생성")
            data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        else:
            try:
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"데이터 파일 읽기 성공: {len(str(data))}바이트")
                
                # 파일 존재 유효성 검사 및 정렬
                for category in ['ai', 'mr', 'live']:
                    category_path = os.path.join(MUSIC_FOLDER, category)
                    if os.path.exists(category_path):
                        try:
                            # 실제 존재하는 파일 목록 가져오기
                            files_on_disk = set()
                            for f in os.listdir(category_path):
                                if os.path.isfile(os.path.join(category_path, f)):
                                    files_on_disk.add(f)
                            
                            # 실제 존재하는 파일만 목록에 유지
                            data['music'][category] = [f for f in data['music'][category] if f in files_on_disk]
                            
                            # 파일 시스템에 있지만 데이터에 없는 파일 추가
                            for f in files_on_disk:
                                if f not in data['music'][category]:
                                    data['music'][category].append(f)
                                    print(f"파일 시스템에서 발견된 '{f}' 파일 추가")
                            
                            # 정렬 (한글 파일명 고려)
                            data['music'][category].sort()
                            
                            print(f"{category} 카테고리: 파일 시스템 {len(files_on_disk)}개, 데이터 {len(data['music'][category])}개")
                        except Exception as e:
                            print(f"{category} 카테고리 검증 중 오류: {e}")
                
                # 스코어 파일 검증
                if os.path.exists(SCORES_FOLDER):
                    try:
                        files_on_disk = set()
                        # 기본 디렉토리의 파일 확인
                        for f in os.listdir(SCORES_FOLDER):
                            if os.path.isfile(os.path.join(SCORES_FOLDER, f)):
                                files_on_disk.add(f)
                        
                        # 하위 디렉토리 확인 (예: scores/default)
                        for subdir in os.listdir(SCORES_FOLDER):
                            subdir_path = os.path.join(SCORES_FOLDER, subdir)
                            if os.path.isdir(subdir_path):
                                print(f"악보 하위 디렉토리 확인: {subdir}")
                                for f in os.listdir(subdir_path):
                                    if os.path.isfile(os.path.join(subdir_path, f)):
                                        files_on_disk.add(f)
                                        print(f"하위 디렉토리 '{subdir}'에서 파일 '{f}' 발견")
                        
                        # 실제 존재하는 파일만 유지하고 누락된 파일 추가
                        data['scores'] = [f for f in data['scores'] if f in files_on_disk]
                        for f in files_on_disk:
                            if f not in data['scores']:
                                data['scores'].append(f)
                                print(f"악보 파일 '{f}' 추가됨")
                        
                        data['scores'].sort()
                        print(f"악보: 파일 시스템 {len(files_on_disk)}개, 데이터 {len(data['scores'])}개")
                    except Exception as e:
                        print(f"악보 파일 검증 중 오류: {e}")
                
                # 비디오 파일 검증
                if os.path.exists(VIDEOS_FOLDER):
                    try:
                        files_on_disk = set()
                        # 기본 디렉토리의 파일 확인
                        for f in os.listdir(VIDEOS_FOLDER):
                            if os.path.isfile(os.path.join(VIDEOS_FOLDER, f)):
                                files_on_disk.add(f)
                        
                        # 하위 디렉토리 확인 (예: videos/default)
                        default_dir = os.path.join(VIDEOS_FOLDER, 'default')
                        if os.path.exists(default_dir):
                            print(f"비디오 하위 디렉토리 확인: default")
                            for f in os.listdir(default_dir):
                                if os.path.isfile(os.path.join(default_dir, f)):
                                    files_on_disk.add(f)
                        
                        # 데이터 파일과 실제 파일 동기화
                        data['videos'] = [f for f in data['videos'] if f in files_on_disk]
                        
                        # 파일 시스템에 있지만 데이터에 없는 파일 추가
                        for f in files_on_disk:
                            if f not in data['videos']:
                                data['videos'].append(f)
                        
                        # 알파벳 순으로 정렬
                        data['videos'].sort()
                        
                        print(f"비디오: 파일 시스템 {len(files_on_disk)}개, 데이터 {len(data['videos'])}개")
                    except Exception as e:
                        print(f"비디오 파일 검증 중 오류: {e}")
                
                # 변경된 데이터 저장
                with open(data_file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("데이터 파일 업데이트 완료")
                
            except json.JSONDecodeError as e:
                print(f"JSON 디코드 오류: {e}, 기본 데이터 생성")
                data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
                
                # 백업 생성
                backup_path = data_file_path + '.bak.' + datetime.now().strftime('%Y%m%d%H%M%S')
                try:
                    shutil.copy2(data_file_path, backup_path)
                    print(f"손상된 data.json 백업 생성: {backup_path}")
                except Exception as backup_error:
                    print(f"백업 생성 실패: {backup_error}")
                
                # 새 데이터 파일 생성
                with open(data_file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
        
        # 응답 데이터에 추가 정보 포함
        result = {
            'status': 'success',
            'message': '파일 목록을 성공적으로 조회했습니다.',
            'timestamp': timestamp,
            **data
        }
        
        print("==== 파일 목록 요청 처리 완료 ====\n")
        return jsonify(result)
    except Exception as e:
        error_msg = f"파일 목록 조회 중 오류 발생: {str(e)}"
        print(error_msg)
        return jsonify({
            'status': 'error',
            'error': error_msg,
            'timestamp': request.args.get('t', 'none'),
            'music': {"ai": [], "mr": [], "live": []},
            'scores': [],
            'videos': []
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print(f"\n==== 파일 업로드 요청 ====")
        
        if 'file' not in request.files:
            print(f"파일이 요청에 없습니다.")
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400

        file = request.files['file']
        category = request.form.get('category')
        
        print(f"업로드 카테고리: {category}")
        print(f"원본 파일명: {file.filename}")
        
        if not category:
            print(f"카테고리가 지정되지 않았습니다.")
            return jsonify({'success': False, 'error': '카테고리가 지정되지 않았습니다.'}), 400
            
        if file.filename == '':
            print(f"선택된 파일이 없습니다.")
            return jsonify({'success': False, 'error': '선택된 파일이 없습니다.'}), 400
            
        # 카테고리 확인 및 처리
        category_parts = category.split('/')
        
        # 카테고리 정보 수정
        main_category = category_parts[0]
        sub_category = category_parts[1] if len(category_parts) > 1 else None
        
        # ai, mr, live 카테고리를 music 하위 카테고리로 처리
        if len(category_parts) == 2 and main_category == 'music' and sub_category in ['ai', 'mr', 'live']:
            # 기존 처리 유지
            pass
        elif len(category_parts) == 1 and main_category in ['ai', 'mr', 'live']:
            # ai, mr, live가 최상위로 지정된 경우 music으로 변경
            main_category = 'music'
            sub_category = category_parts[0]
            category = f"music/{sub_category}"
            print(f"카테고리 자동 수정: {category}")
        elif len(category_parts) != 2 or main_category not in ['music', 'scores', 'videos']:
            print(f"잘못된 카테고리입니다: {category}")
            return jsonify({'success': False, 'error': '잘못된 카테고리입니다.'}), 400
        
        print(f"메인 카테고리: {main_category}, 서브 카테고리: {sub_category}")
        
        # 파일 형식 확인
        if not allowed_file(file.filename, main_category):
            print(f"허용되지 않은 파일 형식입니다: {file.filename}")
            return jsonify({'success': False, 'error': '허용되지 않은 파일 형식입니다.'}), 400
            
        # 파일 저장 경로 설정
        if sub_category:
            upload_path = os.path.join(UPLOAD_FOLDER, main_category, sub_category)
        else:
            upload_path = os.path.join(UPLOAD_FOLDER, main_category)
        
        print(f"업로드 경로: {upload_path}")
            
        # 디렉토리가 없으면 생성
        try:
            os.makedirs(upload_path, exist_ok=True)
            print(f"디렉토리 확인/생성 완료: {upload_path}")
        except Exception as e:
            print(f"디렉토리 생성 실패: {e}")
            return jsonify({'success': False, 'error': f'업로드 디렉토리 생성 실패: {e}'}), 500
        
        # 파일 저장 - 안전한 파일명 사용
        try:
            filename = custom_secure_filename(file.filename)
            file_path = os.path.join(upload_path, filename)
            print(f"저장할 파일 경로: {file_path}")
            
            # 기존 파일 확인
            if os.path.exists(file_path):
                print(f"같은 이름의 파일이 이미 존재합니다. 백업 후 덮어쓰기를 시도합니다.")
                # 백업 파일 생성
                backup_path = file_path + '.bak'
                shutil.copy2(file_path, backup_path)
            
            # 파일 저장
            file.save(file_path)
            
            # 저장된 파일 확인
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"파일 저장 성공: {file_path} (크기: {os.path.getsize(file_path)} 바이트)")
                # 백업 파일 삭제 (성공적으로 저장된 경우)
                backup_path = file_path + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    print(f"백업 파일 삭제 완료: {backup_path}")
            else:
                print(f"파일 저장 실패 또는 파일 크기가 0입니다: {file_path}")
                # 백업에서 복원
                backup_path = file_path + '.bak'
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    os.remove(backup_path)
                    print(f"백업에서 복원 완료")
                return jsonify({'success': False, 'error': '파일이 올바르게 저장되지 않았습니다.'}), 500
        except Exception as e:
            print(f"파일 저장 실패: {e}")
            return jsonify({'success': False, 'error': f'파일 저장 실패: {e}'}), 500
        
        # 데이터 업데이트
        try:
            data_path = os.path.join(DATA_FOLDER, 'data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"data.json 파일 로드 성공")
            else:
                data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
                print(f"data.json 파일이 없어 새로 생성합니다.")
                
            # 파일 정보 데이터에 추가
            if main_category == 'music' and sub_category in ['ai', 'mr', 'live']:
                if filename not in data['music'][sub_category]:
                    data['music'][sub_category].append(filename)
                    data['music'][sub_category].sort()  # 정렬 유지
                    print(f"파일명 '{filename}'을 {main_category}/{sub_category} 목록에 추가했습니다.")
                else:
                    print(f"파일명 '{filename}'이 이미 {main_category}/{sub_category} 목록에 있습니다.")
            elif main_category in ['scores', 'videos']:
                # 점검: 파일이 scores/default와 같은 하위 디렉토리에 저장된 경우 처리
                if main_category == 'scores' and sub_category:
                    # 하위 디렉토리에 저장된 파일도 scores 목록에 추가
                    if filename not in data[main_category]:
                        data[main_category].append(filename)
                        data[main_category].sort()  # 정렬 유지
                        print(f"파일명 '{filename}'을 {main_category} 목록에 추가했습니다. (하위 디렉토리: {sub_category})")
                    else:
                        print(f"파일명 '{filename}'이 이미 {main_category} 목록에 있습니다.")
                else:
                    # 기존 처리 유지
                    if filename not in data[main_category]:
                        data[main_category].append(filename)
                        data[main_category].sort()  # 정렬 유지
                        print(f"파일명 '{filename}'을 {main_category} 목록에 추가했습니다.")
                    else:
                        print(f"파일명 '{filename}'이 이미 {main_category} 목록에 있습니다.")
                    
            # 데이터 저장
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"data.json 파일을 업데이트했습니다.")
                
            # 파일 시스템과 데이터 동기화
            sync_result = sync_data_with_filesystem()
            print(f"파일 시스템과 데이터 동기화 결과: {sync_result}")
            
            print(f"==== 파일 업로드 요청 완료 ====\n")
                
            return jsonify({'success': True, 'filename': filename})
        except Exception as e:
            print(f"데이터 업데이트 중 오류 발생: {e}")
            # 데이터 업데이트 실패해도 파일 자체는 저장되었으니 성공으로 처리
            return jsonify({'success': True, 'filename': filename, 'warning': f'파일은 저장되었으나 데이터 업데이트 중 오류가 발생했습니다: {e}'})
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete/<path:category>/<path:filename>', methods=['DELETE'])
def delete_file(category, filename):
    try:
        # 로그인 여부 확인
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401
            
        # 사용자 정보 확인
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
            
        # 게시판 글이 아닌 경우(music, scores, videos) 관리자만 삭제 가능
        category_parts = category.split('/')
        if category_parts[0] in ['music', 'scores', 'videos'] and user['role'] != 'admin':
            return jsonify({'success': False, 'error': '관리자만 파일을 삭제할 수 있습니다.'}), 403
        
        # 경로 처리 - ai, mr, live 카테고리 파일 경로 수정
        # 요청이 ai/, mr/, live/로 시작하면 music/ 경로를 추가
        if len(category_parts) > 0 and category_parts[0] in ['ai', 'mr', 'live']:
            # music/ 경로를 추가
            modified_category = 'music/' + category
            file_path = os.path.join(UPLOAD_FOLDER, modified_category, filename)
            print(f"수정된 삭제 파일 경로: {file_path}")
        else:
            file_path = os.path.join(UPLOAD_FOLDER, category, filename)
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '파일이 존재하지 않습니다.'}), 404
            
        # 파일 삭제
        os.remove(file_path)
        
        # 데이터 업데이트
        try:
            with open(os.path.join(DATA_FOLDER, 'data.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
            
        # 파일 정보 데이터에서 제거
        if len(category_parts) > 0 and category_parts[0] in ['ai', 'mr', 'live']:
            if filename in data['music'][category_parts[0]]:
                data['music'][category_parts[0]].remove(filename)
        elif len(category_parts) == 2 and category_parts[0] == 'music' and category_parts[1] in ['ai', 'mr', 'live']:
            if filename in data['music'][category_parts[1]]:
                data['music'][category_parts[1]].remove(filename)
        elif category_parts[0] in ['scores', 'videos']:
            if filename in data[category_parts[0]]:
                data[category_parts[0]].remove(filename)
                
        # 데이터 저장
        with open(os.path.join(DATA_FOLDER, 'data.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/edit/<path:category>/<path:filename>', methods=['POST'])
def edit_file(category, filename):
    try:
        print(f"\n==== 파일 수정 요청 시작 ====")
        print(f"카테고리: {category}")
        print(f"원본 파일명(인코딩됨): {filename}")
        
        # 1. 사용자 권한 확인
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
            
        if user['role'] != 'admin':
            return jsonify({'success': False, 'error': '관리자만 파일을 수정할 수 있습니다.'}), 403
        
        # 2. 요청 유효성 검사
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': '선택된 파일이 없습니다.'}), 400
        
        # 3. 디코딩 및 변수 준비
        try:
            # URL에서 디코딩
            try:
                decoded_filename = urllib.parse.unquote(filename)
                print(f"디코딩된 파일명: {decoded_filename}")
            except Exception as decode_error:
                print(f"디코딩 오류 발생, 원본 파일명 사용: {decode_error}")
                decoded_filename = filename
            
            # 카테고리 분석
            category_parts = category.split('/')
            if len(category_parts) < 1 or category_parts[0] not in ['music', 'scores', 'videos']:
                return jsonify({'success': False, 'error': '잘못된 카테고리입니다.'}), 400
            
            main_category = category_parts[0]
            sub_category = category_parts[1] if len(category_parts) > 1 else None
            
            # 파일 형식 확인
            if not allowed_file(file.filename, main_category):
                return jsonify({'success': False, 'error': '허용되지 않은 파일 형식입니다.'}), 400
            
            # 새 파일명 생성
            new_filename = custom_secure_filename(file.filename)
            
            print(f"메인 카테고리: {main_category}")
            print(f"서브 카테고리: {sub_category}")
            print(f"기존 파일명: {decoded_filename}")
            print(f"새 파일명: {new_filename}")
        except Exception as e:
            print(f"파일명 처리 중 오류: {e}")
            return jsonify({'success': False, 'error': f'파일명 처리 오류: {e}'}), 400
        
        # 4. 디렉토리 및 파일 경로 설정
        try:
            # 디렉토리 설정
            if sub_category:
                upload_dir = os.path.join(UPLOAD_FOLDER, main_category, sub_category)
            else:
                upload_dir = os.path.join(UPLOAD_FOLDER, main_category)
            
            # 디렉토리 생성 (없는 경우)
            os.makedirs(upload_dir, exist_ok=True)
            
            # 실제 파일 찾기 (인코딩 문제로 인한 파일 미스매치 방지)
            actual_old_filename = None
            if os.path.exists(os.path.join(upload_dir, decoded_filename)):
                # 정확한 파일명 찾음
                actual_old_filename = decoded_filename
                print(f"정확한 파일명 찾음: {actual_old_filename}")
            else:
                # 디렉토리 내 모든 파일 검색
                print(f"정확한 파일명을 찾을 수 없음, 디렉토리에서 검색 시도...")
                try:
                    dir_files = os.listdir(upload_dir)
                    # 유사한 파일명 검색 (확장자와 이름 일부가 일치하는 경우)
                    file_ext = '.' + decoded_filename.split('.')[-1] if '.' in decoded_filename else ''
                    base_name = decoded_filename.split('.')[0] if '.' in decoded_filename else decoded_filename
                    
                    print(f"검색할 기본 이름: '{base_name}', 확장자: '{file_ext}'")
                    
                    for dir_file in dir_files:
                        # 1. 완전 일치 확인
                        if dir_file == decoded_filename:
                            actual_old_filename = dir_file
                            print(f"완전 일치하는 파일명 찾음: {actual_old_filename}")
                            break
                        
                        # 2. 대소문자 무시 확인
                        elif dir_file.lower() == decoded_filename.lower():
                            actual_old_filename = dir_file
                            print(f"대소문자만 다른 파일명 찾음: {actual_old_filename}")
                            break
                        
                        # 3. 확장자 일치, 이름 유사 확인
                        elif file_ext and dir_file.endswith(file_ext) and base_name.lower() in dir_file.lower():
                            actual_old_filename = dir_file
                            print(f"유사한 파일명 찾음: {actual_old_filename}")
                            break
                    
                    # 4. data.json 확인
                    if not actual_old_filename:
                        data_path = os.path.join(DATA_FOLDER, 'data.json')
                        if os.path.exists(data_path):
                            with open(data_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                
                            # data.json에서 해당 카테고리의 파일 목록 확인
                            if main_category == 'music' and sub_category in data['music']:
                                if decoded_filename in data['music'][sub_category]:
                                    # data.json에 파일이 존재함
                                    actual_old_filename = decoded_filename
                                    print(f"data.json에서 파일명 찾음: {actual_old_filename}")
                except Exception as list_error:
                    print(f"디렉토리 검색 중 오류: {list_error}")
            
            # 파일을 찾지 못한 경우
            if not actual_old_filename:
                # 디코딩된 파일명으로 진행 (새 파일 생성 모드)
                actual_old_filename = decoded_filename
                print(f"파일을 찾지 못해 디코딩된 파일명으로 진행: {actual_old_filename}")
            
            # 파일 경로 설정
            old_file_path = os.path.join(upload_dir, actual_old_filename)
            new_file_path = os.path.join(upload_dir, new_filename)
            
            print(f"업로드 디렉토리: {upload_dir}")
            print(f"기존 파일 경로: {old_file_path}")
            print(f"기존 파일 존재 여부: {os.path.exists(old_file_path)}")
            print(f"새 파일 경로: {new_file_path}")
            print(f"경로 비교 (다른지): {old_file_path != new_file_path}")
            print(f"파일명 비교 (다른지): {actual_old_filename != new_filename}")
            
        except Exception as e:
            print(f"경로 설정 중 오류: {e}")
            return jsonify({'success': False, 'error': f'경로 설정 오류: {e}'}), 500
        
        # 5. 파일 저장 및 교체 (완전히 새로운 구현)
        try:
            # 파일 경로 로깅
            print(f"기존 파일 경로: {old_file_path}")
            print(f"새 파일 경로: {new_file_path}")
            
            # 기존 파일 존재 여부 확인
            old_file_exists = os.path.exists(old_file_path)
            print(f"기존 파일 존재 여부: {old_file_exists}")
            
            # 임시 파일 경로
            temp_file_path = old_file_path + '.temp'
            
            # 1. 새 파일을 임시 파일로 저장
            file_content = file.read()
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            print(f"임시 파일 저장됨: {temp_file_path}")
            
            # 2. 임시 파일 유효성 검사
            if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
                print(f"임시 파일이 유효하지 않음")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return jsonify({'success': False, 'error': '파일 저장에 실패했습니다'}), 500
            
            # 3. 안전한 파일 교체
            # 기존 파일이 있는 경우 백업
            if old_file_exists:
                backup_path = old_file_path + '.bak'
                shutil.copy2(old_file_path, backup_path)
                print(f"기존 파일 백업 생성됨: {backup_path}")
                
                # 기존 파일과 임시 파일의 내용이 동일한지 확인
                try:
                    files_identical = filecmp.cmp(old_file_path, temp_file_path, shallow=False)
                    if files_identical:
                        print(f"파일 내용이 동일함 - 변경 필요 없음")
                        os.remove(temp_file_path)
                        os.remove(backup_path)
                        # 파일 내용이 같으면 성공으로 처리하지만 변경사항 없음 메시지 반환
                        return jsonify({'success': True, 'message': '파일 내용이 동일하여 변경되지 않았습니다'})
                except Exception as cmp_error:
                    print(f"파일 비교 중 오류: {cmp_error}")
                    # 오류 발생 시 계속 진행 (안전하게 새 파일로 교체)
            
            # 4. 실제 파일 교체 (원자적 작업)
            if old_file_exists:
                # 원자적으로 파일 교체 시도
                try:
                    os.replace(temp_file_path, old_file_path)
                    print(f"파일 성공적으로 교체됨: {old_file_path}")
                except Exception as replace_error:
                    print(f"파일 교체 중 오류: {replace_error}")
                    # 대체 방법: 기존 파일 삭제 후 임시 파일 이동
                    os.remove(old_file_path)
                    shutil.move(temp_file_path, old_file_path)
                    print(f"대체 방식으로 파일 교체됨: {old_file_path}")
            else:
                # 기존 파일이 없으면 임시 파일을 이동
                shutil.move(temp_file_path, old_file_path)
                print(f"새 파일 생성됨: {old_file_path}")
            
            # 백업 파일 삭제
            if old_file_exists and os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"백업 파일 삭제됨: {backup_path}")
            
            print(f"파일 수정 성공")
                
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")
            # 오류 발생 시 백업에서 복원
            if old_file_exists and 'backup_path' in locals() and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, old_file_path)
                    os.remove(backup_path)
                    print(f"오류 발생으로 백업에서 복원됨")
                except Exception as restore_error:
                    print(f"복원 중 추가 오류: {restore_error}")
            
            # 임시 파일 정리
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"임시 파일 삭제됨: {temp_file_path}")
                except Exception as temp_clean_error:
                    print(f"임시 파일 삭제 중 오류: {temp_clean_error}")
            
            return jsonify({'success': False, 'error': f'파일 저장 실패: {e}'}), 500
        
        # 6. 데이터 파일 업데이트
        try:
            data_path = os.path.join(DATA_FOLDER, 'data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
                print(f"data.json 파일이 없어 새로 생성합니다.")
                
            if main_category == 'music' and sub_category in ['ai', 'mr', 'live']:
                try:
                    # 데이터 구조 유효성 검사
                    if 'music' not in data:
                        print(f"music 카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data['music'] = {'ai': [], 'mr': [], 'live': []}
                        
                    if sub_category not in data['music']:
                        print(f"{sub_category} 서브카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data['music'][sub_category] = []
                    
                    # 기존 파일명 제거
                    if decoded_filename in data['music'][sub_category]:
                        data['music'][sub_category].remove(decoded_filename)
                        print(f"기존 파일명 '{decoded_filename}'을 data.json에서 제거")
                        
                    # 새 파일명 추가
                    if new_filename not in data['music'][sub_category]:
                        data['music'][sub_category].append(new_filename)
                        print(f"새 파일명 '{new_filename}'을 data.json에 추가")
                except Exception as e:
                    print(f"data.json 처리 중 오류: {e}")
                    print(f"현재 데이터 구조: {data}")
                    # 오류가 발생해도 계속 진행

            elif main_category in ['scores', 'videos']:
                try:
                    # 데이터 구조 유효성 검사
                    if main_category not in data:
                        print(f"{main_category} 카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data[main_category] = []
                        
                    # 기존 파일명 제거
                    if decoded_filename in data[main_category]:
                        data[main_category].remove(decoded_filename)
                        print(f"기존 파일명 '{decoded_filename}'을 data.json에서 제거")
                        
                    # 새 파일명 추가
                    if new_filename not in data[main_category]:
                        data[main_category].append(new_filename)
                        print(f"새 파일명 '{new_filename}'을 data.json에 추가")
                except Exception as e:
                    print(f"data.json {main_category} 처리 중 오류: {e}")
                    print(f"현재 데이터 구조: {data}")
                    # 오류가 발생해도 계속 진행
            
            # 데이터 저장
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"data.json 파일 업데이트 완료")
            
            # 최종 동기화
            sync_data_with_filesystem()
            
            # 파일 존재 확인
            final_path = new_file_path
            if os.path.exists(final_path):
                print(f"최종 확인: 파일이 정상적으로 존재함: {final_path}")
                final_size = os.path.getsize(final_path)
                print(f"최종 파일 크기: {final_size} 바이트")
            else:
                print(f"최종 확인: 파일이 존재하지 않음: {final_path} - 서버 측 오류 가능성 있음")
            
            print(f"==== 파일 수정 요청 완료 ====\n")
            
            # 응답에 파일명 정보 추가 (클라이언트가 파일명 변경을 인지할 수 있도록)
            filename_for_response = os.path.basename(old_file_path)
            return jsonify({
                'success': True, 
                'filename': filename_for_response,
                'original_filename': actual_old_filename,
                'message': '파일이 성공적으로 수정되었습니다.'
            })
        except Exception as e:
            print(f"데이터 업데이트 중 오류: {e}")
            # 파일은 이미 저장됐으므로 성공으로 처리하되 경고 추가
            return jsonify({
                'success': True, 
                'filename': new_filename, 
                'warning': f'파일은 저장되었으나 데이터 업데이트 중 오류가 발생했습니다: {e}'
            })
    except Exception as e:
        print(f"파일 수정 중 예상치 못한 오류: {e}")
        return jsonify({'success': False, 'error': f'예상치 못한 오류가 발생했습니다: {e}'}), 500

# 게시판 API 추가
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        posts = load_posts()
        return jsonify(posts)
    except Exception as e:
        print(f"게시글 목록 조회 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def add_post():
    try:
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            
        posts = load_posts()
        
        post_id = 1
        if posts:
            post_id = max(post['id'] for post in posts) + 1
            
        post = {
            'id': post_id,
            'title': request.form.get('title'),
            'content': request.form.get('content'),
            'author': user['name'],
            'author_id': user['id'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comments': [],
            'file': None
        }
        
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = custom_secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, 'posts', filename)
            os.makedirs(os.path.join(UPLOAD_FOLDER, 'posts'), exist_ok=True)
            file.save(file_path)
            post['file'] = filename
            
        posts.append(post)
        save_posts(posts)
        
        return jsonify({'success': True, 'post_id': post_id})
    except Exception as e:
        print(f"게시글 작성 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            
        posts = load_posts()
        post = next((p for p in posts if p['id'] == post_id), None)
        
        if not post:
            return jsonify({'error': '게시글을 찾을 수 없습니다.'}), 404
            
        if post['author_id'] != user['id'] and user['role'] != 'admin':
            return jsonify({'error': '게시글을 삭제할 권한이 없습니다.'}), 403
            
        if post['file']:
            file_path = os.path.join(UPLOAD_FOLDER, 'posts', post['file'])
            if os.path.exists(file_path):
                os.remove(file_path)
                
        posts.remove(post)
        save_posts(posts)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"게시글 삭제 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    try:
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            
        posts = load_posts()
        post = next((p for p in posts if p['id'] == post_id), None)
        
        if not post:
            return jsonify({'error': '게시글을 찾을 수 없습니다.'}), 404
            
        comment = {
            'id': len(post['comments']) + 1,
            'content': request.form.get('content'),
            'author': user['name'],
            'author_id': user['id'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        post['comments'].append(comment)
        save_posts(posts)
        
        return jsonify({'success': True, 'comment_id': comment['id']})
    except Exception as e:
        print(f"댓글 작성 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            
        posts = load_posts()
        post_index = next((i for i, p in enumerate(posts) if p['id'] == post_id), None)
        
        if post_index is None:
            return jsonify({'error': '게시글을 찾을 수 없습니다.'}), 404
            
        post = posts[post_index]
        
        # 관리자가 아니고 본인 글이 아닌 경우 수정 불가
        if post['author_id'] != user['id'] and user['role'] != 'admin':
            return jsonify({'error': '게시글을 수정할 권한이 없습니다.'}), 403
            
        # 게시글 내용 업데이트
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')
        post['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 새 파일이 있는 경우 처리
        if 'file' in request.files and request.files['file'].filename != '':
            # 기존 파일 삭제
            if post['file']:
                old_file_path = os.path.join(UPLOAD_FOLDER, 'posts', post['file'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # 새 파일 저장
            file = request.files['file']
            filename = custom_secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, 'posts', filename)
            os.makedirs(os.path.join(UPLOAD_FOLDER, 'posts'), exist_ok=True)
            file.save(file_path)
            post['file'] = filename
            
        # 변경된 게시글 저장
        posts[post_index] = post
        save_posts(posts)
        
        return jsonify({'success': True, 'post_id': post_id})
    except Exception as e:
        print(f"게시글 수정 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

# 회원가입 API 추가
@app.route('/api/register', methods=['POST'])
def register():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        
        if not all([username, password, name, email, phone]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400
            
        users = load_users()
        
        # 아이디 중복 확인
        if any(u['username'] == username for u in users):
            return jsonify({'error': '이미 사용 중인 아이디입니다.'}), 400
            
        # 새 사용자 ID 생성
        new_id = 1
        if users:
            new_id = max(u['id'] for u in users) + 1
            
        # 새 사용자 추가
        new_user = {
            'id': new_id,
            'username': username,
            'password': password,
            'name': name,
            'email': email,
            'phone': phone,
            'role': 'new',  # 기본 권한은 신입회원
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users.append(new_user)
        save_users(users)
        
        return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'})
    except Exception as e:
        print(f"회원가입 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-username', methods=['POST'])
def check_username():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        
        if not username:
            return jsonify({'error': '아이디를 입력해주세요.'}), 400
            
        users = load_users()
        
        if any(u['username'] == username for u in users):
            return jsonify({'error': '이미 사용 중인 아이디입니다.'}), 400
            
        return jsonify({'available': True})
    except Exception as e:
        print(f"아이디 확인 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500
        
# 파일 다운로드 경로 추가
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    try:
        # 경로 분리
        path_parts = filename.split('/')
        
        # 악보 파일에 대한 권한 확인 (scores 또는 scores/default 경로)
        if len(path_parts) > 0 and (
            path_parts[0] == 'scores' or 
            (len(path_parts) > 1 and path_parts[0] == 'scores' and path_parts[1] == 'default')
        ):
            # 로그인 여부 확인
            if 'user_id' not in session:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
                
            # 사용자 정보 확인
            users = load_users(); user = next((u for u in users if u['id'] == session['user_id']), None)
            if not user:
                return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            # 특별회원, 관리자만 다운로드 가능
            if user['role'] not in ['admin', 'special']:
                return jsonify({'error': '특별회원 및 관리자만 악보 파일을 다운로드할 수 있습니다.'}), 403
        # 음악 파일에 대한 권한 확인 (music/ai, music/mr, music/live)
        if len(path_parts) > 1 and path_parts[0] == 'music' and path_parts[1] in ['ai', 'mr', 'live']:
            if 'user_id' not in session:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
            users = load_users(); user = next((u for u in users if u['id'] == session['user_id']), None)
            if not user:
                return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            if user['role'] not in ['admin', 'special']:
                return jsonify({'error': '특별회원 및 관리자만 음악 파일을 다운로드할 수 있습니다.'}), 403
        
        if len(path_parts) > 1:
            # 마지막 부분은 파일 이름, 나머지는 디렉토리 경로
            directory = os.path.join(UPLOAD_FOLDER, *path_parts[:-1])
            file_name = path_parts[-1]
            print(f"수정된 파일 경로: {directory}/{file_name}")
            return send_from_directory(directory, file_name)
        else:
            return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error serving upload {filename}: {e}")
        return "File not found", 404

# URL에 파일 경로가 있는 경우를 위한 처리
@app.route('/music/<path:path>')
def serve_music(path):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'music'), path)

@app.route('/scores/<path:path>')
def serve_scores(path):
    try:
        # 로그인 여부 확인
        if 'user_id' not in session:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
            
        # 사용자 정보 확인
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 401
            
        # 일반회원과 신입회원은 악보 다운로드 불가
        if user['role'] == 'new':
            return jsonify({'error': '신입회원은 악보 파일을 다운로드할 수 없습니다.'}), 403
            
        # 관리자와 특별회원만 다운로드 가능
        return send_from_directory(os.path.join(UPLOAD_FOLDER, 'scores'), path)
    except Exception as e:
        print(f"악보 파일 제공 중 오류 발생: {e}")
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

@app.route('/videos/<path:path>')
def serve_videos(path):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'videos'), path)

# 사용자 관련 API 추가
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    try:
        # 요청한 사용자의 권한 확인
        user_id = session.get('user_id')
        users = load_users()
        
        # 사용자 존재 여부 확인
        current_user = next((u for u in users if u['id'] == user_id), None)
        if not current_user:
            return jsonify({'error': '인증되지 않은 사용자입니다.'}), 401
            
        # 관리자 권한 확인
        if current_user['role'] != 'admin':
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
            
        # 사용자 정보 반환 (비밀번호 제외)
        safe_users = []
        for user in users:
            safe_user = user.copy()
            if 'password' in safe_user:
                del safe_user['password']
            safe_users.append(safe_user)
            
        return jsonify(safe_users)
    except Exception as e:
        print(f"사용자 목록 조회 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        # 요청한 사용자의 권한 확인
        admin_id = session.get('user_id')
        users = load_users()
        
        # 관리자 존재 여부 확인
        admin = next((u for u in users if u['id'] == admin_id), None)
        if not admin or admin['role'] != 'admin':
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
            
        # 삭제할 사용자 확인
        user_to_delete = next((u for u in users if u['id'] == user_id), None)
        if not user_to_delete:
            return jsonify({'error': '존재하지 않는 사용자입니다.'}), 404
            
        # 관리자 계정 삭제 방지
        if user_to_delete['role'] == 'admin':
            return jsonify({'error': '관리자 계정은 삭제할 수 없습니다.'}), 403
            
        # 사용자 삭제
        users.remove(user_to_delete)
        save_users(users)
        
        return jsonify({'success': True, 'message': '사용자가 삭제되었습니다.'})
    except Exception as e:
        print(f"사용자 삭제 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@login_required
def update_user_role(user_id):
    try:
        # 요청 데이터 확인
        if not request.is_json:
            return jsonify({'error': '요청 형식이 올바르지 않습니다.'}), 400
            
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in USER_ROLES:
            return jsonify({'error': '올바르지 않은 역할입니다.'}), 400
            
        # 요청한 사용자의 권한 확인
        admin_id = session.get('user_id')
        users = load_users()
        
        # 관리자 존재 여부 확인
        admin = next((u for u in users if u['id'] == admin_id), None)
        if not admin or admin['role'] != 'admin':
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
            
        # 수정할 사용자 확인
        user_to_update = next((u for u in users if u['id'] == user_id), None)
        if not user_to_update:
            return jsonify({'error': '존재하지 않는 사용자입니다.'}), 404
            
        # 관리자 계정 수정 방지
        if user_to_update['role'] == 'admin':
            return jsonify({'error': '관리자 계정의 역할은 변경할 수 없습니다.'}), 403
            
        # 역할 업데이트
        user_to_update['role'] = new_role
        save_users(users)
        
        return jsonify({'success': True, 'message': '사용자 역할이 업데이트되었습니다.'})
    except Exception as e:
        print(f"사용자 역할 수정 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

# 공연 문의 API 추가
@app.route('/api/inquiries', methods=['POST'])
def submit_inquiry():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        event_type = data.get('event-type')
        date = data.get('date')
        location = data.get('location')
        message = data.get('message')
        
        if not all([name, email, phone, event_type, date, location, message]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400
            
        inquiries = load_inquiries()
        
        # 새 문의 ID 생성
        new_id = 1
        if inquiries:
            new_id = max(inq['id'] for inq in inquiries) + 1
            
        # 새 문의 추가
        new_inquiry = {
            'id': new_id,
            'name': name,
            'email': email,
            'phone': phone,
            'event_type': event_type,
            'date': date,
            'location': location,
            'message': message,
            'status': '접수됨',  # 문의 상태 (접수됨, 처리중, 완료)
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        inquiries.append(new_inquiry)
        save_inquiries(inquiries)
        
        return jsonify({'success': True, 'message': '문의가 접수되었습니다.'})
    except Exception as e:
        print(f"문의 접수 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

# 관리자용 문의 목록 API
@app.route('/api/inquiries', methods=['GET'])
@login_required
def get_inquiries():
    try:
        # 요청한 사용자의 권한 확인
        user_id = session.get('user_id')
        users = load_users()
        
        # 사용자 존재 여부 확인
        current_user = next((u for u in users if u['id'] == user_id), None)
        if not current_user:
            return jsonify({'error': '인증되지 않은 사용자입니다.'}), 401
            
        # 관리자/특별회원 권한 확인
        if current_user['role'] not in ['admin', 'special']:
            return jsonify({'error': '권한이 없습니다.'}), 403
            
        # 문의 목록 반환
        inquiries = load_inquiries()
        return jsonify(inquiries)
    except Exception as e:
        print(f"문의 목록 조회 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

# 문의 상태 업데이트 API
@app.route('/api/inquiries/<int:inquiry_id>/status', methods=['PUT'])
@login_required
def update_inquiry_status(inquiry_id):
    try:
        # 요청 데이터 확인
        if not request.is_json:
            return jsonify({'error': '요청 형식이 올바르지 않습니다.'}), 400
            
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['접수됨', '처리중', '완료']:
            return jsonify({'error': '올바르지 않은 상태입니다.'}), 400
            
        # 요청한 사용자의 권한 확인
        user_id = session.get('user_id')
        users = load_users()
        
        # 사용자 존재 여부 확인
        current_user = next((u for u in users if u['id'] == user_id), None)
        if not current_user:
            return jsonify({'error': '인증되지 않은 사용자입니다.'}), 401
            
        # 관리자/특별회원 권한 확인
        if current_user['role'] not in ['admin', 'special']:
            return jsonify({'error': '권한이 없습니다.'}), 403
            
        # 수정할 문의 확인
        inquiries = load_inquiries()
        inquiry_to_update = next((inq for inq in inquiries if inq['id'] == inquiry_id), None)
        if not inquiry_to_update:
            return jsonify({'error': '존재하지 않는 문의입니다.'}), 404
            
        # 상태 업데이트
        inquiry_to_update['status'] = new_status
        save_inquiries(inquiries)
        
        return jsonify({'success': True, 'message': '문의 상태가 업데이트되었습니다.'})
    except Exception as e:
        print(f"문의 상태 수정 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

# 문의 삭제 API
@app.route('/api/inquiries/<int:inquiry_id>', methods=['DELETE'])
@login_required
def delete_inquiry(inquiry_id):
    try:
        # 요청한 사용자의 권한 확인
        user_id = session.get('user_id')
        users = load_users()
        
        # 사용자 존재 여부 확인
        current_user = next((u for u in users if u['id'] == user_id), None)
        if not current_user:
            return jsonify({'error': '인증되지 않은 사용자입니다.'}), 401
            
        # 관리자/특별회원 권한 확인
        if current_user['role'] not in ['admin', 'special']:
            return jsonify({'error': '권한이 없습니다.'}), 403
            
        # 삭제할 문의 확인
        inquiries = load_inquiries()
        inquiry_to_delete = next((inq for inq in inquiries if inq['id'] == inquiry_id), None)
        if not inquiry_to_delete:
            return jsonify({'error': '존재하지 않는 문의입니다.'}), 404
            
        # 문의 삭제
        inquiries.remove(inquiry_to_delete)
        save_inquiries(inquiries)
        
        return jsonify({'success': True, 'message': '문의가 삭제되었습니다.'})
    except Exception as e:
        print(f"문의 삭제 중 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/rename-file/<path:category>/<path:filename>', methods=['POST'])
def rename_file(category, filename):
    try:
        print(f"\n==== 파일명 변경 요청 시작 ====")
        print(f"카테고리: {category}")
        print(f"원본 파일명(인코딩됨): {filename}")
        
        # 디버깅: 모든 요청 정보 출력
        print("==== 요청 디버깅 정보 ====")
        print(f"요청 메서드: {request.method}")
        print(f"요청 URL: {request.url}")
        print(f"요청 헤더: {dict(request.headers)}")
        print(f"요청 쿠키: {request.cookies}")
        print(f"요청 데이터: {request.data}")
        print(f"요청 폼: {request.form}")
        print(f"요청 JSON: {request.json if request.is_json else '비JSON 요청'}")
        print(f"요청 Content-Type: {request.content_type}")
        print(f"세션 정보: {session}")
        print(f"세션 키: {list(session.keys())}")
        print(f"user_id 존재 여부: {'user_id' in session}")
        print("==== 디버깅 정보 끝 ====")
        
        # 1. 사용자 권한 확인
        if 'user_id' not in session:
            print("세션에 user_id가 없습니다.")
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401
            
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            print(f"user_id={session['user_id']} 사용자를 찾을 수 없습니다.")
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
            
        if user['role'] != 'admin':
            print(f"사용자 {user['username']}의 권한이 부족합니다. 현재 권한: {user['role']}")
            return jsonify({'success': False, 'error': '관리자만 파일명을 변경할 수 있습니다.'}), 403
        
        print(f"사용자 인증 성공: {user['username']} (권한: {user['role']})")
        
        # 2. 요청 데이터 파싱 - 간소화된 로직
        if not request.is_json:
            print(f"JSON이 아닌 요청입니다: Content-Type={request.content_type}")
            return jsonify({'success': False, 'error': 'JSON 형식의 요청이 필요합니다.'}), 400
            
        data = request.get_json()
        print(f"파싱된 데이터: {data}")
        
        if not data or 'new_filename' not in data:
            print(f"new_filename 필드가 없습니다: {data}")
            return jsonify({'success': False, 'error': '새 파일명이 제공되지 않았습니다.'}), 400
            
        new_filename = data.get('new_filename')
        if not new_filename or new_filename.strip() == '':
            return jsonify({'success': False, 'error': '유효한 파일명을 입력해주세요.'}), 400
            
        # 파일명에 허용되지 않는 문자 확인
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in new_filename:
                return jsonify({'success': False, 'error': f'파일명에 "{char}" 문자를 사용할 수 없습니다.'}), 400
            
        # 확장자 유지 확인
        try:
            decoded_filename = urllib.parse.unquote(filename)
        except Exception as e:
            print(f"파일명 디코딩 오류: {e}")
            decoded_filename = filename  # 디코딩에 실패하면 원본 사용
            
        print(f"디코딩된 파일명: {decoded_filename}")
        
        # 확장자 추출 및 유지
        if '.' in decoded_filename and '.' not in new_filename:
            extension = decoded_filename.split('.')[-1]
            new_filename = f"{new_filename}.{extension}"
            print(f"확장자 추가된 새 파일명: {new_filename}")
            
        # 안전한 파일명으로 변환
        safe_new_filename = custom_secure_filename(new_filename)
        print(f"안전한 새 파일명: {safe_new_filename}")
        
        # 3. 파일 경로 설정
        category_parts = category.split('/')
        if len(category_parts) < 1 or category_parts[0] not in ['music', 'scores', 'videos']:
            return jsonify({'success': False, 'error': '잘못된 카테고리입니다.'}), 400
            
        main_category = category_parts[0]
        sub_category = category_parts[1] if len(category_parts) > 1 else None
        
        if sub_category:
            upload_dir = os.path.join(UPLOAD_FOLDER, main_category, sub_category)
        else:
            upload_dir = os.path.join(UPLOAD_FOLDER, main_category)
        
        print(f"업로드 디렉토리: {upload_dir}")
            
        # 디렉토리 존재 확인
        if not os.path.exists(upload_dir):
            print(f"디렉토리가 존재하지 않음: {upload_dir}")
            os.makedirs(upload_dir, exist_ok=True)
            return jsonify({'success': False, 'error': '지정된 카테고리가 존재하지 않습니다.'}), 404
            
        # 4. 기존 파일 찾기
        old_file_path = os.path.join(upload_dir, decoded_filename)
        if not os.path.exists(old_file_path):
            # 디렉토리 내 검색 시도
            found = False
            for file in os.listdir(upload_dir):
                if file.lower() == decoded_filename.lower():
                    old_file_path = os.path.join(upload_dir, file)
                    decoded_filename = file
                    found = True
                    break
                    
            if not found:
                return jsonify({'success': False, 'error': '변경할 파일을 찾을 수 없습니다.'}), 404
                
        new_file_path = os.path.join(upload_dir, safe_new_filename)
        print(f"기존 파일 경로: {old_file_path}")
        print(f"새 파일 경로: {new_file_path}")
        
        # 중복 파일명 확인
        if os.path.exists(new_file_path) and old_file_path != new_file_path:
            return jsonify({'success': False, 'error': '같은 이름의 파일이 이미 존재합니다.'}), 400
            
        # 5. 파일명 변경 실행
        try:
            # 기존 파일 확인
            if not os.path.exists(old_file_path):
                print(f"ERROR: 변경할 파일이 존재하지 않습니다: {old_file_path}")
                return jsonify({'success': False, 'error': '변경할 파일을 찾을 수 없습니다.'}), 404
                
            # 새 파일 경로 확인
            if os.path.exists(new_file_path) and old_file_path != new_file_path:
                print(f"ERROR: 같은 이름의 파일이 이미 존재합니다: {new_file_path}")
                return jsonify({'success': False, 'error': '같은 이름의 파일이 이미 존재합니다.'}), 400
            
            # 백업 생성
            backup_path = old_file_path + '.bak'
            print(f"백업 생성 시도: {backup_path}")
            shutil.copy2(old_file_path, backup_path)
            print(f"백업 생성 완료")
            
            try:
                # 파일명 변경 시도
                print(f"파일명 변경 시도: {old_file_path} → {new_file_path}")
                shutil.copy2(old_file_path, new_file_path)
                
                # 복사 성공 후 원본 확인
                if os.path.exists(new_file_path) and os.path.getsize(new_file_path) > 0:
                    print(f"새 파일 생성 확인: {new_file_path} ({os.path.getsize(new_file_path)} 바이트)")
                    # 원본 파일 삭제
                    os.remove(old_file_path)
                    print(f"기존 파일 삭제 완료: {old_file_path}")
                else:
                    raise Exception("새 파일이 올바르게 생성되지 않았습니다.")
                    
                print(f"파일명 변경 완료: {decoded_filename} → {safe_new_filename}")
            except Exception as rename_error:
                # 변경 중 오류 발생 시 복원
                print(f"파일명 변경 중 오류: {rename_error}")
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                    print(f"불완전한 새 파일 삭제: {new_file_path}")
                
                # 백업에서 원본 복원은 하지 않음 (원본이 아직 존재함)
                raise rename_error
                
            # 백업 삭제
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"백업 삭제 완료")
            
        except Exception as e:
            # 오류 발생 시 백업에서 복원
            print(f"파일명 변경 과정 중 오류: {e}")
            if not os.path.exists(old_file_path) and os.path.exists(backup_path):
                print(f"원본 파일이 손실됨, 백업에서 복원 시도")
                shutil.copy2(backup_path, old_file_path)
                print(f"백업에서 복원 완료: {old_file_path}")
                
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    print(f"사용된 백업 파일 삭제")
            
            return jsonify({'success': False, 'error': f'파일명 변경 중 오류가 발생했습니다: {e}'}), 500
        
        # 6. 데이터 파일 업데이트
        try:
            data_path = os.path.join(DATA_FOLDER, 'data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []}
                print(f"data.json 파일이 없어 새로 생성합니다.")
                
            if main_category == 'music' and sub_category in ['ai', 'mr', 'live']:
                try:
                    # 데이터 구조 유효성 검사
                    if 'music' not in data:
                        print(f"music 카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data['music'] = {'ai': [], 'mr': [], 'live': []}
                        
                    if sub_category not in data['music']:
                        print(f"{sub_category} 서브카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data['music'][sub_category] = []
                    
                    # 기존 파일명 제거
                    if decoded_filename in data['music'][sub_category]:
                        data['music'][sub_category].remove(decoded_filename)
                        print(f"기존 파일명 '{decoded_filename}'을 data.json에서 제거")
                        
                    # 새 파일명 추가
                    if safe_new_filename not in data['music'][sub_category]:
                        data['music'][sub_category].append(safe_new_filename)
                        print(f"새 파일명 '{safe_new_filename}'을 data.json에 추가")
                except Exception as e:
                    print(f"data.json 처리 중 오류: {e}")
                    print(f"현재 데이터 구조: {data}")
                    # 오류가 발생해도 계속 진행

            elif main_category in ['scores', 'videos']:
                try:
                    # 데이터 구조 유효성 검사
                    if main_category not in data:
                        print(f"{main_category} 카테고리가 data.json에 없습니다. 새로 생성합니다.")
                        data[main_category] = []
                        
                    # 기존 파일명 제거
                    if decoded_filename in data[main_category]:
                        data[main_category].remove(decoded_filename)
                        print(f"기존 파일명 '{decoded_filename}'을 data.json에서 제거")
                        
                    # 새 파일명 추가
                    if safe_new_filename not in data[main_category]:
                        data[main_category].append(safe_new_filename)
                        print(f"새 파일명 '{safe_new_filename}'을 data.json에 추가")
                except Exception as e:
                    print(f"data.json {main_category} 처리 중 오류: {e}")
                    print(f"현재 데이터 구조: {data}")
                    # 오류가 발생해도 계속 진행
                
            # 데이터 저장
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"data.json 파일 업데이트 완료")
        except Exception as e:
            print(f"데이터 업데이트 중 오류: {e}")
            # 파일 이름은 변경했지만 데이터 업데이트 실패시 경고 추가
            return jsonify({
                'success': True, 
                'filename': safe_new_filename, 
                'old_filename': decoded_filename,
                'warning': '파일명은 변경되었으나 데이터 업데이트 중 오류가 발생했습니다. 페이지를 새로고침해주세요.'
            })
            
        # 7. 동기화 및 최종 응답
        sync_data_with_filesystem()
        
        print(f"==== 파일명 변경 요청 완료 ====\n")
        return jsonify({
            'success': True, 
            'filename': safe_new_filename, 
            'old_filename': decoded_filename,
            'message': '파일명이 성공적으로 변경되었습니다.'
        })
        
    except Exception as e:
        print(f"파일명 변경 중 예상치 못한 오류: {e}")
        return jsonify({'success': False, 'error': f'파일명 변경 중 오류가 발생했습니다: {e}'}), 500

# 테스트용 파일명 변경 함수 - 내부용
@app.route('/test-rename-file', methods=['GET'])
def test_rename_file():
    """파일명 변경 기능 테스트를 위한 페이지"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>파일명 변경 테스트</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #4CAF50; }
            form { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            label { display: block; margin: 10px 0 5px; }
            input, select { padding: 8px; width: 100%; box-sizing: border-box; }
            button { margin-top: 15px; padding: 10px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            pre { background: #f1f1f1; padding: 10px; border-radius: 5px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>파일명 변경 테스트</h1>
        
        <form id="test-form">
            <div>
                <label for="category">카테고리:</label>
                <select id="category" required>
                    <option value="music/ai">AI 음악</option>
                    <option value="music/mr">MR 음악</option>
                    <option value="music/live">Live 음악</option>
                    <option value="scores">악보</option>
                    <option value="videos">동영상</option>
                </select>
            </div>
            
            <div>
                <label for="filename">현재 파일명:</label>
                <input type="text" id="filename" placeholder="변경할 파일의 이름" required>
            </div>
            
            <div>
                <label for="new-filename">새 파일명:</label>
                <input type="text" id="new-filename" placeholder="새 파일명" required>
            </div>
            
            <button type="submit">파일명 변경 테스트</button>
        </form>
        
        <div>
            <h3>결과:</h3>
            <pre id="result">여기에 결과가 표시됩니다.</pre>
        </div>
        
        <script>
            document.getElementById('test-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const category = document.getElementById('category').value;
                const filename = document.getElementById('filename').value;
                const newFilename = document.getElementById('new-filename').value;
                const resultElement = document.getElementById('result');
                
                // 로딩 상태 표시
                resultElement.textContent = "요청 전송 중...";
                
                try {
                    // URL 인코딩
                    const encodedFilename = encodeURIComponent(filename);
                    const requestUrl = `/rename-file/${category}/${encodedFilename}`;
                    
                    // API 요청
                    const response = await fetch(requestUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            new_filename: newFilename
                        })
                    });
                    
                    // 텍스트 응답 확인
                    const responseText = await response.text();
                    console.log('응답 원문:', responseText);
                    
                    // JSON 파싱 시도
                    try {
                        const data = JSON.parse(responseText);
                        
                        resultElement.textContent = `상태 코드: ${response.status}\n` + 
                                                 JSON.stringify(data, null, 2);
                    } catch (parseError) {
                        resultElement.textContent = `상태 코드: ${response.status}\n` + 
                                                 `JSON 파싱 오류: ${parseError.message}\n\n` + 
                                                 responseText;
                    }
                } catch (error) {
                    resultElement.textContent = `오류 발생: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    '''

# 일정 관련 함수
def load_schedules():
    try:
        if os.path.exists(SCHEDULES_FILE):
            with open(SCHEDULES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_schedules(schedules):
    try:
        with open(SCHEDULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"일정 데이터 저장 중 오류 발생: {e}")
        return False

# 일정 관리 API
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    try:
        schedules = load_schedules()
        return jsonify({'success': True, 'schedules': schedules})
    except Exception as e:
        print(f"일정 목록 조회 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules', methods=['POST'])
@login_required
def add_schedule():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': '요청 형식이 올바르지 않습니다.'}), 400
            
        data = request.get_json()
        
        # 필수 필드 확인
        required_fields = ['title', 'type', 'date', 'time', 'location']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다.'}), 400
        
        # 유형 확인
        valid_types = ['practice', 'performance', 'meeting']
        if data['type'] not in valid_types:
            return jsonify({'success': False, 'error': '유효하지 않은 일정 유형입니다.'}), 400
        
        # 사용자 정보 가져오기
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
        
        # 일정 목록 로드
        schedules = load_schedules()
        
        # 새 일정 ID
        schedule_id = str(uuid.uuid4())
        
        # 새 일정 생성
        new_schedule = {
            'id': schedule_id,
            'title': data['title'],
            'type': data['type'],
            'date': data['date'],
            'time': data['time'],
            'location': data['location'],
            'description': data.get('description', ''),
            'created_by': user['id'],
            'created_by_name': user['name'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 일정 추가
        schedules.append(new_schedule)
        save_schedules(schedules)
        
        return jsonify({
            'success': True, 
            'message': '일정이 추가되었습니다.',
            'schedule': new_schedule
        })
    except Exception as e:
        print(f"일정 추가 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    try:
        schedules = load_schedules()
        schedule = next((s for s in schedules if s['id'] == schedule_id), None)
        
        if not schedule:
            return jsonify({'success': False, 'error': '일정을 찾을 수 없습니다.'}), 404
            
        return jsonify({'success': True, 'schedule': schedule})
    except Exception as e:
        print(f"일정 조회 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules/<schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': '요청 형식이 올바르지 않습니다.'}), 400
            
        data = request.get_json()
        
        # 필수 필드 확인
        required_fields = ['title', 'type', 'date', 'time', 'location']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다.'}), 400
        
        # 유형 확인
        valid_types = ['practice', 'performance', 'meeting']
        if data['type'] not in valid_types:
            return jsonify({'success': False, 'error': '유효하지 않은 일정 유형입니다.'}), 400
        
        # 사용자 정보 가져오기
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
        
        # 일정 목록 로드
        schedules = load_schedules()
        
        # 일정 찾기
        schedule_index = next((i for i, s in enumerate(schedules) if s['id'] == schedule_id), None)
        
        if schedule_index is None:
            return jsonify({'success': False, 'error': '일정을 찾을 수 없습니다.'}), 404
            
        schedule = schedules[schedule_index]
        
        # 일정 수정 권한 확인 (관리자 또는 작성자만 수정 가능)
        if user['role'] != 'admin' and schedule['created_by'] != user['id']:
            return jsonify({'success': False, 'error': '일정을 수정할 권한이 없습니다.'}), 403
            
        # 일정 업데이트
        schedule.update({
            'title': data['title'],
            'type': data['type'],
            'date': data['date'],
            'time': data['time'],
            'location': data['location'],
            'description': data.get('description', ''),
            'updated_by': user['id'],
            'updated_by_name': user['name'],
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 일정 저장
        schedules[schedule_index] = schedule
        save_schedules(schedules)
        
        return jsonify({
            'success': True, 
            'message': '일정이 수정되었습니다.',
            'schedule': schedule
        })
    except Exception as e:
        print(f"일정 수정 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules/<schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    try:
        # 사용자 정보 가져오기
        users = load_users()
        user = next((u for u in users if u['id'] == session['user_id']), None)
        
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 401
        
        # 일정 목록 로드
        schedules = load_schedules()
        
        # 일정 찾기
        schedule = next((s for s in schedules if s['id'] == schedule_id), None)
        
        if not schedule:
            return jsonify({'success': False, 'error': '일정을 찾을 수 없습니다.'}), 404
            
        # 일정 삭제 권한 확인 (관리자 또는 작성자만 삭제 가능)
        if user['role'] != 'admin' and schedule['created_by'] != user['id']:
            return jsonify({'success': False, 'error': '일정을 삭제할 권한이 없습니다.'}), 403
            
        # 일정 삭제
        schedules.remove(schedule)
        save_schedules(schedules)
        
        return jsonify({
            'success': True, 
            'message': '일정이 삭제되었습니다.'
        })
    except Exception as e:
        print(f"일정 삭제 중 오류 발생: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 메뉴 권한 관련 API 추가
@app.route('/api/menu-permissions', methods=['GET'])
@login_required
def get_menu_permissions():
    try:
        return jsonify({
            'menu_items': MENU_ITEMS,
            'role_permissions': MENU_PERMISSIONS,
            'user_roles': USER_ROLES
        })
    except Exception as e:
        print(f"메뉴 권한 정보 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu-permissions/update', methods=['POST'])
@login_required
def update_menu_permissions():
    try:
        # 관리자 권한 확인
        user_id = session.get('user_id')
        users = load_users()
        current_user = next((u for u in users if u['id'] == user_id), None)
        
        if not current_user or current_user['role'] != 'admin':
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
        # 요청 데이터 확인
        data = request.get_json()
        if not data or 'permissions' not in data:
            return jsonify({'error': '유효하지 않은 요청입니다.'}), 400
        
        new_permissions = data['permissions']
        
        # 권한 유효성 검사 - 모든 역할에 대해 최소한 '소개'는 접근 가능하도록 함
        for role, menus in new_permissions.items():
            if role not in USER_ROLES:
                return jsonify({'error': f'유효하지 않은 역할입니다: {role}'}), 400
            if not menus or 'about' not in menus:
                return jsonify({'error': '모든 역할은 최소한 소개 페이지에 접근할 수 있어야 합니다.'}), 400
        
        # 전역 변수 업데이트 (서버 재시작 전까지 유지)
        global MENU_PERMISSIONS
        MENU_PERMISSIONS = new_permissions
        
        # 설정 파일에 저장 (서버 재시작 후에도 유지)
        menu_config_file = os.path.join(DATA_FOLDER, 'menu_config.json')
        with open(menu_config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'menu_permissions': MENU_PERMISSIONS
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '메뉴 권한이 업데이트되었습니다.'})
    except Exception as e:
        print(f"메뉴 권한 업데이트 오류: {e}")
        return jsonify({'error': str(e)}), 500

# 서버 시작 시 메뉴 설정 불러오기
def load_menu_config():
    try:
        menu_config_file = os.path.join(DATA_FOLDER, 'menu_config.json')
        if os.path.exists(menu_config_file):
            with open(menu_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                global MENU_PERMISSIONS
                MENU_PERMISSIONS = config.get('menu_permissions', MENU_PERMISSIONS)
                print("메뉴 설정을 불러왔습니다.")
    except Exception as e:
        print(f"메뉴 설정 불러오기 실패: {e}")

# 서버 시작 시 설정 불러오기
load_menu_config()

# 비밀번호 재설정 - 인증 코드 발송
@app.route('/api/send-verification-code', methods=['POST'])
def send_verification_code():
    try:
        data = request.form
        username = data.get('username')
        email = data.get('email')
        
        print(f"비밀번호 재설정 인증 코드 요청 - 이메일: {email}, 아이디(옵션): {username}")
        
        if not email:
            return jsonify({'error': '이메일을 입력해주세요.'}), 400
        
        # 사용자 확인 (이메일만으로 확인)
        users = load_users()
        matching_users = []
        
        for u in users:
            if u.get('email') == email:
                matching_users.append(u)
        
        if not matching_users:
            return jsonify({'error': '입력한 이메일로 등록된 사용자를 찾을 수 없습니다.'}), 404
        
        # 인증 코드 생성
        verification_code = generate_verification_code()
        print(f"생성된 인증 코드: {verification_code}")
        
        # 인증 코드 저장 (실제 서비스에서는 데이터베이스나 캐시에 저장)
        if 'verification_codes' not in session:
            session['verification_codes'] = {}
        
        # 이메일을 키로 사용
        session['verification_codes'][email] = {
            'code': verification_code,
            'created_at': datetime.now().timestamp(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).timestamp(),
            'matching_users': [{'username': u['username'], 'email': u['email']} for u in matching_users]
        }
        
        # 실제 이메일 전송
        email_subject = "[셀라 합창단] 비밀번호 재설정 인증번호"
        email_body = f"""안녕하세요.

셀라 합창단 웹사이트 비밀번호 재설정을 위한 인증번호입니다.

인증번호: {verification_code}

이 인증번호는 10분 동안만 유효합니다.
본인이 요청하지 않았다면 이 이메일을 무시하셔도 됩니다.

감사합니다.
셀라 합창단 관리자
"""
        
        # 이메일 전송 시도
        email_sent = send_email(email, email_subject, email_body)
        
        if email_sent:
            return jsonify({'message': '인증 번호가 이메일로 전송되었습니다.'}), 200
        else:
            # 이메일 전송 실패시 인증 코드를 응답에 포함 (테스트용, 실제 서비스에서는 제거)
            return jsonify({
                'message': '이메일 서버 연결에 실패했습니다. 테스트를 위해 인증 코드를 제공합니다.',
                'verification_code': verification_code
            }), 200
        
    except Exception as e:
        print(f"인증 코드 전송 중 오류 발생: {str(e)}")
        return jsonify({'error': f'인증 코드 전송 중 오류가 발생했습니다: {str(e)}'}), 500

# 비밀번호 재설정 - 인증 코드 확인
@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    try:
        data = request.form
        username = data.get('username')
        email = data.get('email')
        code = data.get('code')
        
        print(f"인증 코드 확인 요청 - 이메일: {email}, 아이디(옵션): {username}, 코드: {code}")
        
        if not code:
            return jsonify({'error': '인증 번호를 입력해주세요.'}), 400
        elif not email:
            return jsonify({'error': '이메일 정보가 누락되었습니다. 처음부터 다시 시도해주세요.'}), 400
        
        # 인증 코드 확인
        verification_codes = session.get('verification_codes', {})
        user_verification = verification_codes.get(email)
        
        if not user_verification:
            return jsonify({'error': '인증 코드가 발급되지 않았습니다. 인증번호 받기를 다시 클릭해주세요.'}), 404
        
        # 인증 코드 만료 확인
        now = datetime.now().timestamp()
        if now > user_verification['expires_at']:
            # 만료된 인증 코드 삭제
            del verification_codes[email]
            session['verification_codes'] = verification_codes
            return jsonify({'error': '인증 코드가 만료되었습니다. 인증번호 받기를 다시 클릭해주세요.'}), 400
        
        # 인증 코드 일치 확인
        if user_verification['code'] != code:
            return jsonify({'error': '인증 코드가 일치하지 않습니다. 다시 확인해주세요.'}), 400
        
        # 인증 완료 표시
        user_verification['verified'] = True
        session['verification_codes'] = verification_codes
        
        # 해당 이메일에 대한 사용자 목록 반환
        return jsonify({
            'message': '인증 코드가 확인되었습니다.',
            'matching_users': user_verification.get('matching_users', [])
        }), 200
        
    except Exception as e:
        print(f"인증 코드 확인 중 오류 발생: {str(e)}")
        return jsonify({'error': f'인증 코드 확인 중 오류가 발생했습니다: {str(e)}'}), 500

# 비밀번호 재설정 - 새 비밀번호 설정
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.form
        username = data.get('username')
        email = data.get('email')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        print(f"비밀번호 재설정 요청 - 사용자: {username}, 이메일: {email}")
        
        if not username:
            return jsonify({'error': '아이디를 입력해주세요.'}), 400
        elif not email:
            return jsonify({'error': '이메일 정보가 유효하지 않습니다. 처음부터 다시 시도해주세요.'}), 400
        elif not new_password or not confirm_password:
            return jsonify({'error': '새 비밀번호와 확인 비밀번호를 모두 입력해주세요.'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': '새 비밀번호와 확인 비밀번호가 일치하지 않습니다. 다시 확인해주세요.'}), 400
        
        # 인증 여부 확인
        verification_codes = session.get('verification_codes', {})
        user_verification = verification_codes.get(email)
        
        if not user_verification or not user_verification.get('verified'):
            return jsonify({'error': '이메일 인증이 완료되지 않았습니다. 처음부터 인증 과정을 다시 진행해주세요.'}), 401
        
        # 사용자 정보 업데이트
        users = load_users()
        user_updated = False
        
        for user in users:
            if user['username'] == username and user.get('email') == email:
                user['password'] = new_password
                user_updated = True
                break
        
        if not user_updated:
            return jsonify({'error': '해당 아이디와 이메일이 일치하는 사용자를 찾을 수 없습니다. 다시 확인해주세요.'}), 404
        
        # 사용자 정보 저장
        save_users(users)
        
        # 인증 정보 삭제
        del verification_codes[email]
        session['verification_codes'] = verification_codes
        
        return jsonify({'message': '비밀번호가 성공적으로 재설정되었습니다. 새 비밀번호로 로그인해주세요.'}), 200
        
    except Exception as e:
        print(f"비밀번호 재설정 중 오류 발생: {str(e)}")
        return jsonify({'error': f'비밀번호 재설정 중 오류가 발생했습니다: {str(e)}'}), 500

# 비밀번호 변경 - 사용자 검증 (로그인된 사용자가 비밀번호 변경시)
@app.route('/api/verify-user', methods=['POST'])
def verify_user():
    try:
        data = request.form
        username = data.get('username')
        current_password = data.get('current_password')
        
        print(f"사용자 검증 요청 - 사용자: {username}")
        
        if not username:
            return jsonify({'error': '아이디를 입력해주세요.'}), 400
        elif not current_password:
            return jsonify({'error': '현재 비밀번호를 입력해주세요.'}), 400
        
        # 사용자 확인
        users = load_users()
        user = None
        
        for u in users:
            if u['username'] == username and u['password'] == current_password:
                user = u
                break
        
        if not user:
            return jsonify({'error': '아이디 또는 비밀번호가 일치하지 않습니다.'}), 401
        
        return jsonify({'message': '사용자 확인이 완료되었습니다.'}), 200
        
    except Exception as e:
        print(f"사용자 검증 중 오류 발생: {str(e)}")
        return jsonify({'error': f'사용자 검증 중 오류가 발생했습니다: {str(e)}'}), 500

# 비밀번호 변경 - 새 비밀번호 설정 (로그인된 사용자가 비밀번호 변경시)
@app.route('/api/change-password', methods=['POST'])
def change_password():
    try:
        data = request.form
        username = data.get('username')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        print(f"비밀번호 변경 요청 - 사용자: {username}")
        
        if not username:
            return jsonify({'error': '아이디 정보가 유효하지 않습니다. 처음부터 다시 시도해주세요.'}), 400
        elif not new_password or not confirm_password:
            return jsonify({'error': '새 비밀번호와 확인 비밀번호를 모두 입력해주세요.'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': '새 비밀번호와 확인 비밀번호가 일치하지 않습니다. 다시 확인해주세요.'}), 400
        
        # 사용자 정보 업데이트
        users = load_users()
        user_updated = False
        
        for user in users:
            if user['username'] == username:
                user['password'] = new_password
                user_updated = True
                break
        
        if not user_updated:
            return jsonify({'error': '해당 아이디를 가진 사용자를 찾을 수 없습니다.'}), 404
        
        # 사용자 정보 저장
        save_users(users)
        
        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인해주세요.'}), 200
        
    except Exception as e:
        print(f"비밀번호 변경 중 오류 발생: {str(e)}")
        return jsonify({'error': f'비밀번호 변경 중 오류가 발생했습니다: {str(e)}'}), 500

# 이메일 전송 기능
def send_email(recipient, subject, body):
    try:
        # 이메일 서버 설정 (Gmail 예시)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "selahensemble1@gmail.com"  # 실제 발신용 이메일 계정으로 변경
        smtp_password = "앱 비밀번호"  # Gmail의 앱 비밀번호를 입력해야 함
        
        # 이메일 메시지 생성
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = recipient
        message["Subject"] = subject
        
        # 이메일 내용 추가
        message.attach(MIMEText(body, "plain"))
        
        # SMTP 서버 연결 및 이메일 전송
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # TLS 보안 연결
        server.login(smtp_username, smtp_password)
        server.send_message(message)
        server.quit()
        
        print(f"이메일이 성공적으로 전송되었습니다: {recipient}")
        return True
    except Exception as e:
        print(f"이메일 전송 중 오류 발생: {str(e)}")
        return False

import os
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))