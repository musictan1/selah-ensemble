#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 데이터 복구 및 검증 도구
모바일에서 회원가입한 사용자들이 사라지는 문제를 해결하기 위한 도구
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# 설정
DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
BACKUP_FOLDER = os.path.join(DATA_FOLDER, 'backups')

def load_users():
    """사용자 데이터 로드"""
    try:
        if not os.path.exists(USERS_FILE):
            print(f"사용자 파일이 존재하지 않습니다: {USERS_FILE}")
            return []
            
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return users if isinstance(users, list) else []
    except Exception as e:
        print(f"사용자 데이터 로드 중 오류 발생: {e}")
        return []

def save_users(users):
    """사용자 데이터 저장"""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        
        # 백업 생성
        if os.path.exists(USERS_FILE):
            backup_path = USERS_FILE + '.bak.' + datetime.now().strftime('%Y%m%d%H%M%S')
            shutil.copy2(USERS_FILE, backup_path)
            print(f"백업 생성: {backup_path}")
        
        # 임시 파일에 저장
        temp_file = USERS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # 원자적 이동
        os.replace(temp_file, USERS_FILE)
        print(f"사용자 데이터 저장 완료: {len(users)}명")
        
    except Exception as e:
        print(f"사용자 데이터 저장 중 오류 발생: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

def validate_user_data(user):
    """사용자 데이터 유효성 검사"""
    required_fields = ['id', 'username', 'password', 'name', 'email', 'phone', 'role', 'created_at']
    
    for field in required_fields:
        if field not in user:
            print(f"필수 필드 누락: {field}")
            return False
    
    if not user['username'] or not user['password'] or not user['name']:
        print(f"기본 정보 누락: {user.get('username', 'N/A')}")
        return False
    
    return True

def fix_user_data():
    """사용자 데이터 복구"""
    print("=== 사용자 데이터 복구 시작 ===")
    
    # 현재 사용자 데이터 로드
    users = load_users()
    print(f"현재 사용자 수: {len(users)}")
    
    # 백업 폴더 생성
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    
    # 백업 파일들 확인
    backup_files = []
    for file in os.listdir(DATA_FOLDER):
        if file.startswith('users.json.bak.'):
            backup_files.append(os.path.join(DATA_FOLDER, file))
    
    if backup_files:
        print(f"발견된 백업 파일들: {len(backup_files)}개")
        for backup in sorted(backup_files, reverse=True):
            print(f"  - {backup}")
    
    # 백업에서 누락된 사용자 복구
    recovered_users = []
    
    for backup_file in backup_files:
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_users = json.load(f)
            
            print(f"\n백업 파일 검사: {backup_file}")
            print(f"백업 사용자 수: {len(backup_users)}")
            
            for backup_user in backup_users:
                # 현재 사용자 목록에 없는 사용자인지 확인
                if not any(u['username'] == backup_user['username'] for u in users):
                    if validate_user_data(backup_user):
                        recovered_users.append(backup_user)
                        print(f"복구된 사용자: {backup_user['username']} ({backup_user['name']})")
                    else:
                        print(f"유효하지 않은 사용자 데이터: {backup_user.get('username', 'N/A')}")
        
        except Exception as e:
            print(f"백업 파일 읽기 실패: {backup_file} - {e}")
    
    # 복구된 사용자들을 현재 목록에 추가
    if recovered_users:
        print(f"\n총 {len(recovered_users)}명의 사용자를 복구했습니다.")
        
        # ID 재할당
        max_id = max(u['id'] for u in users) if users else 0
        for user in recovered_users:
            max_id += 1
            user['id'] = max_id
            user['recovered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        users.extend(recovered_users)
        save_users(users)
        
        print("복구 완료!")
    else:
        print("복구할 사용자가 없습니다.")
    
    return users

def check_user_consistency():
    """사용자 데이터 일관성 검사"""
    print("\n=== 사용자 데이터 일관성 검사 ===")
    
    users = load_users()
    
    # 중복 사용자명 검사
    usernames = [u['username'] for u in users]
    duplicates = [name for name in set(usernames) if usernames.count(name) > 1]
    
    if duplicates:
        print(f"중복 사용자명 발견: {duplicates}")
        for dup in duplicates:
            dup_users = [u for u in users if u['username'] == dup]
            print(f"  {dup}: {len(dup_users)}개")
    else:
        print("중복 사용자명 없음")
    
    # 유효성 검사
    invalid_users = []
    for user in users:
        if not validate_user_data(user):
            invalid_users.append(user)
    
    if invalid_users:
        print(f"유효하지 않은 사용자 데이터: {len(invalid_users)}개")
        for user in invalid_users:
            print(f"  - {user.get('username', 'N/A')}: {user}")
    else:
        print("모든 사용자 데이터가 유효함")
    
    return len(duplicates) == 0 and len(invalid_users) == 0

def main():
    """메인 함수"""
    print("셀라앙상블 찬양단 - 사용자 데이터 복구 도구")
    print("=" * 50)
    
    # 1. 데이터 일관성 검사
    is_consistent = check_user_consistency()
    
    # 2. 데이터 복구
    if not is_consistent:
        print("\n데이터 일관성 문제 발견. 복구를 시작합니다...")
        users = fix_user_data()
    else:
        print("\n데이터 일관성 확인됨. 복구가 필요하지 않습니다.")
        users = load_users()
    
    # 3. 최종 결과 출력
    print(f"\n=== 최종 결과 ===")
    print(f"총 사용자 수: {len(users)}")
    
    for user in users:
        role_display = {
            'admin': '관리자',
            'special': '특별회원', 
            'regular': '정회원',
            'new': '신입회원'
        }.get(user['role'], user['role'])
        
        print(f"  - {user['username']} ({user['name']}) - {role_display}")
    
    print("\n복구 작업 완료!")

if __name__ == '__main__':
    main() 