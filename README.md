# Pelican WebP Images Plugin

**Pelican WebP Images** is a plugin for [Pelican](https://getpelican.com/) that automatically generates responsive WebP images from your static images during the build process.

## Features

- **WebP Conversion**: Converts JPEG, PNG, and other formats to WebP for better compression
- **Responsive Sizes**: Generates multiple image sizes (300px, 400px, 600px, 800px, 1200px by default)
- **Smart Processing**: Only processes files when source is newer than output
- **Configurable**: Flexible settings for quality, sizes, and directories
- **Optimized Compression**: Default quality of 80 balances file size and visual quality
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
WEBP_RESPONSIVE_SIZES = [300, 400, 600, 800, 1200] # Responsive sizes to generate
WEBP_QUALITY = 80                                   # WebP quality (0-100, default: 80)
WEBP_METHOD = 6                                     # libwebp compression effort (0-6)
WEBP_SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']  # Supported formats
WEBP_SKIP_DIRS = ['thumbnails']                     # Directories to skip
WEBP_PROCESS_ORIGINAL = True                        # Generate original size WebP
```

### Quality Settings

The default `WEBP_QUALITY` is set to 80, which provides an excellent balance between file size and visual quality. This setting is optimized for web performance and Google PageSpeed Insights.

- **80 (default)**: Recommended for most use cases - great quality with smaller file sizes
- **85-90**: Higher quality, larger files - use for photography portfolios
- **70-75**: More aggressive compression - use when file size is critical

The `WEBP_METHOD` setting controls compression effort (CPU time vs file size):
- **6 (default)**: Maximum compression, slower encoding
- **4**: Good balance of speed and compression
- **0**: Fastest encoding, larger files

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
- `photo-400.webp` (400px wide)
- `photo-600.webp` (600px wide)
- `photo-800.webp` (800px wide)
- `photo-1200.webp` (1200px wide)

Note: The plugin will not upscale images, so if your source is 500px wide, only `photo.webp`, `photo-300.webp`, and `photo-400.webp` would be generated.

## Integration with HTML

You can use the generated responsive images in your templates:

```html
<picture>
  <source srcset="/static/images/photo-300.webp" media="(max-width: 400px)">
  <source srcset="/static/images/photo-400.webp" media="(max-width: 600px)">
  <source srcset="/static/images/photo-600.webp" media="(max-width: 800px)">
  <source srcset="/static/images/photo-800.webp" media="(max-width: 1000px)">
  <source srcset="/static/images/photo-1200.webp" media="(max-width: 1400px)">
  <img src="/static/images/photo.webp" alt="Description" loading="lazy"
       width="1200" height="800">
</picture>
```

### Best Practices for Google PageSpeed Insights

To maximize your PageSpeed score:

1. **Match display size to image size**: Use the `<picture>` element with appropriate media queries to serve the right image size for each viewport
2. **Specify width and height**: Always include `width` and `height` attributes on `<img>` tags to prevent layout shifts (CLS)
3. **Use lazy loading**: Add `loading="lazy"` to defer offscreen images
4. **Optimize for actual display**: If an image displays at 370px wide, use the 400px variant (not the 600px or larger)

Example for an image displayed at ~370px wide on mobile and ~590px on tablet:

```html
<picture>
  <source srcset="/static/images/hero-400.webp" media="(max-width: 600px)">
  <source srcset="/static/images/hero-600.webp" media="(max-width: 900px)">
  <img src="/static/images/hero-800.webp" alt="Hero image" loading="lazy"
       width="800" height="600">
</picture>
```

### Customizing Responsive Sizes

If you need different sizes to match your specific design, customize `WEBP_RESPONSIVE_SIZES`:

```python
# For images commonly displayed at 370px and 590px
WEBP_RESPONSIVE_SIZES = [370, 590, 800, 1200]
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
