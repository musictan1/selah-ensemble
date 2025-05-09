import os
import re

def add_menu_permissions_script(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if script is already included
    if 'src="js/menu-permissions.js"' in content:
        print(f"{html_file}: 이미 메뉴 권한 스크립트가 추가되어 있습니다.")
        return
    
    # Find the closing body tag
    body_close_pattern = re.compile(r'</body>', re.IGNORECASE)
    match = body_close_pattern.search(content)
    
    if match:
        # Insert menu permissions script before the closing body tag
        script_tag = '    <script src="js/menu-permissions.js"></script>\n'
        position = match.start()
        
        new_content = content[:position] + script_tag + content[position:]
        
        # Save the updated content
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"{html_file}: 메뉴 권한 스크립트 추가 완료")
    else:
        print(f"{html_file}: </body> 태그를 찾을 수 없습니다.")

def main():
    # Get all HTML files in the current directory
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    # Update each HTML file
    for html_file in html_files:
        # Skip files that shouldn't be updated
        if html_file in ['login.html', 'register.html', 'change-password.html', 'reset-password.html']:
            print(f"{html_file}: 인증 관련 페이지는 건너뜁니다.")
            continue
            
        add_menu_permissions_script(html_file)
        
    print("\n모든 HTML 파일 업데이트 완료")

if __name__ == "__main__":
    main() 