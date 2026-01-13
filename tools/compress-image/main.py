import os
import io
import time
from PIL import Image
from decouple import config

def compress_image(file_path, max_size_mb=2, quality=85):
    try:
        image = Image.open(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        format = image.format

        if file_size <= max_size_mb:
            print(f"Image {file_path} is already under {max_size_mb} MB.")
            return

        print(f"Compressing {file_path} ({file_size:.2f} MB)...")

        while file_size > max_size_mb:
            buffer = io.BytesIO()
            if format.lower() == 'jpeg':
                image.save(buffer, format=format, quality=quality)
            else:
                image.save(buffer, format=format)

            file_size = buffer.getbuffer().nbytes / (1024 * 1024)
            quality -= 5

            if quality < 10:
                print(f"Cannot compress {file_path} under {max_size_mb} MB.")
                return

        with open(file_path, 'wb') as f:
            f.write(buffer.getbuffer())
        print(f"Image {file_path} compressed to {file_size:.2f} MB.")
    
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def traverse_and_compress(root_dir, max_size_mb=2):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                compress_image(file_path, max_size_mb)

if __name__ == "__main__":
    start_time = time.time()
    
    directory = config('DIR_IMAGE', default='D:/')
    traverse_and_compress(directory, max_size_mb=2)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Execution time: {elapsed_time:.2f} seconds")
    input("Press Enter to exit...")
