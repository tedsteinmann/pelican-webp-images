import os
import logging
from pathlib import Path
from PIL import Image
from pelican import signals

logger = logging.getLogger(__name__)

class WebPProcessor:
    """Class to handle WebP image processing and responsive sizes"""
    
    def __init__(self, pelican_instance):
        self.pelican = pelican_instance
        self.settings = pelican_instance.settings
        
        # Get settings with defaults
        self.image_source_dir = Path(self.settings.get('WEBP_SOURCE_DIR', 'portfolio/static/images'))
        self.image_output_dir = Path(self.settings.get('OUTPUT_PATH', 'output')) / 'static' / 'images'
        self.supported_exts = self.settings.get('WEBP_SUPPORTED_FORMATS', [".jpg", ".jpeg", ".png", ".webp"])
        self.responsive_sizes = self.settings.get('WEBP_RESPONSIVE_SIZES', [300, 600, 1200])
        self.quality = self.settings.get('WEBP_QUALITY', 85)
        self.skip_dirs = self.settings.get('WEBP_SKIP_DIRS', ['thumbnails'])
        self.process_original = self.settings.get('WEBP_PROCESS_ORIGINAL', True)
        
    def ensure_directories(self):
        """Create output directories if they don't exist"""
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
    
    def should_skip_image(self, img_path):
        """Check if image should be skipped"""
        # Skip images in excluded directories
        if any(skip_dir in img_path.parts for skip_dir in self.skip_dirs):
            return True
            
        # Skip already resized images (e.g., image-300.webp)
        stem = img_path.stem
        if any(stem.endswith(f"-{s}") for s in self.responsive_sizes):
            return True
            
        return False
    
    def needs_processing(self, source_path, output_paths):
        """Check if source is newer than any of the output files"""
        source_mtime = source_path.stat().st_mtime
        
        for output_path in output_paths:
            if not output_path.exists() or source_mtime > output_path.stat().st_mtime:
                return True
        return False
    
    def process_image(self, img_path):
        """Process a single image to generate WebP versions"""
        try:
            with Image.open(img_path) as img:
                # Convert image mode for WebP compatibility
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                
                base_name = img_path.stem
                
                # Determine output path structure
                rel_path = img_path.relative_to(self.image_source_dir)
                target_dir = self.image_output_dir / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Prepare output paths for checking
                output_paths = []
                
                # Original WebP path
                webp_path = target_dir / f"{base_name}.webp"
                if self.process_original:
                    output_paths.append(webp_path)
                
                # Responsive size paths
                responsive_paths = []
                for width in self.responsive_sizes:
                    if img.width >= width:  # Don't upscale images
                        resized_path = target_dir / f"{base_name}-{width}.webp"
                        output_paths.append(resized_path)
                        responsive_paths.append((width, resized_path))
                
                # Check if processing is needed
                if not self.needs_processing(img_path, output_paths):
                    return 0
                
                processed_count = 0
                
                # Save original WebP
                if self.process_original:
                    img.save(webp_path, "WEBP", quality=self.quality)
                    logger.info(f"[WebP Plugin] Original: {img_path.name} → {webp_path.relative_to(self.image_output_dir)}")
                    processed_count += 1
                
                # Save responsive versions
                for width, resized_path in responsive_paths:
                    ratio = width / img.width
                    resized = img.resize((width, int(img.height * ratio)), Image.Resampling.LANCZOS)
                    resized.save(resized_path, "WEBP", quality=self.quality)
                    logger.info(f"[WebP Plugin] Resized: {base_name} → {resized_path.relative_to(self.image_output_dir)} ({width}px)")
                    processed_count += 1
                
                return processed_count
                
        except Exception as e:
            logger.error(f"[WebP Plugin] Error processing {img_path}: {e}")
            return 0
    
    def process_images(self):
        """Process all images in the source directory"""
        self.ensure_directories()
        
        if not self.image_source_dir.exists():
            logger.warning(f"[WebP Plugin] Source directory {self.image_source_dir} does not exist")
            return
        
        logger.info(f"[WebP Plugin] Processing images from {self.image_source_dir}")
        
        total_processed = 0
        total_files = 0
        
        # Process all supported image types
        for img_path in self.image_source_dir.rglob("*"):
            if img_path.suffix.lower() not in self.supported_exts:
                continue
                
            if self.should_skip_image(img_path):
                continue
            
            total_files += 1
            processed_count = self.process_image(img_path)
            total_processed += processed_count
        
        logger.info(f"[WebP Plugin] Processed {total_processed} image variants from {total_files} source images")

def process_webp_images(pelican_instance):
    """Signal handler to process WebP images during Pelican generation"""
    try:
        processor = WebPProcessor(pelican_instance)
        processor.process_images()
    except Exception as e:
        logger.error(f"[WebP Plugin] Processing failed: {e}")

def register():
    """Register the plugin with Pelican"""
    signals.finalized.connect(process_webp_images)
