import os
import json
import sys

def force_sync():
    print("Starting forced synchronization of data.json with file system...")
    
    # Define paths
    data_path = os.path.join('data', 'data.json')
    uploads_dir = 'uploads'
    
    # Load data.json
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded data.json")
    except Exception as e:
        print(f"Error loading data.json: {e}")
        return False
    
    # Initialize data structure if needed
    if 'music' not in data:
        data['music'] = {'ai': [], 'mr': [], 'live': []}
    if 'scores' not in data:
        data['scores'] = []
    if 'videos' not in data:
        data['videos'] = []
    
    # Sync music files
    for category in ['ai', 'mr', 'live']:
        category_path = os.path.join(uploads_dir, 'music', category)
        if os.path.exists(category_path):
            files = [f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f))]
            print(f"Found {len(files)} files in music/{category} directory")
            data['music'][category] = sorted(files)
    
    # Sync scores files
    scores_path = os.path.join(uploads_dir, 'scores')
    scores_default_path = os.path.join(scores_path, 'default')
    scores_files = []
    
    # Check main scores directory
    if os.path.exists(scores_path):
        scores_files.extend([f for f in os.listdir(scores_path) if os.path.isfile(os.path.join(scores_path, f))])
    
    # Check scores/default directory
    if os.path.exists(scores_default_path):
        scores_files.extend([f for f in os.listdir(scores_default_path) if os.path.isfile(os.path.join(scores_default_path, f))])
    
    print(f"Found {len(scores_files)} files in scores directories")
    data['scores'] = sorted(scores_files)
    
    # Sync videos files
    videos_path = os.path.join(uploads_dir, 'videos')
    videos_default_path = os.path.join(videos_path, 'default')
    videos_files = []
    
    # Check main videos directory
    if os.path.exists(videos_path):
        videos_files.extend([f for f in os.listdir(videos_path) if os.path.isfile(os.path.join(videos_path, f))])
    
    # Check videos/default directory
    if os.path.exists(videos_default_path):
        videos_files.extend([f for f in os.listdir(videos_default_path) if os.path.isfile(os.path.join(videos_default_path, f))])
    
    print(f"Found {len(videos_files)} files in videos directories")
    data['videos'] = sorted(videos_files)
    
    # Save updated data.json
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully saved updated data.json")
    except Exception as e:
        print(f"Error saving data.json: {e}")
        return False
    
    print("Forced synchronization completed successfully")
    return True

if __name__ == "__main__":
    force_sync() 