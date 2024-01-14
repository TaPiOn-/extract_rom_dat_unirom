import mmap
import os
import struct

def read_element(file_map, offset):
    # Read element structure from the file map
    element_format = "IIII45s3x"
    element_size = struct.calcsize(element_format)
    element_data = file_map[offset:offset + element_size]

    if not element_data:
        return None

    # Unpack element data
    length, offset, checksum, unused, description_bytes = struct.unpack(element_format, element_data)

    if length == 0:
        return None

    # Convert description from bytes to string
    description = description_bytes.rstrip(b'\x00').decode('ascii')

    return {
        'length': length,
        'offset': offset,
        'checksum': checksum,
        'unused': unused,
        'description': description,
    }

def calculate_checksum(file_map, offset, length):
    # Read the ROM data from the file map
    rom_data = file_map[offset:offset + length]

    # Simple checksum calculation
    return sum(rom_data) & 0xFFFFFFFF

def main(file_path):
    with open(file_path, 'rb') as file:
        # Map the entire file into memory
        file_map = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

        # Create a folder for extracted ROMs
        os.makedirs("extract_roms", exist_ok=True)

        # Loop through elements
        offset = 0
        while True:
            element = read_element(file_map, offset)

            if element is None:
                break

            # Display element details
            print("\nROM:")
            for key, value in element.items():
                print(f"{key}: {hex(value) if isinstance(value, int) else value}")

            # Check the checksum
            calculated_checksum = calculate_checksum(file_map, element['offset'], element['length'])

            if calculated_checksum == element['checksum']:
                print("Checksum is correct!")

                # Write ROM data to a file
                rom_filename = os.path.join("extract_roms", f"{element['description']}.rom")
                with open(rom_filename, 'wb') as rom_file:
                    rom_file.write(file_map[element['offset']:element['offset'] + element['length']])
                print(f"ROM data written to: {rom_filename}")
            else:
                print("Checksum is incorrect!")

            offset += struct.calcsize("IIII45s3x")

if __name__ == "__main__":
    file_path = "O_ROMS.DAT"  # Replace with the actual file path
    main(file_path)
