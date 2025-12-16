#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 BIN Merger - Merge multiple .bin files into a single file for flashing
This script merges bootloader.bin, partitions.bin, and firmware.bin into one file
with proper offsets for ESP32 SPI flash.

Usage:
    python3 merge_bin.py
    python3 merge_bin.py --output merged_fw.bin --bootloader boot.bin --partitions part.bin --firmware fw.bin
    python3 merge_bin.py --build-dir /path/to/build/dir
"""

import os
import sys
import argparse
from pathlib import Path

# Default offsets for ESP32 (in bytes)
DEFAULT_OFFSETS = {
    'bootloader': 0x1000,      # 4KB
    'partitions': 0x8000,      # 32KB
    'firmware': 0x10000,       # 64KB
}

# Default file names
DEFAULT_FILES = {
    'bootloader': 'bootloader.bin',
    'partitions': 'partitions.bin',
    'firmware': 'firmware.bin',
}

# Default build directory relative to script location
DEFAULT_BUILD_DIR = '../.pio/build/esp32dev'

class BinMerger:
    def __init__(self, output_path, bootloader_offset=0x1000, partitions_offset=0x8000, firmware_offset=0x10000):
        self.output_path = output_path
        self.offsets = {
            'bootloader': bootloader_offset,
            'partitions': partitions_offset,
            'firmware': firmware_offset,
        }
        self.merged_data = {}
    
    def read_binary_file(self, file_path):
        """Read binary file and return bytes"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            print(f"✓ Đọc: {file_path} ({len(data)} bytes)")
            return data
        except FileNotFoundError:
            print(f"✗ Lỗi: Không tìm thấy file {file_path}")
            return None
        except Exception as e:
            print(f"✗ Lỗi khi đọc {file_path}: {e}")
            return None
    
    def merge_files(self, bootloader_path, partitions_path, firmware_path):
        """Merge three binary files with proper offsets"""
        print("\n=== ESP32 BIN Merger ===\n")
        
        # Read all files
        bootloader_data = self.read_binary_file(bootloader_path)
        partitions_data = self.read_binary_file(partitions_path)
        firmware_data = self.read_binary_file(firmware_path)
        
        if not all([bootloader_data, partitions_data, firmware_data]):
            return False
        
        # Calculate total size
        max_offset = max(
            self.offsets['bootloader'] + len(bootloader_data),
            self.offsets['partitions'] + len(partitions_data),
            self.offsets['firmware'] + len(firmware_data),
        )
        
        # Create merged binary (fill with 0xFF like flash memory)
        merged = bytearray([0xFF] * max_offset)
        
        # Place each file at its offset
        print("\n=== Placing files at offsets ===")
        print(f"Bootloader at 0x{self.offsets['bootloader']:06X} ({self.offsets['bootloader']} bytes)")
        print(f"Partitions at 0x{self.offsets['partitions']:06X} ({self.offsets['partitions']} bytes)")
        print(f"Firmware at 0x{self.offsets['firmware']:06X} ({self.offsets['firmware']} bytes)")
        
        merged[self.offsets['bootloader']:self.offsets['bootloader'] + len(bootloader_data)] = bootloader_data
        merged[self.offsets['partitions']:self.offsets['partitions'] + len(partitions_data)] = partitions_data
        merged[self.offsets['firmware']:self.offsets['firmware'] + len(firmware_data)] = firmware_data
        
        # Write merged file
        try:
            with open(self.output_path, 'wb') as f:
                f.write(merged)
            print(f"\n✓ Ghép thành công: {self.output_path}")
            print(f"  Kích thước: {len(merged)} bytes ({len(merged) / (1024*1024):.2f} MB)")
            return True
        except Exception as e:
            print(f"\n✗ Lỗi khi ghi file: {e}")
            return False
    
    def get_flash_command(self):
        """Get esptool.py flash command"""
        return f"esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 {self.output_path}"


def main():
    parser = argparse.ArgumentParser(
        description='Merge multiple ESP32 .bin files into one file for flashing'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='merged_firmware.bin',
        help='Output merged binary file (default: merged_firmware.bin)'
    )
    
    parser.add_argument(
        '--build-dir', '-d',
        default=None,
        help=f'Build directory containing .bin files (default: {DEFAULT_BUILD_DIR})'
    )
    
    parser.add_argument(
        '--bootloader', '-b',
        default=None,
        help='Path to bootloader.bin (overrides build-dir)'
    )
    
    parser.add_argument(
        '--partitions', '-p',
        default=None,
        help='Path to partitions.bin (overrides build-dir)'
    )
    
    parser.add_argument(
        '--firmware', '-f',
        default=None,
        help='Path to firmware.bin (overrides build-dir)'
    )
    
    parser.add_argument(
        '--bootloader-offset',
        type=lambda x: int(x, 0),
        default=0x1000,
        help='Bootloader offset in hex (default: 0x1000)'
    )
    
    parser.add_argument(
        '--partitions-offset',
        type=lambda x: int(x, 0),
        default=0x8000,
        help='Partitions offset in hex (default: 0x8000)'
    )
    
    parser.add_argument(
        '--firmware-offset',
        type=lambda x: int(x, 0),
        default=0x10000,
        help='Firmware offset in hex (default: 0x10000)'
    )
    
    args = parser.parse_args()
    
    # Determine file paths
    script_dir = Path(__file__).parent
    
    # Determine build directory
    if args.build_dir:
        build_dir = Path(args.build_dir)
    else:
        build_dir = script_dir / DEFAULT_BUILD_DIR
    
    # If build_dir doesn't exist, try to find it from workspace root
    if not build_dir.exists():
        workspace_build = script_dir.parent.parent / '.pio' / 'build' / 'esp32dev'
        if workspace_build.exists():
            build_dir = workspace_build
    
    # Get file paths
    if args.bootloader:
        bootloader_path = args.bootloader
    else:
        bootloader_path = build_dir / DEFAULT_FILES['bootloader']
    
    if args.partitions:
        partitions_path = args.partitions
    else:
        partitions_path = build_dir / DEFAULT_FILES['partitions']
    
    if args.firmware:
        firmware_path = args.firmware
    else:
        firmware_path = build_dir / DEFAULT_FILES['firmware']
    
    output_path = args.output
    
    # Create merger and merge files
    merger = BinMerger(
        output_path,
        bootloader_offset=args.bootloader_offset,
        partitions_offset=args.partitions_offset,
        firmware_offset=args.firmware_offset,
    )
    
    success = merger.merge_files(str(bootloader_path), str(partitions_path), str(firmware_path))
    
    if success:
        print(f"\n=== Hướng dẫn nạp ===")
        print(f"Dùng esptool.py để nạp file merged:")
        print(f"  esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 {output_path}")
        print(f"\nHoặc với platformio:")
        print(f"  pio run --target upload")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
