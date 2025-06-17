# Workplan

## Tool description

A tool to analyze roof quality, age, shape, and material using satellite imagery. The end goal is for a user to be able to input any Canadian address and it will be able to make a determination across the 4 factors.

## Tool workflow

1. User enters an address
2. Address is turned in to lat, lon
3. Lat, lon is used to get satellite imagery of the roof of a house hold
4. Image is cropped to standard size
5. Image is passess through an LLM
6. LLM determines roof quality ("good|worn|patched"), shape ("gable|hip|flat|hip and valley|pyramid|dormer|other"), material ("asphalt_shingle|metal|clay_tile|slate|wood|other"), age range in years ("0-5|6-15|16-30|>30"), and confidence in it's prediction (0% to 100%)
7. Tool outputs LLM predictions in JSON format

## Development 
### PHASE 1: DATA PIPELINE & PREPROCESSING
1. Geocoding
Input: Canadian address

Tool: Google Maps Geocoding API

Output: Latitude and longitude coordinates

2. Satellite Imagery Retrieval
Input: Lat/lon coordinates

Tool: Sentinel-2 API

Output: Top-down image of the roof

Note: You may need to crop/zoom to fit a house-sized bounding box.

3. Image Preprocessing
Tasks:

Normalize image sizes (e.g., 256x256 or 512x512)

Enhance contrast or denoise if needed

Optional: Use semantic segmentation to isolate the roof

### PHASE 2: MODEL DEVELOPMENT
4. Model Selection
Use multimodal LLMs (e.g., Gemini Pro Vision, GPT-4o) that accept image + prompt:

Prompt: “Describe the roof’s quality, estimated age, shape, and material.”

