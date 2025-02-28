# AugmentX
Simple program for augmentation annotated images.
Tool for dataset augmentation that automatically preserves YOLO annotations. Create augmented versions of your annotated images while maintaining correct bounding box coordinates.

## Features
- Automatic Annotation Update: The annotations of the original images are automatically adjusted along with the augmented images, eliminating the need for manual re-annotation.
- Image augmentation with various transformations:
  - Horizontal and vertical flips
  - Rotations (90°, 180°, 270°)
  - Brightness and contrast adjustments
- Integrated LabelImg support for image annotation
- Only YOLO format annotation support
- Real-time preview of augmentation settings

## Installation
1. Clone the repository:
```bash
git clone https://github.com/XAlthor/AugmentX.git
```
2. Navigate to the project directory:
```bash
cd AugmentX
```
3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate  # For Windows
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python mainwindow.py
```
2. Select input folder with annotated images
3. Select output folder for augmented images
4. Choose desired augmentations
5. Click "Apply Augmentation" to generate augmented images
6. Use "Open in LabelImg" to view and annotate images

## Note

The application requires labelImg to be installed (included in requirements.txt). If you encounter any issues with labelImg, you can install it separately:
```bash
pip install labelImg
```
