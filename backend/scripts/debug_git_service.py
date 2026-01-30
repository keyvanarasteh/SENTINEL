
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.git_service import GitService

def debug_service():
    print("Debugging GitService...")
    service = GitService()
    repo_url = "https://github.com/octocat/Hello-World"
    
    try:
        print(f"1. Cloning {repo_url}...")
        repo_path = service.clone_repository({}, repo_url)
        print(f"   Clone successful: {repo_path}")
        
        print("2. Listing files...")
        files = service.list_repo_files(repo_path)
        print(f"   Found {len(files)} files")
        for f in files:
            print(f"   - {f['relative_path']} ({f['extension']})")
            
        print("3. Cleaning up...")
        service.cleanup_repo(repo_path)
        print("   Cleanup successful")
        
        if len(files) > 0:
            print("✅ GitService working correctly")
        else:
            print("⚠️ No files found (Config issue?)")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Service Failed: {e}")

if __name__ == "__main__":
    debug_service()
