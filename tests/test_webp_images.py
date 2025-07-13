import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

# Mock the dependencies that might not be available during testing
import sys
sys.modules['pelican'] = MagicMock()
sys.modules['pelican.signals'] = MagicMock()

from webp_images.webp_images import WebPProcessor, process_webp_images

def create_test_image(path, size=(1200, 800), format="JPEG"):
    """Helper to create test images"""
    img = Image.new("RGB", size, color="red")
    img.save(path, format)
    return path

class TestWebPProcessor:
    
    def test_init_with_default_settings(self):
        """Test WebPProcessor initialization with default settings"""
        pelican_mock = Mock()
        pelican_mock.settings = {}
        
        processor = WebPProcessor(pelican_mock)
        
        assert processor.image_source_dir == Path('portfolio/static/images')
        assert processor.supported_exts == [".jpg", ".jpeg", ".png", ".webp"]
        assert processor.responsive_sizes == [300, 600, 1200]
        assert processor.quality == 85
        assert processor.skip_dirs == ['thumbnails']
        assert processor.process_original is True
    
    def test_init_with_custom_settings(self):
        """Test WebPProcessor initialization with custom settings"""
        pelican_mock = Mock()
        pelican_mock.settings = {
            'WEBP_SOURCE_DIR': 'custom/path',
            'OUTPUT_PATH': 'custom/output',
            'WEBP_RESPONSIVE_SIZES': [400, 800],
            'WEBP_QUALITY': 95,
            'WEBP_SKIP_DIRS': ['thumbs', 'cache'],
            'WEBP_PROCESS_ORIGINAL': False
        }
        
        processor = WebPProcessor(pelican_mock)
        
        assert processor.image_source_dir == Path('custom/path')
        assert processor.responsive_sizes == [400, 800]
        assert processor.quality == 95
        assert processor.skip_dirs == ['thumbs', 'cache']
        assert processor.process_original is False
    
    def test_should_skip_image(self):
        """Test image skipping logic"""
        pelican_mock = Mock()
        pelican_mock.settings = {'WEBP_SKIP_DIRS': ['thumbnails']}
        
        processor = WebPProcessor(pelican_mock)
        
        # Should skip images in thumbnails directory
        thumbnail_path = Path('/test/thumbnails/image.jpg')
        assert processor.should_skip_image(thumbnail_path) is True
        
        # Should skip already resized images
        resized_path = Path('/test/image-300.jpg')
        assert processor.should_skip_image(resized_path) is True
        
        # Should not skip normal images
        normal_path = Path('/test/image.jpg')
        assert processor.should_skip_image(normal_path) is False
    
    def test_needs_processing_new_file(self):
        """Test needs_processing for new files"""
        pelican_mock = Mock()
        pelican_mock.settings = {}
        
        processor = WebPProcessor(pelican_mock)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.jpg"
            output_path = Path(tmpdir) / "output.webp"
            
            create_test_image(source_path)
            
            # Output doesn't exist, should need processing
            assert processor.needs_processing(source_path, [output_path]) is True
    
    def test_needs_processing_existing_newer_file(self):
        """Test needs_processing for existing newer output file"""
        pelican_mock = Mock()
        pelican_mock.settings = {}
        
        processor = WebPProcessor(pelican_mock)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.jpg"
            output_path = Path(tmpdir) / "output.webp"
            
            create_test_image(source_path)
            
            # Create output file after source
            import time
            time.sleep(0.1)
            output_path.touch()
            
            # Output is newer, should not need processing
            assert processor.needs_processing(source_path, [output_path]) is False
    
    def test_process_image_success(self):
        """Test successful image processing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pelican_mock = Mock()
            pelican_mock.settings = {
                'OUTPUT_PATH': tmpdir,
                'WEBP_RESPONSIVE_SIZES': [300, 600]
            }
            
            processor = WebPProcessor(pelican_mock)
            processor.image_source_dir = Path(tmpdir) / "source"
            processor.image_output_dir = Path(tmpdir) / "output"
            
            # Create source directory and image
            processor.image_source_dir.mkdir()
            source_image = processor.image_source_dir / "test.jpg"
            create_test_image(source_image, size=(1200, 800))
            
            # Process the image
            processed_count = processor.process_image(source_image)
            
            # Should process original + 2 responsive sizes
            assert processed_count == 3
            
            # Check output files exist
            output_dir = processor.image_output_dir
            assert (output_dir / "test.webp").exists()
            assert (output_dir / "test-300.webp").exists()
            assert (output_dir / "test-600.webp").exists()
    
    def test_process_image_no_upscaling(self):
        """Test that images are not upscaled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pelican_mock = Mock()
            pelican_mock.settings = {
                'OUTPUT_PATH': tmpdir,
                'WEBP_RESPONSIVE_SIZES': [300, 600, 1200]
            }
            
            processor = WebPProcessor(pelican_mock)
            processor.image_source_dir = Path(tmpdir) / "source"
            processor.image_output_dir = Path(tmpdir) / "output"
            
            # Create small source image
            processor.image_source_dir.mkdir()
            source_image = processor.image_source_dir / "small.jpg"
            create_test_image(source_image, size=(400, 300))  # Smaller than responsive sizes
            
            # Process the image
            processed_count = processor.process_image(source_image)
            
            # Should only process original + 300px version (not 600px or 1200px)
            assert processed_count == 2
            
            output_dir = processor.image_output_dir
            assert (output_dir / "small.webp").exists()
            assert (output_dir / "small-300.webp").exists()
            assert not (output_dir / "small-600.webp").exists()
            assert not (output_dir / "small-1200.webp").exists()
    
    def test_process_images_with_files(self):
        """Test processing multiple images"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pelican_mock = Mock()
            pelican_mock.settings = {
                'OUTPUT_PATH': tmpdir,
                'WEBP_RESPONSIVE_SIZES': [300]
            }
            
            processor = WebPProcessor(pelican_mock)
            processor.image_source_dir = Path(tmpdir) / "source"
            processor.image_output_dir = Path(tmpdir) / "output"
            
            # Create source directory and images
            processor.image_source_dir.mkdir()
            create_test_image(processor.image_source_dir / "image1.jpg")
            create_test_image(processor.image_source_dir / "image2.png")
            create_test_image(processor.image_source_dir / "skip-300.jpg")  # Should be skipped
            
            # Create thumbnails directory with image (should be skipped)
            thumbs_dir = processor.image_source_dir / "thumbnails"
            thumbs_dir.mkdir()
            create_test_image(thumbs_dir / "thumb.jpg")
            
            # Process images
            processor.process_images()
            
            # Check outputs
            output_dir = processor.image_output_dir
            assert (output_dir / "image1.webp").exists()
            assert (output_dir / "image1-300.webp").exists()
            assert (output_dir / "image2.webp").exists()
            assert (output_dir / "image2-300.webp").exists()
            
            # Should not process skipped files
            assert not (output_dir / "skip-300.webp").exists()
            assert not (output_dir / "thumbnails" / "thumb.webp").exists()
    
    def test_process_images_missing_source_dir(self):
        """Test handling of missing source directory"""
        pelican_mock = Mock()
        pelican_mock.settings = {}
        
        processor = WebPProcessor(pelican_mock)
        processor.image_source_dir = Path("/nonexistent")
        
        # Should not raise exception
        processor.process_images()

def test_process_webp_images_signal_handler():
    """Test the signal handler function"""
    pelican_mock = Mock()
    pelican_mock.settings = {}
    
    with patch('webp_images.webp_images.WebPProcessor') as mock_processor_class:
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        process_webp_images(pelican_mock)
        
        # Should create processor and call process_images
        mock_processor_class.assert_called_once_with(pelican_mock)
        mock_processor.process_images.assert_called_once()
