import os
import re

def update_menu_names(directory):
    # Get all HTML files in the directory
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    
    # Define the replacements
    replacements = [
        (r'<li><a href="performances.html">공연영상</a></li>', 
         '<li><a href="performances.html">찬양사역영상</a></li>'),
        (r'<li><a href="inquiry.html">공연문의</a></li>', 
         '<li><a href="inquiry.html">찬양사역문의</a></li>'),
        # Also handle cases with different quotes or paths
        (r'<li><a href="/performances.html">공연영상</a></li>', 
         '<li><a href="/performances.html">찬양사역영상</a></li>'),
        (r'<li><a href="/inquiry.html">공연문의</a></li>', 
         '<li><a href="/inquiry.html">찬양사역문의</a></li>')
    ]
    
    # Process each HTML file
    for filename in html_files:
        filepath = os.path.join(directory, filename)
        
        # Skip already processed files
        if filename in ['performances.html', 'inquiry.html']:
            print(f"Skipping already processed file: {filename}")
            continue
            
        print(f"Processing {filename}...")
        
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Apply all replacements
        modified = False
        for old, new in replacements:
            if re.search(old, content):
                content = re.sub(old, new, content)
                modified = True
        
        # Write back if modified
        if modified:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated menu names in {filename}")
        else:
            print(f"No changes needed in {filename}")

if __name__ == "__main__":
    # Update files in the current directory
    update_menu_names('.')
    print("Done updating menu names in all HTML files.") 