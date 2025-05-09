import os
import sys
import shutil

def clear_screen():
    """화면 지우기"""
    os.system('cls' if os.name == 'nt' else 'clear')

def debug_file_rename():
    """파일명 변경 디버그 도구"""
    clear_screen()
    print("==== 파일명 변경 디버깅 도구 ====")
    
    # 작업 디렉토리 확인
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    
    # 폴더 선택
    print("\n사용 가능한 카테고리:")
    categories = [
        "uploads/music/ai", 
        "uploads/music/mr", 
        "uploads/music/live",
        "uploads/scores",
        "uploads/videos"
    ]
    
    for i, category in enumerate(categories):
        # 해당 폴더에 있는 파일 수 계산
        try:
            if os.path.exists(category):
                files = [f for f in os.listdir(category) if os.path.isfile(os.path.join(category, f))]
                print(f"{i+1}. {category} ({len(files)}개 파일)")
            else:
                print(f"{i+1}. {category} (폴더 없음)")
        except Exception as e:
            print(f"{i+1}. {category} (오류: {e})")
    
    try:
        choice = int(input("\n테스트할 카테고리 번호 선택: ")) - 1
        if choice < 0 or choice >= len(categories):
            print("잘못된 선택입니다.")
            return
            
        selected_category = categories[choice]
        
        # 폴더 존재 여부 확인
        if not os.path.exists(selected_category):
            print(f"오류: 선택한 폴더 '{selected_category}'가 존재하지 않습니다.")
            return
            
        # 파일 목록 보여주기
        files = [f for f in os.listdir(selected_category) if os.path.isfile(os.path.join(selected_category, f))]
        
        if not files:
            print(f"'{selected_category}' 폴더에 파일이 없습니다.")
            return
            
        print(f"\n'{selected_category}' 폴더의 파일 목록:")
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
            
        file_choice = int(input("\n테스트할 파일 번호 선택: ")) - 1
        if file_choice < 0 or file_choice >= len(files):
            print("잘못된 선택입니다.")
            return
            
        selected_file = files[file_choice]
        old_path = os.path.join(selected_category, selected_file)
        
        new_filename = input(f"\n새 파일명 입력 (현재: {selected_file}): ")
        if not new_filename:
            print("파일명이 입력되지 않았습니다.")
            return
            
        # 파일명을 직접 제어
        if '.' not in new_filename and '.' in selected_file:
            # 확장자 추가
            ext = selected_file.split('.')[-1]
            new_filename = f"{new_filename}.{ext}"
            print(f"확장자 추가됨: {new_filename}")
            
        new_path = os.path.join(selected_category, new_filename)
        
        # 파일명 변경 전 확인
        print("\n===== 파일명 변경 전 확인 =====")
        print(f"원본 파일 존재 여부: {os.path.exists(old_path)}")
        print(f"새 파일명 중복 여부: {os.path.exists(new_path)}")
        print(f"원본 경로: {old_path}")
        print(f"새 경로: {new_path}")
        print(f"경로 정규화 (원본): {os.path.normpath(old_path)}")
        print(f"경로 정규화 (새 경로): {os.path.normpath(new_path)}")
        print(f"대소문자 무시 비교: {os.path.normcase(old_path) == os.path.normcase(new_path)}")
        
        if os.path.exists(new_path) and os.path.normcase(old_path) != os.path.normcase(new_path):
            print("\n오류: 같은 이름의 파일이 이미 존재합니다.")
            return
            
        proceed = input("\n파일명을 변경하시겠습니까? (y/n): ")
        if proceed.lower() != 'y':
            print("작업이 취소되었습니다.")
            return
            
        # 파일명 변경 실행
        try:
            # 안전한 파일명 변경 방법 (복사 후 삭제)
            shutil.copy2(old_path, new_path)
            
            # 확인 후 이전 파일 삭제
            if os.path.exists(new_path) and os.path.getsize(new_path) > 0:
                os.remove(old_path)
                print(f"파일명이 성공적으로 변경되었습니다: {selected_file} → {new_filename}")
            else:
                print("새 파일 생성 실패")
                if os.path.exists(new_path):
                    os.remove(new_path)
        except Exception as e:
            print(f"파일명 변경 중 오류 발생: {e}")
            # 오류 발생 시 새 파일 삭제
            if os.path.exists(new_path) and os.path.normcase(old_path) != os.path.normcase(new_path):
                os.remove(new_path)
    except Exception as e:
        print(f"오류 발생: {e}")
        
if __name__ == "__main__":
    debug_file_rename() 