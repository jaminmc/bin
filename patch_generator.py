import sys


def find_binary_sets(data):
    binary_sets = []
    current_set = []
    for byte in data:
        if byte >= 32 and byte <= 126:
            current_set.append(byte)
        else:
            if len(current_set) >= 4:
                binary_sets.append(bytes(current_set))
            current_set = []
    if len(current_set) >= 4:
        binary_sets.append(bytes(current_set))
    return binary_sets


def generate_patch(bin1_path, bin2_path):
    with open(bin1_path, "rb") as f1, open(bin2_path, "rb") as f2:
        bin1_data = f1.read()
        bin2_data = f2.read()

    if len(bin1_data) != len(bin2_data):
        print("Error: Binary files have different sizes.")
        return

    # Find binary sets in the second binary
    binary_sets = find_binary_sets(bin2_data)

    # Generate patches
    patches = []
    for set_bytes in binary_sets:
        set_hex = set_bytes.hex()
        # Ensure the set exists only once in the original binary
        while bin1_data.count(set_bytes) > 1:
            # Add a unique byte to the set
            set_bytes += bytes([0])
        patches.append({"set_hex": set_hex, "patch_hex": set_bytes.hex()})

    # Create bash script
    bash_script = (
        "#!/bin/bash\n"
        "binary_file=" + bin1_path + "\n"
        "prep() {\n"
        '    sudo xattr -cr "$ocx_file"\n'
        '    sudo xattr -r -d com.apple.quarantine "$ocx_file"\n'
        '    sudo codesign --force --sign - "$ocx_file"\n'
        "}\n\n"
    )

    for patch in patches:
        bash_script += f"sudo perl -0777pi -e 's|{patch['set_hex']}|{patch['patch_hex']}|g' \"$binary_file\"\n"

    bash_script += (
        "ocx_file=<path_to_ocx_file>\n"  # Provide the path to the OCX file
        "prep\n"
    )

    return bash_script


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python patch_generator.py <binary1> <binary2>")
        sys.exit(1)

    bin1_path = sys.argv[1]
    bin2_path = sys.argv[2]

    patch = generate_patch(bin1_path, bin2_path)
    print(patch)
