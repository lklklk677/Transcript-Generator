"""
Whisper Model Downloader - ULTRA STABLE VERSION
Uses Git LFS endpoints to avoid corrupted JSON files
"""

import requests
from pathlib import Path
from tqdm import tqdm
import time

# Configuration
MODEL_NAME = "large-v3"
OUTPUT_DIR = Path.home() / ".cache" / "whisper" / MODEL_NAME
MAX_RETRIES = 3
CHUNK_SIZE = 65536  # 64KB chunks

# Create directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use Hugging Face CDN with proper headers to avoid corruption
BASE_URL = "https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main"

FILES = {
    "model.bin": {
        "url": f"{BASE_URL}/model.bin",
        "size": 3094683252,
        "binary": True
    },
    "config.json": {
        "url": f"{BASE_URL}/config.json",
        "size": None,
        "binary": False  # Text file - verify UTF-8
    },
    "tokenizer.json": {
        "url": f"{BASE_URL}/tokenizer.json",
        "size": None,
        "binary": False
    },
    "vocabulary.json": {
        "url": f"{BASE_URL}/vocabulary.json",
        "size": None,
        "binary": False
    }
}

def download_file(url, output_path, expected_size=None, is_binary=True):
    """Download with proper encoding handling"""
    
    # Check if already complete
    if output_path.exists():
        current_size = output_path.stat().st_size
        if expected_size and current_size == expected_size:
            print(f"✅ {output_path.name} already complete")
            
            # Validate JSON files
            if not is_binary:
                try:
                    import json
                    with open(output_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"   ✓ JSON validation passed")
                except Exception as e:
                    print(f"   ⚠️  JSON corrupted, re-downloading: {e}")
                    output_path.unlink()
                else:
                    return True
            else:
                return True
    
    print(f"\n📥 Downloading: {output_path.name}")
    if expected_size:
        print(f"   Expected: {expected_size:,} bytes ({expected_size/1024/1024:.2f} MB)")
    
    retry = 0
    while retry < MAX_RETRIES:
        try:
            # Proper headers to avoid corruption
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': '*/*',
                'Accept-Encoding': 'identity'  # Disable compression to avoid corruption
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=120)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0)) or expected_size or 0
            
            # Download
            with open(output_path, 'wb') as f:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"  {output_path.name}",
                    ncols=80
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            # Verify
            final_size = output_path.stat().st_size
            
            # Check size
            if expected_size and final_size != expected_size:
                print(f"   ❌ Size mismatch: {final_size:,} vs {expected_size:,}")
                output_path.unlink()
                retry += 1
                time.sleep(2)
                continue
            
            # Validate JSON files
            if not is_binary:
                try:
                    import json
                    with open(output_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"   ✅ Downloaded and validated ({final_size:,} bytes)")
                    return True
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON corrupt: {e}")
                    output_path.unlink()
                    retry += 1
                    time.sleep(2)
                    continue
            else:
                print(f"   ✅ Downloaded ({final_size:,} bytes)")
                return True
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            retry += 1
            if retry < MAX_RETRIES:
                print(f"   🔄 Retry {retry}/{MAX_RETRIES}...")
                time.sleep(3)
            else:
                return False
    
    return False

# Main
print("=" * 80)
print("🚀 Whisper large-v3 Downloader - STABLE VERSION")
print("📂 Destination:", OUTPUT_DIR)
print("=" * 80)

success = 0
for filename, info in FILES.items():
    if download_file(
        info['url'],
        OUTPUT_DIR / filename,
        info.get('size'),
        info.get('binary', True)
    ):
        success += 1

# Final check
print("\n" + "=" * 80)
print("🔍 Final Verification")
print("=" * 80)

all_ok = True
for filename, info in FILES.items():
    path = OUTPUT_DIR / filename
    if path.exists():
        size = path.stat().st_size
        expected = info.get('size')
        
        status = "✅"
        if expected and size != expected:
            status = "⚠️ "
            all_ok = False
        
        print(f"{status} {filename}: {size:,} bytes")
        
        # Validate JSON
        if not info.get('binary', True):
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"   ✓ JSON valid")
            except Exception as e:
                print(f"   ✗ JSON INVALID: {e}")
                all_ok = False
    else:
        print(f"❌ {filename}: MISSING")
        all_ok = False

print("\n" + "=" * 80)
if all_ok:
    print("🎉 SUCCESS! All files downloaded and verified!")
    print(f"\n📂 Model: {OUTPUT_DIR}")
    print("\n✅ Ready to use - restart your Streamlit app!")
else:
    print("⚠️  INCOMPLETE - re-run this script")
print("=" * 80)
print(f"\n📊 Downloaded: {success}/{len(FILES)} files")
