import argparse
import os
import shutil
import sys

# List of image and video file extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
video_extensions = ['.mp', '.mp4', '.avi', '.mkv']


def copy_media_files(source_dir, destination_dir):
    num_of_video_image_files = 0
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            # print(f'file_extension: {file_extension}')
            if (file_extension in image_extensions) or (file_extension in video_extensions):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_dir, os.path.basename(file))

                destination_folder = os.path.dirname(destination_path)
                os.makedirs(destination_folder, exist_ok=True)

                shutil.copy2(source_path, destination_folder)
                print(f"Copied: {source_path} -> {destination_path}")
                num_of_video_image_files += 1

    print(f'num_of_video_image_files found: {str(num_of_video_image_files)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find picture and video files in a directory and its subdirectories. "
                    "Then copy the files to a folder. The script was orignaly written to "
                    "copy media files from folders downloaded from google takeout."
                    "Command usage: python move_image_video_to_folder.py -s <SOURCE_DIRECTORY> -d <DESTINATION_DIRECTORY>"
                    "Command example: python move_image_video_to_folder.py -s aaaMoveImagesVideos -d aaaMoveImagesVideos_OUT2")
    parser.add_argument('--source_directory', '-s', dest="source_directory",
                        help='Path to parent directory containing picture and video files to copy.')
    parser.add_argument('--destination_directory', '-d',  dest="destination_directory",
                        help='Path to folder where the files should be copied to.'
                             'The script will create the folder, if it has not already been created.')
    args = parser.parse_args()

    source_directory = args.source_directory
    if not source_directory or not os.path.exists(source_directory):
        sys.exit(f'Path ({source_directory}) does not exist.  Exiting ...')

    destination_directory = args.destination_directory
    if not os.path.exists(destination_directory):
        try:
            os.makedirs(destination_directory, exist_ok=True)
            print(f'{source_directory} has been created.')
        except:
            print(f'Failed to create {destination_directory}')

    sys.exit(copy_media_files(source_directory, destination_directory))
