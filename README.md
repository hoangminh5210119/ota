# ESP32 OTA & BIN Merger

Công cụ để ghép các file .bin và nạp firmware cho ESP32.

## Ghép các file .bin

Script `merge_bin.py` giúp merge bootloader, partitions, và firmware thành 1 file duy nhất.

### Cách sử dụng cơ bản

```bash
python3 merge_bin.py
```

Script sẽ tìm 3 file trong cùng thư mục:
- `bootloader.bin`
- `partitions.bin`
- `firmware.bin`

Kết quả sẽ được lưu vào: `merged_firmware.bin`

### Cách sử dụng nâng cao

```bash
# Chỉ định file input và output
python3 merge_bin.py \
  --bootloader bootloader.bin \
  --partitions partitions.bin \
  --firmware firmware.bin \
  --output my_merged_fw.bin

# Chỉ định offset (nếu khác default)
python3 merge_bin.py \
  --bootloader-offset 0x1000 \
  --partitions-offset 0x8000 \
  --firmware-offset 0x10000
```

### File được tạo

| File | Offset | Mô tả |
|------|--------|-------|
| bootloader.bin | 0x1000 (4KB) | Bootstrap code |
| partitions.bin | 0x8000 (32KB) | Partition table |
| firmware.bin | 0x10000 (64KB) | Application firmware |

## Nạp firmware merged

### Dùng esptool.py

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 merged_firmware.bin

esptool.py --chip esp32 --baud 115200 write_flash 0x0 merged_firmware.bin
```

### Dùng PlatformIO

```bash
pio run --target upload
```

## Hướng dẫn Step-by-Step

### 1. Copy file từ build output

```bash
# Copy từ .pio/build/esp32dev
cp ../.pio/build/esp32dev/bootloader.bin .
cp ../.pio/build/esp32dev/partitions.bin .
cp ../.pio/build/esp32dev/firmware.bin .
```

### 2. Chạy merge script

```bash
python3 merge_bin.py
```

### 3. Nạp file merged

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 merged_firmware.bin
```

## Ghi chú

- Default offsets hỗ trợ ESP32 standard
- File merged được fill với 0xFF (như flash memory)
- Tương thích với esptool.py v3.0+
- Python 3.6+
