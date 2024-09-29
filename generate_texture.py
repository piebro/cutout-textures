import os
import random
import math
import argparse
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def main():
    parser = argparse.ArgumentParser(description="Generate generative art with customizable parameters.")
    parser.add_argument("cutout_file", help="Filename of the cutout image to use")
    parser.add_argument("output_file", help="Filename for the output image")
    parser.add_argument("--canvas-size", nargs=2, type=int, default=[1024, 1024], help="Canvas size (width height)")
    parser.add_argument("--base-dx-range", nargs=2, type=int, default=[50, 200], help="Base dx range (min max)")
    parser.add_argument("--base-dy-range", nargs=2, type=int, default=[50, 200], help="Base dy range (min max)")
    parser.add_argument("--base-cutout-angle-range", nargs=2, type=float, default=[0, 360], help="Base cutout angle range (min max)")
    parser.add_argument("--base-scale-range", nargs=2, type=float, default=[0.5, 1.5], help="Base scale range (min max)")
    parser.add_argument("--position-variation-range", nargs=2, type=int, default=[-20, 20], help="Position variation range (min max)")
    parser.add_argument("--scale-variation-range", nargs=2, type=float, default=[0.8, 1.2], help="Scale variation range (min max)")
    parser.add_argument("--angle-variation-range", nargs=2, type=float, default=[-15, 15], help="Angle variation range (min max)")
    parser.add_argument("--grid-tilt-range", nargs=2, type=float, default=[-180, 180], help="Grid tilt range (min max)")
    parser.add_argument("--seed", type=int, help="Random seed (if not provided, a random seed will be generated)")
    parser.add_argument("--add-center-cutout", action="store_true", help="Add the cutout in the center of the image at the end")

    args = parser.parse_args()

    # Generate a random seed if not provided
    if args.seed is None:
        args.seed = random.randint(0, 2**32 - 1)

    # Construct the command to reproduce the image
    command = f"python3 generate_texture.py {args.cutout_file} {args.output_file}"
    command += f" --canvas-size {args.canvas_size[0]} {args.canvas_size[1]}"
    command += f" --base-dx-range {args.base_dx_range[0]} {args.base_dx_range[1]}"
    command += f" --base-dy-range {args.base_dy_range[0]} {args.base_dy_range[1]}"
    command += f" --base-cutout-angle-range {args.base_cutout_angle_range[0]} {args.base_cutout_angle_range[1]}"
    command += f" --base-scale-range {args.base_scale_range[0]} {args.base_scale_range[1]}"
    command += f" --position-variation-range {args.position_variation_range[0]} {args.position_variation_range[1]}"
    command += f" --scale-variation-range {args.scale_variation_range[0]} {args.scale_variation_range[1]}"
    command += f" --angle-variation-range {args.angle_variation_range[0]} {args.angle_variation_range[1]}"
    command += f" --grid-tilt-range {args.grid_tilt_range[0]} {args.grid_tilt_range[1]}"
    command += f" --seed {args.seed}"
    if args.add_center_cutout:
        command += " --add-center-cutout"

    # Set the random seed
    random.seed(args.seed)

    # Use the specified cutout file
    if not os.path.exists(args.cutout_file):
        print(f"Error: The specified cutout file '{args.cutout_file}' does not exist.")
        return

    cutout = Image.open(args.cutout_file).convert("RGBA")

    # Set base grid spacing
    base_dx = random.randint(*args.base_dx_range)
    base_dy = random.randint(*args.base_dy_range)

    # Set base angle and scale for cutouts
    base_cutout_angle = random.uniform(*args.base_cutout_angle_range)
    base_scale = random.uniform(*args.base_scale_range)

    # Calculate starting positions to ensure full coverage
    start_x = -cutout.width
    start_y = -cutout.height

    # Create a larger canvas to accommodate rotation
    diagonal = int(math.sqrt(args.canvas_size[0]**2 + args.canvas_size[1]**2))
    large_canvas = Image.new('RGB', (diagonal, diagonal), color='white')

    # Place cutouts in a grid pattern on the larger canvas with variations
    for y in range(start_y, diagonal, base_dy):
        for x in range(start_x, diagonal, base_dx):
            # Add randomness to position
            random_x = x + random.randint(*args.position_variation_range)
            random_y = y + random.randint(*args.position_variation_range)

            # Add randomness to scale
            random_scale = base_scale * random.uniform(*args.scale_variation_range)
            new_size = tuple(int(dim * random_scale) for dim in cutout.size)

            # Add randomness to rotation
            random_angle = base_cutout_angle + random.uniform(*args.angle_variation_range)

            # Resize and rotate the cutout
            rotated_cutout = cutout.resize(new_size, Image.LANCZOS)
            rotated_cutout = rotated_cutout.rotate(random_angle, expand=True)

            large_canvas.paste(rotated_cutout, (random_x, random_y), rotated_cutout)

    # Set random tilt angle for the entire grid
    grid_tilt = random.uniform(*args.grid_tilt_range)

    # Rotate the entire canvas
    rotated_canvas = large_canvas.rotate(grid_tilt, resample=Image.BICUBIC, expand=False)

    # Crop the rotated canvas back to the original size
    left = (rotated_canvas.width - args.canvas_size[0]) // 2
    top = (rotated_canvas.height - args.canvas_size[1]) // 2
    right = left + args.canvas_size[0]
    bottom = top + args.canvas_size[1]
    final_canvas = rotated_canvas.crop((left, top, right, bottom))

    # Add the center cutout if specified
    if args.add_center_cutout:
        center_x = args.canvas_size[0] // 2
        center_y = args.canvas_size[1] // 2
        center_cutout = cutout.copy()
        center_cutout = center_cutout.resize((int(cutout.width * base_scale), int(cutout.height * base_scale)), Image.LANCZOS)
        #center_cutout = center_cutout.rotate(base_cutout_angle, expand=True)
        paste_x = center_x - center_cutout.width // 2
        paste_y = center_y - center_cutout.height // 2
        final_canvas.paste(center_cutout, (paste_x, paste_y), center_cutout)

    # Create PngInfo object and add the command
    metadata = PngInfo()
    metadata.add_text("command", command)

    # Ensure the directory exists
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the final image with metadata
    final_canvas.save(args.output_file, pnginfo=metadata)

if __name__ == "__main__":
    main()