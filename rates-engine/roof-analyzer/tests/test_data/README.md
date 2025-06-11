# Test Data Directory

This directory contains sample images for testing the roof analysis pipeline.

## Images

### sample_roof.jpg
A clear satellite image of a residential roof used for testing the image processing pipeline. This image is used in the `test_individual_components` test to verify the segmentation and enhancement functionality works correctly.

## Usage

The test images in this directory are used by:
1. `test_full_pipeline.py` - For testing the complete pipeline from address to processed roof
2. Unit tests that need sample roof images

## Adding New Test Images

When adding new test images:
1. Use clear, high-resolution satellite images
2. Include a mix of roof types (flat, pitched, complex)
3. Document the source and any relevant details in this README
4. Use descriptive filenames 