import os
import io
from rembg import remove
from PIL import Image, ImageEnhance, ImageStat

# Set folder paths
input_folder = r"D:\my_photos\input_images"
output_folder = r"D:\my_photos\output_images"
model_path = r"D:\my_photos\model\u2net.onnx"

# Create folders if they don't exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# List image files
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

if not image_files:
    print("⚠️ No images found. Check input folder.")
else:
    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"bg_removed_{filename}")
        try:
            print(f"📸 Processing: {filename}")

            # Open image
            with open(input_path, "rb") as f:
                img_bytes = f.read()

            # 🟡 Remove background
            output_bytes = remove(img_bytes, model_dir=model_path)

            # Convert output to PIL image
            img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

            # Extract the alpha channel and main image
            alpha = img.split()[3]
            img_rgb = img.convert("RGB")

            # Calculate image statistics for main image
            stat = ImageStat.Stat(img_rgb)
            brightness = stat.mean[0]  # Average brightness
            color_intensity = stat.mean[1]  # Average color intensity

            # 🟡 Adjust brightness based on average brightness
            if brightness < 100:
                img_rgb = ImageEnhance.Brightness(img_rgb).enhance(1.5)
            elif brightness > 200:
                img_rgb = ImageEnhance.Brightness(img_rgb).enhance(0.7)

            # 🟡 Adjust color based on average color intensity
            if color_intensity < 100:
                img_rgb = ImageEnhance.Color(img_rgb).enhance(1.5)
            elif color_intensity > 200:
                img_rgb = ImageEnhance.Color(img_rgb).enhance(0.7)

            # 🟡 Adjust contrast
            img_rgb = ImageEnhance.Contrast(img_rgb).enhance(1.1)

            # 🟡 Adjust sharpness
            img_rgb = ImageEnhance.Sharpness(img_rgb).enhance(1.2)

            # 🟡 Center the subject in the image with margin
            bbox = img.getbbox()
            img_cropped = img.crop(bbox)
            margin = int(37.8)  # 1 cm margin in pixels
            img_width, img_height = img_cropped.size
            new_size = 1000 - 2 * margin  # 1000 px frame size minus 2 margins
            scale_factor = min(new_size / img_width, new_size / img_height)
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            img_resized = img_cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 🟡 Create centered image with solid white background
            final_img = Image.new("RGBA", (1000, 1000), (255, 255, 255, 255))
            paste_x = (1000 - new_width) // 2
            paste_y = (1000 - new_height) // 2
            final_img.paste(img_resized, (paste_x, paste_y), img_resized)

            # 🟡 Save output with white background
            final_img.convert("RGB").save(output_path, "JPEG", quality=100)
            print(f"✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

print("🎉 Background removal and editing finished.")
