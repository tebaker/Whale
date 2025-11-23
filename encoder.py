# ==============================================================================
# WHALE-PUUP Encoder Module (encoder.py)
# Handles Base64 encoding of a file (e.g., a ZIP archive) and decoding a Base64
# text file back into its original binary format.
# ==============================================================================

import base64
import os
# Assumes utilities.py exists for the color function
import utilities 

def encode_file_to_base64(input_file_path, output_file_path):
    """
    Reads a binary file, encodes its content to Base64, and writes it to a text file.

    Args:
        input_file_path (str): Path to the binary file (e.g., ZIP).
        output_file_path (str): Path to the output text file (.txt).
    """
    try:
        # Read the binary file
        with open(input_file_path, 'rb') as input_file:
            binary_data = input_file.read()

        # Encode the binary data to Base64
        base64_data = base64.b64encode(binary_data)

        # Write the Base64 data (as bytes) to the output file
        with open(output_file_path, 'wb') as output_file:
            output_file.write(base64_data)
            
        print(utilities.color(f"Successfully encoded {os.path.basename(input_file_path)} to Base64.", "GREEN"))

    except Exception as e:
        print(utilities.color(f"[ERROR in Encoder] Failed to encode file {input_file_path}: {e}", "RED"))


def decode_file_from_base64(input_file_path, output_file_path):
    """
    Reads a Base64 text file, decodes its content, and writes the binary data 
    to a new file (e.g., a ZIP archive).

    Args:
        input_file_path (str): Path to the Base64 text file (.txt).
        output_file_path (str): Path to the output binary file (e.g., .zip).
        
    Returns:
        bool: True if decoding was successful, False otherwise.
    """
    try:
        # Read the Base64 data (as bytes)
        with open(input_file_path, 'rb') as input_file:
            base64_data = input_file.read()

        # Decode the Base64 data back to binary
        binary_data = base64.b64decode(base64_data)

        # Write the resulting binary data to the output file
        with open(output_file_path, 'wb') as output_file:
            output_file.write(binary_data)
            
        print(utilities.color(f"Successfully decoded {os.path.basename(input_file_path)} to {os.path.basename(output_file_path)}.", "GREEN"))
        return True

    except Exception as e:
        print(utilities.color(f"[ERROR in Decoder] Failed to decode file {input_file_path}: {e}", "RED"))
        return False