import argparse
import hashlib
import os
import random
import shutil
import sys
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    # __import__(package)
    from tqdm import tqdm
except (ModuleNotFoundError, ImportError) as err:
    print(f'{err}')
    import pip
    pip.main(['install', 'tqdm'])
    # os.system("pip install " + package)
    from tqdm import tqdm

# List of image and video file extensions
# image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.dng', '.tiff', '.heif']
# video_extensions = ['.mp', '.mp4', '.avi', '.mkv', '.mpeg-4', '.h.264', '.h.265', '.m4v', '.mov']
file_extension_to_ignore = ['.json', '.xml', '.html', '.htm', '.xls', '.xlsx', '.doc', '.docx',
                            '.ppt', '.pdf', '.txt', '.zip']


def rename_file(file):
    file_parts = os.path.splitext(file)
    file_name = file_parts[0]
    file_extension = file_parts[1]
    new_name = file_name + '_' + str(random.randint(1, 100)) + file_extension

    return new_name


def get_new_destination_filename_if_not_same_file_to_be_copied(file_to_copy, file_with_same_name_already_in_destination,
                                                               destination_dir):
    hash_file1 = hashlib.md5(open(file_to_copy, 'rb').read()).hexdigest()
    hash_file2 = hashlib.md5(open(file_with_same_name_already_in_destination, 'rb').read()).hexdigest()

    new_destination_file_name = ''
    if hash_file1 != hash_file2:
        new_destination_file_name = os.path.join(destination_dir,
                                                 rename_file(os.path.basename(file_to_copy)))
        print(f'Files with same name but different content found - {file_to_copy}\n'
              f'It will be renamed in destination to {new_destination_file_name}')

    return new_destination_file_name


def copy_files(root, file, destination_dir, renamed_files, files_skipped_copying):
    # renamed_files = []
    # files_skipped_copying = []
    file_has_extension_that_should_be_copied = True
    file_copied_to_destination = False
    file_extension = os.path.splitext(file)[1].lower()
    # if (file_extension in image_extensions) or (file_extension in video_extensions):
    if file_extension not in file_extension_to_ignore:
        source_path = os.path.join(root, file)
        destination_path = os.path.join(destination_dir, os.path.basename(file))

        if not os.path.exists(destination_path):
            shutil.copy2(source_path, destination_dir)
            # print(f"Copied: {source_path} -> {destination_path}")
            # num_of_video_image_files += 1
            file_copied_to_destination = True
        else:
            # If path exist but has different md5, then it is not the same file
            # Check if new file is the exact one already copied
            new_destination_path = get_new_destination_filename_if_not_same_file_to_be_copied(source_path,
                                                                                              destination_path,
                                                                                              destination_dir)
            if new_destination_path:
                shutil.copy2(source_path, new_destination_path)
                file_copied_to_destination = True
                renamed_files.append(new_destination_path + '\n')
            else:
                print(f'{destination_path} has already been copied from another folder. Skipping ...')
                files_skipped_copying.append(destination_path + '\n')
    else:
        file_has_extension_that_should_be_copied = False

    return file_copied_to_destination, file_has_extension_that_should_be_copied, renamed_files, files_skipped_copying


def copy_media_files(source_dir, destination_dir):
    total_num_of_video_image_files_copied = 0
    number_of_files_not_copied = 0
    num_of_files = 0  # Usig this since len(files) just returns 1
    renamed_files = []
    files_skipped_copying = []
    for root, _, files in os.walk(source_dir):
        with ThreadPoolExecutor(max_workers=16) as executor:
            future_results = []
            for file in files:
                num_of_files += 1
                future_results.append(
                    executor.submit(copy_files, root, file, destination_dir, renamed_files, files_skipped_copying))
            for future in tqdm(as_completed(future_results),
                               total=len(future_results)):

                try:
                    file_copied_to_destination, file_has_extension_that_should_be_copied, \
                        renamed_files, files_skipped_copying = future.result()
                    if file_has_extension_that_should_be_copied:
                        if not file_copied_to_destination:
                            number_of_files_not_copied += 1
                        else:
                            total_num_of_video_image_files_copied += 1
                except UnicodeEncodeError as err:
                    print(f'{err}')

    print('\n\n' + ('#' * 35) + ' SUMMARY ' + ('#' * 35))
    print(f'Total number of ALL files (media/non-media) found in folder and sub-folders: {num_of_files}')
    print(f'Total number of renamed media files for destination directory: {len(renamed_files)}')
    print(f'Total number of video/image files copied: {total_num_of_video_image_files_copied}')
    print(f'Total number of video/image skipped since they were already copied: {number_of_files_not_copied}\n')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # write files in destination directory that were renamed to a
    # file in the same directory as the script
    if renamed_files:
        renamed_files_list = os.path.join(script_dir, 'renamed_files_list.txt')
        renamed_files.sort()
        with open(renamed_files_list, 'w') as df:
            df.writelines(renamed_files)
            print(f'files in destination directory that were renamed have been written to - {renamed_files_list}')

    # write to a file, list of files that were skipped since they have already been copied
    if files_skipped_copying:
        skipped_files = os.path.join(script_dir, 'files_skipped_copying.txt')
        files_skipped_copying.sort()
        with open(skipped_files, 'w') as df:
            df.writelines(files_skipped_copying)
            print(f'files that were not copied since they have already been copied have been written to - {skipped_files}')

    # get the end time
    end_time = time.time()

    # get the execution time
    elapsed_time = end_time - start_time
    print('\nExecution time:', elapsed_time, 'seconds')
    print(('#' * 80))


if __name__ == "__main__":
    # get the start time
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Find picture and video files in a directory and its subdirectories. "
                    "Then copy the files to a folder. The script was originally written to "
                    "copy media files from folders downloaded from google takeout."
                    "Command usage: python move_image_video_to_folder.py -s <SOURCE_DIRECTORY> -d <DESTINATION_DIRECTORY>"
                    "Command example: python move_image_video_to_folder.py -s aaaMoveImagesVideos -d aaaMoveImagesVideos_OUT2")
    parser.add_argument('--source_directory', '-s', dest="source_directory",
                        help='Path to parent directory containing picture and video files to copy.')
    parser.add_argument('--destination_directory', '-d', dest="destination_directory",
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
            print(f'{source_directory} has been created.\n')
        except:
            print(f'Failed to create {destination_directory}')

    sys.exit(copy_media_files(source_directory, destination_directory))
