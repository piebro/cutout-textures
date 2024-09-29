import os
import subprocess
import argparse
import json
import shlex
from tqdm import tqdm

def generate_textures(input_dir, output_dir, settings_list):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png'))]

    # Calculate total number of operations
    total_operations = len(image_files) * len(settings_list)

    # Process each image with a progress bar
    with tqdm(total=total_operations, desc="Generating textures") as pbar:
        for image_file in sorted(image_files):
            input_path = os.path.join(input_dir, image_file)
            base_name = os.path.splitext(image_file)[0]

            for i, settings in enumerate(settings_list):
                output_file = f"{base_name}_{i:02d}.png"
                output_path = os.path.join(output_dir, output_file)

                # Construct the base command
                command = f"python3 generate_texture.py {shlex.quote(input_path)} {shlex.quote(output_path)}"

                # Add settings to the command
                for key, value in settings.items():
                    if isinstance(value, bool) and value:
                        # For boolean True values, just add the flag
                        command += f" --{key}"
                    elif isinstance(value, list):
                        # For list values, join them into a space-separated string
                        command += f" --{key} {' '.join(map(str, value))}"
                    elif value is not None:
                        # For other non-None values, add them as usual
                        command += f" --{key} {shlex.quote(str(value))}"

                # Run the command
                try:
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error generating {output_path}: {e}")
                    print(f"Command output: {e.output}")

                # Update progress bar
                pbar.update(1)

    print("Finished!")

def main():
    parser = argparse.ArgumentParser(description="Generate textures from cutout images with multiple settings.")
    parser.add_argument("input_dir", help="Directory containing input images")
    parser.add_argument("output_dir", help="Directory to save generated textures")
    parser.add_argument("settings", nargs='+', help="JSON strings representing settings dictionaries")

    args = parser.parse_args()

    # Parse the JSON strings into Python dictionaries
    settings_list = [json.loads(s) for s in args.settings]

    generate_textures(args.input_dir, args.output_dir, settings_list)

if __name__ == "__main__":
    main()