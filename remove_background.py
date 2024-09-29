import argparse
import os
import fal_client
from PIL import Image
import requests
from io import BytesIO

def remove_background(input_path, output_path):
    # Check if the output file already exists
    if os.path.exists(output_path):
        print(f"Skipping {input_path} as output already exists: {output_path}")
        return

    # Upload the image using fal_client
    try:
        image_url = fal_client.upload_file(input_path)
    except Exception as e:
        print(f"Failed to upload {input_path}: {str(e)}")
        return

    # Use the fal-ai API to remove the background
    handler = fal_client.submit(
        "fal-ai/imageutils/rembg",
        arguments={
            "image_url": image_url
        },
    )
    result = handler.get()

    # Download and save the result
    if 'image' in result and isinstance(result['image'], dict) and 'url' in result['image']:
        response = requests.get(result['image']['url'])
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(output_path, 'PNG')
            print(f"Processed image saved as {output_path}")
        else:
            print(f"Failed to download processed image for {input_path}")
    else:
        print(f"No processed image URL found in the result for {input_path}")

def main():
    parser = argparse.ArgumentParser(description="Remove background from images in a folder")
    parser.add_argument("input_folder", help="Input folder containing images")
    parser.add_argument("output_folder", help="Output folder for processed images")
    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    for filename in sorted(os.listdir(args.input_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            input_path = os.path.join(args.input_folder, filename)
            output_path = os.path.join(args.output_folder, filename)
            remove_background(input_path, output_path)

if __name__ == "__main__":
    main()