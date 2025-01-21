# This Python file uses the following encoding: utf-8
import sys
import os
import cv2
import numpy as np
from pathlib import Path
import albumentations as A
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import Qt, QThread, Signal

from ui_form import Ui_MainWindow

class AugmentationImages(QThread):
    """Thread for performing image augmentation"""
    # Signals for updating UI
    progress = Signal(int)  # Progress of operation (0-100%)
    status = Signal(str)    # Current status of operation
    finished = Signal()     # Signal for completion of operation
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = self.parent()
    
    def _create_transforms(self):
        """Creates all transformations based on selected settings"""
        transforms = []
        
        # Geometric transformations
        h_flip = self.main_window.ui.flip_horizontal.isChecked()
        v_flip = self.main_window.ui.flip_vertical.isChecked()
        rotate = self.main_window.ui.rotate.isChecked()
        
        # Reflections
        if h_flip:
            transforms.append(('h_flip', A.HorizontalFlip(p=1.0)))
        if v_flip:
            transforms.append(('v_flip', A.VerticalFlip(p=1.0)))
        
        # Rotations
        if rotate:
            transforms.extend([
                ('rot90', A.SafeRotate(limit=(90, 90), border_mode=cv2.BORDER_CONSTANT, p=1.0)),
                ('rot180', A.SafeRotate(limit=(180, 180), border_mode=cv2.BORDER_CONSTANT, p=1.0)),
                ('rot270', A.SafeRotate(limit=(270, 270), border_mode=cv2.BORDER_CONSTANT, p=1.0))
            ])
        
        # Brightness and contrast
        brightness = self.main_window.ui.brightness_check.isChecked()
        contrast = self.main_window.ui.contrast_check.isChecked()
        
        if brightness:
            transforms.append(('brightness', A.RandomBrightnessContrast(
                brightness_limit=(-0.1, 0.1),
                contrast_limit=0,
                p=1.0
            )))
        
        if contrast:
            transforms.append(('contrast', A.RandomBrightnessContrast(
                brightness_limit=0,
                contrast_limit=(-0.1, 0.1),
                p=1.0
            )))
        
        return transforms
    
    def _save_augmented_image(self, img, bboxes, class_labels, output_path, annotation_path):
        """Saves augmented image and its annotations"""
        cv2.imwrite(str(output_path), img)
        
        with open(annotation_path, 'w') as f:
            for bbox, class_id in zip(bboxes, class_labels):
                f.write(f"{int(class_id)} {' '.join(map(str, bbox))}\n")
    
    def _process_single_image(self, img_path, transforms_to_apply, augmented_dir):
        """Processes a single image by applying all selected transformations"""
        # Loading image
        img = cv2.imread(str(img_path))
        if img is None:
            return
        
        # Check for annotation file
        annotation_path = img_path.with_suffix('.txt')
        if not annotation_path.exists():
            self.status.emit(f"Warning: annotation file not found for {img_path.name}")
            return
            
        # Read annotations
        bboxes = []
        class_labels = []
        with open(annotation_path, 'r') as f:
            for line in f:
                class_id, x_center, y_center, w, h = map(float, line.strip().split())
                bboxes.append([x_center, y_center, w, h])
                class_labels.append(int(class_id))
        
        # Apply geometric transformations
        for suffix, transform in transforms_to_apply:
            if self.isInterruptionRequested():
                return
            
            if not ('brightness' in suffix or 'contrast' in suffix):
                transformed = transform(image=img, bboxes=bboxes)
                transformed_img = transformed['image']
                transformed_bboxes = transformed['bboxes']
            else:
                transformed_img = transform(image=img)['image']
                transformed_bboxes = bboxes
            
            # Save augmented image and annotations
            output_name = f"{img_path.stem}_{suffix}{img_path.suffix}"
            output_path = augmented_dir / output_name
            annotation_output_path = output_path.with_suffix('.txt')
            
            self._save_augmented_image(
                transformed_img,
                transformed_bboxes,
                class_labels,
                output_path,
                annotation_output_path
            )
    
    def run(self):
        """Main processing loop"""
        if not hasattr(self.main_window, 'input_folder') or not hasattr(self.main_window, 'output_folder'):
            self.status.emit("Error: Input or output folder not selected")
            return
            
        input_dir = Path(self.main_window.input_folder)
        output_dir = Path(self.main_window.output_folder)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Get all image files
        image_files = list(input_dir.glob('*.jpg')) + list(input_dir.glob('*.png'))
        if not image_files:
            self.status.emit("No image files found in input directory")
            return
            
        # Create transformations
        transforms_to_apply = self._create_transforms()
        if not transforms_to_apply:
            self.status.emit("No transformations selected")
            return
            
        # Process each image
        total_images = len(image_files)
        for i, img_path in enumerate(image_files, 1):
            if self.isInterruptionRequested():
                break
                
            self.status.emit(f"Processing {img_path.name}")
            self._process_single_image(img_path, transforms_to_apply, output_dir)
            self.progress.emit(int(i * 100 / total_images))
            
        self.status.emit("Processing complete")
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize variables for paths
        #self.input_folder = ""
        #self.output_folder = ""
        
        # Connect signals
        self.ui.input_folder_button.clicked.connect(self.select_input_folder)
        self.ui.output_folder_button.clicked.connect(self.select_output_folder)
        self.ui.apply_button.clicked.connect(self.start_augmentation)
        
        # Connect update of information when checkboxes change
        self.ui.flip_horizontal.stateChanged.connect(self.update_augmentation_info)
        self.ui.flip_vertical.stateChanged.connect(self.update_augmentation_info)
        self.ui.rotate.stateChanged.connect(self.update_augmentation_info)
        self.ui.brightness_check.stateChanged.connect(self.update_augmentation_info)
        self.ui.contrast_check.stateChanged.connect(self.update_augmentation_info)
        
        self.update_augmentation_info()  # Initialize information
        
    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder = folder
            self.ui.input_folder_label.setText(f"Input: {folder}")
            
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.ui.output_folder_label.setText(f"Output: {folder}")
            
    def start_augmentation(self):
        """Start augmentation process in a separate thread"""
        if not self.input_folder or not self.output_folder:
            self.ui.statusbar.showMessage("Please select both input and output folders")
            return
            
        # Create and configure the thread
        self.augmentation_thread = AugmentationImages(self)
        self.augmentation_thread.progress.connect(self.update_progress)
        self.augmentation_thread.status.connect(self.update_status)
        self.augmentation_thread.finished.connect(self.augmentation_finished)
        
        # Disable UI elements
        self.ui.apply_button.setEnabled(False)
        self.ui.progress_bar.setValue(0)
        
        # Start processing
        self.augmentation_thread.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.ui.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status"""
        self.ui.statusbar.showMessage(message)
        
    def augmentation_finished(self):
        """Handle completion of augmentation"""
        self.ui.apply_button.setEnabled(True)
        
    def update_augmentation_info(self):
        """Update information about number and types of transformations"""
        transforms = []
        if self.ui.flip_horizontal.isChecked():
            transforms.append("horizontal flip")
        if self.ui.flip_vertical.isChecked():
            transforms.append("vertical flip")
        if self.ui.rotate.isChecked():
            transforms.append("90°, 180°, 270° rotations")
        if self.ui.brightness_check.isChecked():
            transforms.append("brightness adjustment")
        if self.ui.contrast_check.isChecked():
            transforms.append("contrast adjustment")
            
        if transforms:
            info = f"Selected transformations: {', '.join(transforms)}"
        else:
            info = "No transformations selected"
            
        self.ui.augmentation_info.setText(info)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())