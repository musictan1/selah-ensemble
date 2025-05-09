import os
import json
from flask import Flask, render_template, request, session, jsonify, send_from_directory
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# 세션 설정
app.config['SECRET_KEY'] = 'test-session-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')

# Session 초기화
Session(app)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/test-session', methods=['GET'])
def test_session():
    """세션 테스트 엔드포인트"""
    try:
        # 세션에 user_id 설정 (로그인 시뮬레이션)
        if 'user_id' not in session:
            session['user_id'] = 1
            session['username'] = 'admin'
            session['role'] = 'admin'
        
        print("현재 세션 데이터:", dict(session))
        
        return jsonify({
            'success': True,
            'session': dict(session),
            'cookies': dict(request.cookies)
        })
    except Exception as e:
        print(f"세션 테스트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rename-test', methods=['POST'])
def rename_test():
    """파일명 변경 API 테스트"""
    try:
        # 세션 확인
        if 'user_id' not in session:
            print("세션에 user_id가 없음")
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401
        
        print("세션 데이터:", dict(session))
        print("사용자 ID:", session.get('user_id'))
        print("사용자 역할:", session.get('role'))
        
        # JSON 요청 확인
        print("요청 헤더:", dict(request.headers))
        print("Content-Type:", request.content_type)
        print("요청 데이터 (raw):", request.data)
        
        # JSON 파싱 처리
        try:
            if request.is_json:
                data = request.get_json()
                print("JSON 파싱 결과:", data)
            elif request.data:
                # 수동 파싱
                data = json.loads(request.data)
                print("수동 JSON 파싱 결과:", data)
            else:
                print("요청 데이터 없음")
                return jsonify({'success': False, 'error': '데이터가 없습니다.'}), 400
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return jsonify({'success': False, 'error': f'잘못된 JSON 형식: {e}'}), 400
            
        # 새 파일명 확인
        if not data or 'new_filename' not in data:
            print("새 파일명이 없음:", data)
            return jsonify({'success': False, 'error': '새 파일명이 제공되지 않았습니다.'}), 400
            
        new_filename = data['new_filename']
        if not new_filename or not new_filename.strip():
            return jsonify({'success': False, 'error': '빈 파일명은 사용할 수 없습니다.'}), 400
            
        # 성공 응답
        return jsonify({
            'success': True, 
            'filename': new_filename,
            'message': '파일명이 성공적으로 변경되었습니다.'
        })
    except Exception as e:
        print(f"파일명 변경 테스트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

if __name__ == '__main__':
    # 필요한 디렉토리 생성
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 테스트 HTML 파일 생성
    with open('templates/test.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>파일명 변경 테스트</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>파일명 변경 API 테스트</h1>
    
    <div>
        <h2>세션 테스트</h2>
        <button id="test-session">세션 확인</button>
        <pre id="session-result"></pre>
    </div>
    
    <div>
        <h2>파일명 변경 테스트</h2>
        <input type="text" id="filename" placeholder="새 파일명" value="test-file.mp3">
        <button id="rename-test">파일명 변경 요청</button>
        <pre id="rename-result"></pre>
    </div>
    
    <script>
        document.getElementById('test-session').addEventListener('click', async () => {
            try {
                const response = await fetch('/test-session', {
                    method: 'GET',
                    credentials: 'include'
                });
                const result = await response.json();
                document.getElementById('session-result').innerHTML = 
                    `<span class="${response.ok ? 'success' : 'error'}">
                        ${JSON.stringify(result, null, 2)}
                    </span>`;
            } catch (error) {
                document.getElementById('session-result').innerHTML = 
                    `<span class="error">오류: ${error.message}</span>`;
            }
        });
        
        document.getElementById('rename-test').addEventListener('click', async () => {
            try {
                const filename = document.getElementById('filename').value;
                const requestData = { new_filename: filename };
                
                console.log('요청 데이터:', requestData);
                
                const response = await fetch('/rename-test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify(requestData)
                });
                
                // 응답 텍스트 먼저 확인
                const text = await response.text();
                console.log('응답 원본:', text);
                
                // JSON 파싱 시도
                let result;
                try {
                    result = JSON.parse(text);
                } catch (e) {
                    result = { success: false, error: '응답을 파싱할 수 없습니다: ' + e.message };
                }
                
                document.getElementById('rename-result').innerHTML = 
                    `<span class="${response.ok ? 'success' : 'error'}">
                        상태 코드: ${response.status}<br>
                        ${JSON.stringify(result, null, 2)}
                    </span>`;
            } catch (error) {
                document.getElementById('rename-result').innerHTML = 
                    `<span class="error">오류: ${error.message}</span>`;
            }
        });
    </script>
</body>
</html>
        ''')
    
    # 서버 실행
    app.run(host='0.0.0.0', port=5001, debug=True) 