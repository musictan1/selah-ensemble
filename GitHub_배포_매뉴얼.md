# 셀라앙상블 찬양단 - GitHub 배포 매뉴얼

## 📋 개요
GitHub을 통한 자동 배포 방법을 설명합니다.

## 🎯 GitHub 저장소 정보
- **저장소**: https://github.com/musictan1/selah-ensemble.git
- **브랜치**: master

## 🚀 배포 방법

### 방법 1: Netlify 배포 (추천)

#### 1.1 Netlify 설정
1. [Netlify](https://netlify.com) 로그인
2. "New site from Git" 클릭
3. GitHub 선택 → `musictan1/selah-ensemble` 저장소 선택
4. **Build settings**:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.` (또는 `public` 폴더)
5. "Deploy site" 클릭

#### 1.2 업데이트 방법
```bash
# 로컬에서 변경사항 커밋
git add .
git commit -m "음악 업로드 기능 수정"
git push origin master

# Netlify에서 자동 배포됨
```

### 방법 2: Vercel 배포

#### 2.1 Vercel 설정
1. [Vercel](https://vercel.com) 로그인
2. "New Project" 클릭
3. GitHub 저장소 import
4. **Framework Preset**: Other
5. **Build Command**: `pip install -r requirements.txt && python app.py`
6. "Deploy" 클릭

#### 2.2 업데이트 방법
```bash
git add .
git commit -m "업데이트"
git push origin master
# Vercel에서 자동 배포
```

### 방법 3: Railway 배포

#### 3.1 Railway 설정
1. [Railway](https://railway.app) 로그인
2. "New Project" → "Deploy from GitHub repo"
3. `musictan1/selah-ensemble` 선택
4. **Environment Variables** 설정:
   - `FLASK_ENV`: production
   - `PORT`: 5000

#### 3.2 업데이트 방법
```bash
git add .
git commit -m "업데이트"
git push origin master
# Railway에서 자동 배포
```

## 📁 배포할 파일들

### 핵심 파일들
- `app.py` - Flask 서버
- `music.html` - 음악 페이지
- `admin.html` - 관리자 페이지
- `requirements.txt` - Python 패키지

### 데이터 파일들 (선택사항)
- `data/` 폴더 - 사용자 및 설정 데이터
- `uploads/` 폴더 - 업로드된 파일들

## ⚙️ 환경 설정

### requirements.txt 확인
```
Flask==2.3.3
Werkzeug==2.3.7
```

### Procfile 생성 (Heroku용)
```
web: python app.py
```

## 🔧 문제 해결

### 1. 배포 실패 시
```bash
# 로컬에서 테스트
python app.py
# 오류 확인 후 수정
```

### 2. 환경 변수 설정
- Netlify/Vercel/Railway 대시보드에서 설정
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`

### 3. 데이터베이스 연결
- 클라우드 데이터베이스 사용 권장
- SQLite 대신 PostgreSQL/MySQL

## 📞 지원
- **Netlify**: 대시보드에서 로그 확인
- **Vercel**: Functions 로그 확인
- **Railway**: Application 로그 확인

## 🎯 현재 권장 방법
**Netlify**를 통한 배포를 권장합니다:
1. 무료 플랜 제공
2. 자동 배포
3. SSL 인증서 자동 제공
4. 사용자 친화적 인터페이스 