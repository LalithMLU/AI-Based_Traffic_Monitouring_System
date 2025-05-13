import os
import shutil
import datetime
import random

def split_dataset(images_folder, labels_folder, output_folder, train_ratio=0.8, test_ratio=0.1, valid_ratio=0.1):
    # Get today's date to name the main folder
    today_date = datetime.datetime.now().strftime("%d-%b-%Y")
    
    # Create main output folder with date
    main_folder_name = os.path.join(output_folder, f"no_helmet_detection{today_date}")
    os.makedirs(main_folder_name, exist_ok=True)
    
    # Create subfolders for train, test, and valid splits
    subfolders = ['train', 'test', 'valid']
    for folder in subfolders:
        os.makedirs(os.path.join(main_folder_name, folder, 'images'), exist_ok=True)
        os.makedirs(os.path.join(main_folder_name, folder, 'labels'), exist_ok=True)
        
    # Get list of image files and filter to only those with matching annotation files
    image_files = sorted([f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))])
    matched_files = [
        f for f in image_files 
        if os.path.exists(os.path.join(labels_folder, f.replace(".jpg", ".txt"))) or 
           os.path.exists(os.path.join(labels_folder, f.replace(".jpeg", ".txt")))
    ]
    
    # Shuffle matched files to randomize the dataset
    random.shuffle(matched_files)
    
    # Calculate split sizes
    total_files = len(matched_files)
    train_size = int(train_ratio * total_files)
    test_size = int(test_ratio * total_files)
    valid_size = total_files - train_size - test_size
    
    # Split the dataset into train, test, and valid sets
    splits = {
        'train': matched_files[:train_size],
        'test': matched_files[train_size:train_size + test_size],
        'valid': matched_files[train_size + test_size:]
    }
    
    # Copy files to their respective folders
    for split, files in splits.items():
        for image_file in files:
            image_src = os.path.join(images_folder, image_file)
            
            # Determine the label source file based on the image file extension
            if os.path.exists(os.path.join(labels_folder, image_file.replace(".jpg", ".txt"))):
                label_src = os.path.join(labels_folder, image_file.replace(".jpg", ".txt"))
            elif os.path.exists(os.path.join(labels_folder, image_file.replace(".jpeg", ".txt"))):
                label_src = os.path.join(labels_folder, image_file.replace(".jpeg", ".txt"))
            else:
                continue  # Skip if no matching label file is found
            
            image_dest = os.path.join(main_folder_name, split, 'images', image_file)
            label_dest = os.path.join(main_folder_name, split, 'labels', os.path.basename(label_src))
            
            # Copy the image and annotation file to the destination folder
            shutil.copy(image_src, image_dest)
            shutil.copy(label_src, label_dest)
        
        print(f"{split.capitalize()} set: Copied {len(files)} files.")

    print("Data splitting completed successfully.")

# Usage
images_folder = "G:\\Insulator_defects\\traffic_images"
labels_folder = "G:\\Insulator_defects\\traffic_labels"
output_folder = "G:\\Insulator_defects\\dataset"  # Main folder where the split dataset will be created

split_dataset(images_folder, labels_folder, output_folder)
