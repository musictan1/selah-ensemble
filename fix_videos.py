import os
import json
import shutil

def fix_videos():
    print("Starting video file path fix...")
    
    # Define paths
    data_path = os.path.join('data', 'data.json')
    videos_dir = os.path.join('uploads', 'videos')
    videos_default_dir = os.path.join(videos_dir, 'default')
    
    # Ensure the videos/default directory exists
    os.makedirs(videos_default_dir, exist_ok=True)
    
    # Load data.json
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded data.json")
    except Exception as e:
        print(f"Error loading data.json: {e}")
        return False
    
    # Check if videos key exists in data
    if 'videos' not in data:
        print("No videos key in data.json, creating it")
        data['videos'] = []
    
    # Get list of files in videos/default directory
    default_files = []
    if os.path.exists(videos_default_dir):
        default_files = [f for f in os.listdir(videos_default_dir) if os.path.isfile(os.path.join(videos_default_dir, f))]
    print(f"Found {len(default_files)} files in videos/default directory: {default_files}")
    
    # Get list of files in videos directory (excluding subdirectories)
    root_files = []
    if os.path.exists(videos_dir):
        root_files = [f for f in os.listdir(videos_dir) if os.path.isfile(os.path.join(videos_dir, f))]
    print(f"Found {len(root_files)} files in videos directory: {root_files}")
    
    # Move any files from videos directory to videos/default
    for file in root_files:
        src = os.path.join(videos_dir, file)
        dst = os.path.join(videos_default_dir, file)
        try:
            shutil.move(src, dst)
            print(f"Moved {file} from videos to videos/default")
            if file not in default_files:
                default_files.append(file)
        except Exception as e:
            print(f"Error moving {file}: {e}")
    
    # Update data.json with all files found
    all_videos = set(default_files + data['videos'])
    data['videos'] = sorted(list(all_videos))
    print(f"Updated videos list in data.json: {data['videos']}")
    
    # Save updated data.json
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully saved updated data.json")
    except Exception as e:
        print(f"Error saving data.json: {e}")
        return False
    
    print("Video file path fix completed successfully")
    return True

if __name__ == "__main__":
    fix_videos() 