import json
import os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'debug-secret-key'

@app.route('/test-session', methods=['GET'])
def test_session():
    """세션 상태를 확인하는 엔드포인트"""
    session_data = dict(session)
    print("현재 세션 데이터:", session_data)
    
    # 세션에 테스트 데이터 추가
    if 'test_count' not in session:
        session['test_count'] = 1
    else:
        session['test_count'] += 1
        
    return jsonify({
        'session_data': session_data,
        'test_count': session['test_count'],
        'cookies': dict(request.cookies),
        'session_keys': list(session.keys())
    })

@app.route('/test-json', methods=['POST'])
def test_json():
    """JSON 요청 처리를 테스트하는 엔드포인트"""
    print("요청 헤더:", dict(request.headers))
    print("Content-Type:", request.content_type)
    print("요청 메서드:", request.method)
    
    try:
        # JSON 파싱 시도
        if request.is_json:
            data = request.get_json()
            print("파싱된 JSON 데이터:", data)
            return jsonify({
                'success': True,
                'method': 'get_json',
                'received_data': data
            })
        else:
            # 직접 파싱 시도
            print("Raw 데이터:", request.data)
            if request.data:
                try:
                    data = json.loads(request.data)
                    print("수동 파싱 JSON 데이터:", data)
                    return jsonify({
                        'success': True,
                        'method': 'manual_parse',
                        'received_data': data
                    })
                except json.JSONDecodeError as e:
                    print("JSON 파싱 오류:", e)
                    return jsonify({
                        'success': False,
                        'error': f'JSON 파싱 오류: {str(e)}',
                        'raw_data': request.data.decode('utf-8', errors='replace')
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
    except Exception as e:
        print("요청 처리 중 예외 발생:", e)
        return jsonify({
            'success': False,
            'error': f'예외 발생: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 