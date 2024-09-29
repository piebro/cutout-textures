import fal_client
import requests
from PIL import Image
import io
import argparse
import os

def get_image_size(size_option, custom_width=None, custom_height=None):
    size_options = {
        "square": {"width": 512, "height": 512},
        "square_hd": {"width": 1024, "height": 1024},
        "landscape_4_3": {"width": 1024, "height": 768},
        "landscape_16_9": {"width": 1024, "height": 576},
        "portrait_3_4": {"width": 768, "height": 1024},
        "portrait_9_16": {"width": 576, "height": 1024},
    }
    
    if size_option == "custom":
        return {"width": custom_width, "height": custom_height}
    return size_options.get(size_option, size_options["square"])

def generate_image(prompt, output_dir, image_size, num_images):
    handler = fal_client.submit(
        "fal-ai/flux/dev",
        arguments={
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": num_images,
            "enable_safety_checker": False,
            "output_format": "png",
        },
    )

    result = handler.get()
    os.makedirs(output_dir, exist_ok=True)
    
    if 'images' in result and result['images']:
        for i, image_data in enumerate(result['images']):
            response = requests.get(image_data['url'])
            if response.status_code == 200:
                counter = 0
                while True:
                    filename = f"{prompt[:180].replace(' ', '_')}_{counter:02d}.png"
                    save_path = os.path.join(output_dir, filename)
                    if not os.path.exists(save_path):
                        break
                    counter += 1
                
                Image.open(io.BytesIO(response.content)).save(save_path)
                print(f"Image saved as {save_path}")
            else:
                print(f"Failed to download image {i+1}. Status code: {response.status_code}")
    else:
        print("No image data found in the result")

def main():
    parser = argparse.ArgumentParser(description="Generate images using Flux")
    parser.add_argument("prompts", nargs="+", help="One or more prompts for image generation")
    parser.add_argument("--output", required=True, help="Output directory for generated images")
    parser.add_argument("--size", choices=["square", "square_hd", "landscape_4_3", "landscape_16_9", "portrait_3_4", "portrait_9_16", "custom"], default="square", help="Image size option")
    parser.add_argument("--width", type=int, help="Custom width for image size")
    parser.add_argument("--height", type=int, help="Custom height for image size")
    parser.add_argument("--num-images", type=int, default=1, help="Number of images to generate per prompt")
    args = parser.parse_args()
    
    if args.size == "custom" and (args.width is None or args.height is None):
        parser.error("Custom size requires both --width and --height to be specified")
    
    image_size = get_image_size(args.size, args.width, args.height)

    for prompt in args.prompts:
        generate_image(prompt, args.output, image_size, args.num_images)

if __name__ == "__main__":
    main()