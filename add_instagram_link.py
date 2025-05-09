import os
import re

def add_instagram_link_to_menu(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Instagram link is already in the menu
    if 'href="https://www.instagram.com/selahensemble1/"' in content:
        print(f"{html_file}: 이미 인스타그램 링크가 있습니다.")
        return
    
    # Find the nav-menu list in the HTML
    nav_menu_pattern = re.compile(r'<ul class="nav-menu">(.*?)</ul>', re.DOTALL)
    match = nav_menu_pattern.search(content)
    
    if not match:
        print(f"{html_file}: nav-menu를 찾을 수 없습니다.")
        return
    
    # Find the position to insert the Instagram link 
    # (typically after YouTube link or before admin/login links)
    nav_menu_content = match.group(1)
    
    # Check if there's a youtube link
    youtube_link_pattern = re.compile(r'<li><a href="youtube\.html">유튜브</a></li>')
    youtube_match = youtube_link_pattern.search(nav_menu_content)
    
    # Position to insert: after YouTube link if found, otherwise before admin/login links
    if youtube_match:
        insert_position = match.start(1) + youtube_match.end()
        new_link = '\n                <li><a href="https://www.instagram.com/selahensemble1/" target="_blank">인스타그램</a></li>'
    else:
        # Find admin or login link as fallback
        admin_link_pattern = re.compile(r'<li><a href="admin\.html">회원관리</a></li>')
        admin_match = admin_link_pattern.search(nav_menu_content)
        
        if admin_match:
            insert_position = match.start(1) + admin_match.start()
        else:
            # Insert at the end of the nav-menu
            insert_position = match.start(1) + len(nav_menu_content)
        
        new_link = '\n                <li><a href="https://www.instagram.com/selahensemble1/" target="_blank">인스타그램</a></li>'
    
    # Insert the Instagram link
    new_content = content[:insert_position] + new_link + content[insert_position:]
    
    # Save the updated content
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"{html_file}: 인스타그램 링크 추가 완료")

def main():
    # Get all HTML files in the current directory
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    # Update each HTML file
    for html_file in html_files:
        add_instagram_link_to_menu(html_file)
        
    print("\n모든 HTML 파일에 인스타그램 링크 추가 완료")

if __name__ == "__main__":
    main() 