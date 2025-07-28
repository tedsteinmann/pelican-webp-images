# Pelican WebP Images Plugin

**Pelican WebP Images** is a plugin for [Pelican](https://getpelican.com/) that automatically generates responsive WebP images from your static images during the build process.

## Features

- **WebP Conversion**: Converts JPEG, PNG, and other formats to WebP for better compression
- **Responsive Sizes**: Generates multiple image sizes (300px, 600px, 1200px by default)
- **Smart Processing**: Only processes files when source is newer than output
- **Configurable**: Flexible settings for quality, sizes, and directories
- **Compression Control**: Tweak `WEBP_METHOD` and `WEBP_QUALITY` for smaller files
- **Skip Logic**: Excludes thumbnail directories and prevents upscaling
- **Performance**: Efficient processing with proper error handling

## Installation

1. Install the plugin:
   ```sh
   pip install -e .
   ```

2. Add `webp_images` to your `PLUGINS` list in `pelicanconf.py`:
   ```python
   PLUGINS = [
       # ... other plugins ...
       'webp_images',
   ]
   ```

## Configuration

Add these optional settings to your `pelicanconf.py` to customize the plugin:

```python
# WebP Images Plugin Settings
WEBP_SOURCE_DIR = 'portfolio/static/images'        # Source directory for images
WEBP_RESPONSIVE_SIZES = [300, 600, 1200]           # Responsive sizes to generate
WEBP_QUALITY = 85                                  # WebP quality (0-100)
WEBP_METHOD = 6                                    # libwebp compression effort (0-6)
WEBP_SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']  # Supported formats
WEBP_SKIP_DIRS = ['thumbnails']                    # Directories to skip
WEBP_PROCESS_ORIGINAL = True                       # Generate original size WebP
```

## Usage

1. Place your images in the configured source directory (default: `portfolio/static/images`)

2. Build your Pelican site as usual:
   ```sh
   pelican content
   ```

3. The plugin will automatically:
   - Convert images to WebP format
   - Generate responsive sizes for each image
   - Only process files that have been modified
   - Skip thumbnail directories and already-resized images

## Output Structure

For an image `photo.jpg` (assuming it's 1800px wide), the plugin generates:
- `photo.webp` (original size, 1800px)
- `photo-300.webp` (300px wide)
- `photo-600.webp` (600px wide)
- `photo-1200.webp` (1200px wide)

Note: The plugin will not upscale images, so if your source is 800px wide, only `photo.webp` and `photo-300.webp` and `photo-600.webp` would be generated.

## Integration with HTML

You can use the generated responsive images in your templates:

```html
<picture>
  <source srcset="/static/images/photo-300.webp" media="(max-width: 400px)">
  <source srcset="/static/images/photo-600.webp" media="(max-width: 800px)">
  <source srcset="/static/images/photo-1200.webp" media="(max-width: 1400px)">
  <img src="/static/images/photo.webp" alt="Description" loading="lazy"
       sizes="(max-width: 800px) 380px, 1200px">
</picture>
```

## Development & Testing

1. Create a virtual environment and install dependencies:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run tests with [pytest](https://pytest.org):
   ```sh
   pytest
   ```

## Dependencies

- **Pillow**: Required for image processing
- **Pelican**: Required for plugin integration

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss your ideas or report bugs.

---

**Author:** Ted Steinmann  
**Project:** [pelican-webp-images](https://github.com/tedsteinmann/pelican-webp-images)
