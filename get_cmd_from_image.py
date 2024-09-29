import argparse
from PIL import Image

def print_image_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Image metadata for '{image_path}':")
            if img.info:
                for key, value in img.info.items():
                    print(f"{key}: {value}")
            else:
                print("No metadata found.")
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
    except IOError:
        print(f"Error: Unable to open the file '{image_path}'. It may not be a valid image file.")

def main():
    parser = argparse.ArgumentParser(description="Print metadata of an image file.")
    parser.add_argument("image_path", help="Path to the image file")
    args = parser.parse_args()

    print_image_metadata(args.image_path)

if __name__ == "__main__":
    main()