# This Python file uses the following encoding: utf-8
import sys
import os
import cv2
import shutil
#import labelimg
from pathlib import Path
import albumentations as A
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QThread, Signal

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
        img = cv2.imread(str(img_path))
        if img is None:
            return

        annotation_path = img_path.with_suffix('.txt')
        bboxes = []
        class_labels = []

        if annotation_path.exists():
            with open(annotation_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_labels.append(int(parts[0]))
                        bboxes.append([float(x) for x in parts[1:]])

        # Geometric transformations (with bbox handling)
        for suffix, transform in transforms_to_apply:
            if self.isInterruptionRequested():
                return

            if not ('brightness' in suffix or 'contrast' in suffix):
                transform = A.Compose([transform],
                    bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
                try:
                    transformed = transform(image=img, bboxes=bboxes, class_labels=class_labels)
                    output_img_path = augmented_dir / f"{img_path.stem}_aug_{suffix}{img_path.suffix}"
                    output_ann_path = augmented_dir / f"{img_path.stem}_aug_{suffix}.txt"
                    self._save_augmented_image(transformed['image'], transformed['bboxes'],
                                             transformed['class_labels'], output_img_path, output_ann_path)
                except Exception as e:
                    print(f"Error during geometric transformation: {str(e)}")
                    continue

        # Brightness and contrast (without bbox handling)
        for suffix, transform in transforms_to_apply:
            if self.isInterruptionRequested():
                return

            if 'brightness' in suffix or 'contrast' in suffix:
                transform = A.Compose([transform])  # No bbox_params here
                try:
                    transformed = transform(image=img)
                    output_img_path = augmented_dir / f"{img_path.stem}_aug_{suffix}{img_path.suffix}"
                    cv2.imwrite(str(output_img_path), transformed['image'])

                    if annotation_path.exists():
                        output_ann_path = augmented_dir / f"{img_path.stem}_aug_{suffix}.txt"
                        shutil.copy2(annotation_path, output_ann_path)
                except Exception as e:
                    print(f"Error during brightness/contrast change: {str(e)}")

    def run(self):
        """Main method for performing augmentation"""
        try:
            # Create output directory
            augmented_dir = Path(self.main_window.output_folder)
            augmented_dir.mkdir(parents=True, exist_ok=True)

            # Copy classes.txt if it exists
            input_classes_file = Path(self.main_window.input_folder) / "classes.txt"
            if input_classes_file.exists():
                shutil.copy2(input_classes_file, augmented_dir / "classes.txt")
                self.status.emit("Copied classes.txt to output directory")

            # Get list of images
            image_files = list(Path(self.main_window.input_folder).glob("*.jpg")) + \
                         list(Path(self.main_window.input_folder).glob("*.png")) + \
                         list(Path(self.main_window.input_folder).glob("*.jpeg"))

            # Create list of transformations
            transforms_to_apply = self._create_transforms()

            # Process images
            total_files = len(image_files)

            for i, img_path in enumerate(image_files):
                if self.isInterruptionRequested():
                    break

                self.status.emit(f"Processing {img_path.name}")
                self.progress.emit(int((i / total_files) * 100))

                self._process_single_image(img_path, transforms_to_apply, augmented_dir)

            if not self.isInterruptionRequested():
                self.progress.emit(100)
                self.status.emit("Augmentation completed")
            else:
                self.status.emit("Augmentation interrupted")

        except Exception as e:
            self.status.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize variables for paths
        self.input_folder = ""
        self.output_folder = ""

        # Connect signals
        self.ui.input_folder_button.clicked.connect(self.select_input_folder)
        self.ui.output_folder_button.clicked.connect(self.select_output_folder)
        self.ui.apply_button.clicked.connect(self.start_augmentation)
        self.ui.launch_labelimg_button.clicked.connect(self.launch_labelimg)

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
        augmentations = []
        new_images = 0
        
        # Map checkboxes to their descriptions and image counts
        aug_map = {
            self.ui.flip_horizontal: ("Horizontal Flip", 1),
            self.ui.flip_vertical: ("Vertical Flip", 1),
            self.ui.rotate: ("Rotation (90°, 180°, 270°)", 3),
            self.ui.brightness_check: ("Brightness", 1),
            self.ui.contrast_check: ("Contrast", 1)
        }
        
        # Process checked augmentations
        for checkbox, (desc, count) in aug_map.items():
            if checkbox.isChecked():
                augmentations.append(f"{desc} (+{count})")
                new_images += count
        
        # Create info text
        info_text = "Selected augmentations:\n" if augmentations else "No augmentations selected"
        if augmentations:
            info_text += "\n".join(f"• {aug}" for aug in augmentations)
            info_text += f"\n\n{new_images} new images will be created"
            
        self.ui.augmentation_info.setText(info_text)


    def launch_labelimg(self):
        """Launch labelImg application in virtual environment"""
        try:
            # Get the virtual environment's Python interpreter path
            venv_python = os.path.join(os.path.dirname(sys.executable), 'python')
            
            # Import labelImg to get its location
            import labelImg
            labelimg_dir = os.path.dirname(labelImg.__file__)
            labelimg_main = os.path.join(labelimg_dir, 'labelImg.py')
            
            if not os.path.exists(labelimg_main):
                labelimg_main = os.path.join(labelimg_dir, 'labelImg', 'labelImg.py')
                if not os.path.exists(labelimg_main):
                    raise FileNotFoundError("Could not find labelImg.py")
            
            if hasattr(self, 'output_folder') and self.output_folder:
                command = f'"{venv_python}" "{labelimg_main}" "{self.output_folder}"'
            else:
                command = f'"{venv_python}" "{labelimg_main}"'

            # Use subprocess to run in background
            import subprocess
            subprocess.Popen(command, shell=True)
            self.ui.statusbar.showMessage("LabelImg launched successfully")

        except Exception as e:
            self.ui.statusbar.showMessage(f"Error launching labelImg: {str(e)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
