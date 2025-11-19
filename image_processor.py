from PIL import Image
import io
from typing import Tuple

class ImageProcessor:
	def __init__(self, watermark_path: str):
		self.watermark_path = watermark_path
		self.watermark = None
		if watermark_path:
			try:
				self.watermark = Image.open(watermark_path).convert("RGBA")
			except Exception as e:
				print(f"Error opening watermark image: {e}")

	def fix_aspect_ratio(self, image: Image.Image, target_ratio: Tuple[int, int]) -> Image.Image:
		"""
		Fix the aspect ratio of the image to the target ratio by adding padding to the sides or top/bottom.
		"""
		width, height = image.size
		current_ratio = width / height

		if abs(current_ratio - target_ratio) < 0.01:
			return image

		if current_ratio > target_ratio:
			new_width = width
			new_height = int(width / target_ratio)
		else:
			new_height = height
			new_width = int(height * target_ratio)

		new_image = Image.new('RGB', (new_width, new_height), 'white')

		x_offset = (new_width - width) // 2
		y_offset = (new_height - height) // 2

		new_image.paste(image, (x_offset, y_offset))

		return new_image

	def add_watermark(self, image: Image.Image, opacity: float = 0.3, position: str = 'center', margin: int = 20) -> Image.Image:
		"""
		Add a watermark to the image at the specified position.
		"""
		if not self.watermark:
			print("No watermark image provided")
			return image

		if image.mode != 'RGBA':
			image = image.convert('RGBA')

		max_wm_width = int(image.width * 0.2)
		max_wm_height = int(image.height * 0.2)

		watermark = self.watermark.copy()
		if watermark.width > max_wm_width or watermark.height > max_wm_height:
			watermark.thumbnail((max_wm_width, max_wm_height), Image.Resampling.LANCZOS)

			watermark_with_opacity = watermark.copy()
			alpha = watermark_with_opacity.split()[3]
			alpha = alpha.point(lambda p: int(p * opacity))
			watermark_with_opacity.putalpha(alpha)

		wm_width, wm_height = watermark_with_opacity.size
		img_width, img_height = image.size

		if position == 'bottom-right':
			x = img_width - wm_width - margin
			y = img_height - wm_height - margin
		elif position == 'bottom-left':
			x = margin
			y = img_height - wm_height - margin
		elif position == 'top-right':
			x = img_width - wm_width - margin
			y = margin
		elif position == 'top-left':
			x = margin
			y = margin
		else: # center
			x = (img_width - wm_width) // 2
			y = (img_height - wm_height) // 2


		transparent = Image.new('RGBA', image.size, (0, 0, 0, 0))
		transparent.paste(watermark_with_opacity, (x, y))

		watermarked = Image.alpha_composite(image, transparent)

		return watermarked

	def process_image(self, image_bytes: bytes, target_ratio: Tuple[int, int], watermark_opacity: float = 0.3, watermark_position: str = 'center', watermark_margin: int = 20) -> bytes:
		"""
		Main processing pipeline: fix aspect ratio, add watermark, and return the processed image as bytes.
		"""

		try:
			image = Image.open(io.BytesIO(image_bytes))
		except Exception as e:
			print(f"Error opening image: {e}")
			return None

		 # Convert to RGB if necessary
		if image.mode in ('RGBA', 'LA', 'P'):
			background = Image.new('RGB', image.size, (255, 255, 255))
			if image.mode == 'P':
				image = image.convert('RGBA')
			background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
			image = background

		# Fix aspect ratio
		image = self.fix_aspect_ratio(image, target_ratio)

		# Add watermark
		image = self.add_watermark(image, watermark_opacity, watermark_position, watermark_margin)

		# Convert back to RGB for JPEG output
		if image.mode == 'RGBA':
			background = Image.new('RGB', image.size, (255, 255, 255))
			background.paste(image, mask=image.split()[3])
			image = background

		# Save to bytes
		output = io.BytesIO()
		image.save(output, format='JPEG', quality=90, optimize=True)
		output.seek(0)

		return output.getvalue()
