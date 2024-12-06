import os
import shutil
import hashlib

def calculate_hash(file_path):
    """Calculate the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def sync_directories(path_a, path_b):
    """Synchronize content from path_a to path_b with verification."""
    if not os.path.exists(path_a):
        print(f"Source path {path_a} does not exist.")
        return

    os.makedirs(path_b, exist_ok=True)

    # Step 1: Copy files from path_a to path_b
    for root, dirs, files in os.walk(path_a):
        relative_path = os.path.relpath(root, path_a)
        dest_root = os.path.join(path_b, relative_path)
        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            while True:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_root, file)
                
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {src_file} -> {dest_file}")

                src_hash = calculate_hash(src_file)
                dest_hash = calculate_hash(dest_file)
                if src_hash != dest_hash:
                    print(f"Integrity check failed for: {dest_file}")
                else:
                    print(f"Verified: {dest_file}")
                    break

    # Step 2: Remove files and directories from path_b not in path_a
    for root, dirs, files in os.walk(path_b, topdown=False):
        relative_path = os.path.relpath(root, path_b)
        src_root = os.path.join(path_a, relative_path)

        for file in files:
            dest_file = os.path.join(root, file)
            src_file = os.path.join(src_root, file)
            if not os.path.exists(src_file):
                os.remove(dest_file)
                print(f"Removed: {dest_file}")

        for dir in dirs:
            dest_dir = os.path.join(root, dir)
            src_dir = os.path.join(src_root, dir)
            if not os.path.exists(src_dir):
                shutil.rmtree(dest_dir)
                print(f"Removed directory: {dest_dir}")

if __name__ == "__main__":
    path_a = '/run/media/lplaat/LEONARD-HDD2/programming/leoDL again/build'
    path_b = '/run/media/lplaat/IPOD FROM L/Music'
    sync_directories(path_a, path_b)
