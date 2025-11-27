import urllib.request
import gzip
import shutil
import os

url = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
output_dir = r"c:\Users\abhir\OneDrive\DP\graph_dp_project\data"
compressed_file = os.path.join(output_dir, "facebook_combined.txt.gz")
extracted_file = os.path.join(output_dir, "facebook_combined.txt")

import ssl

def download_file(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=ctx) as response, open(filepath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download: {e}")
        exit(1)

def extract_file(compressed_path, extracted_path):
    print(f"Extracting {compressed_path} to {extracted_path}...")
    try:
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(extracted_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print("Extraction complete.")
    except Exception as e:
        print(f"Failed to extract: {e}")
        exit(1)

if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    download_file(url, compressed_file)
    extract_file(compressed_file, extracted_file)
