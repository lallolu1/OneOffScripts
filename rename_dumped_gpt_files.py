import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def get_windows_path(win_path):
    path_rel_to_mount = win_path
    if str(win_path).startswith('/'):
        path_rel_to_mount = str(win_path).lstrip('/')
    elif str(win_path).startswith('\\'):
        path_rel_to_mount = str(win_path).lstrip('\\')

    path_rel_to_mount = path_rel_to_mount.split('/', 1)
    partition_xml_path = path_rel_to_mount[0] + ':/' + path_rel_to_mount[1]
    return partition_xml_path


def xml_content(partition_xml):
    try:
        tree = ET.parse(partition_xml)
        root = tree.getroot()
    except BaseException as err:
        print(f'{err}')
        return

    xml_list = []
    for child in root:
        if not child.tag == 'partition':
            continue
        xml_list.append(child.attrib)
        child.attrib['start_sector_hex'] = hex(int(child.attrib.get('start_sector')))

    return xml_list


def rename(xml_list, in_folder):
    path_content = list(Path(in_folder).glob('*'))
    path_content = [str(x) for x in path_content]
    if not path_content:
        print(f'{in_folder} is empty. No rename done.')
        return
    for p in path_content:
        for row in xml_list:
            if row.get('num_partition_sectors') in p and row.get('start_sector_hex') in p:
                new_file_name = Path(in_folder, row.get("label") + ".bin")

                # print(f'mv {Path(p).name} {new_file_name.name}')  # Simple
                # print(f'mv {p} {new_file_name}')  # full path

                print(f'Renaming {p} to {new_file_name}')
                try:
                    os.rename(p, str(new_file_name))
                except BaseException as err:
                    print(f'{err}')


def main():
    parser = argparse.ArgumentParser(
        description='Rename dumped gpt files to partition.img.')
    parser.add_argument('--partition_xml', dest="partition_xml",
                        help='Path to COM3_PartitionsList.xml.')
    parser.add_argument('--in_folder', dest="in_folder",
                        help='Path to folder containing partion '
                             'files to be renamed ')

    args = parser.parse_args()

    if os.name == 'nt':  # windows == 'nt'
        partition_xml = get_windows_path(args.partition_xml)
        in_folder = get_windows_path(args.in_folder)

    xml_list = xml_content(partition_xml)
    if xml_list:
        rename(xml_list, in_folder)


if __name__=='__main__':
    main()
