import base64
import os

def encode_file_to_base64(input_filepath, output_filepath):
    """
    Reads a binary file, encodes its content to Base64, and writes the
    resulting ASCII string to a new output file.

    This function is designed to handle binary files (like the final ZIP archive)
    and converts them into a text-safe Base64 string.
    """
    print(f"\n--- Base64 Encoding Process ---")
    print(f"Input File: {input_filepath}")
    
    # --- 1. Read the input file in binary mode ---
    try:
        # Use 'rb' (read binary) mode to read the file as raw bytes.
        with open(input_filepath, 'rb') as f:
            binary_data = f.read()
        print(f"Successfully read {len(binary_data)} bytes.")

    except FileNotFoundError:
        print(f"Error: The input file '{input_filepath}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    # --- 2. Encode the binary data to Base64 ---
    encoded_bytes = base64.b64encode(binary_data)
    
    # Convert the encoded bytes (e.g., b'VGhpcyBpcy...') to a string
    encoded_content = encoded_bytes.decode('ascii')
    
    print("Content successfully Base64 encoded.")

    # --- 3. Write the Base64 string to the output file ---
    try:
        # Use 'w' (write text) mode to write the Base64 string.
        with open(output_filepath, 'w') as f:
            f.write(encoded_content)
        
        # Calculate size comparison
        original_size_bytes = os.path.getsize(input_filepath)
        encoded_size_bytes = os.path.getsize(output_filepath)
        
        original_size_kb = original_size_bytes / 1024
        encoded_size_kb = encoded_size_bytes / 1024
        
        print(f"Output File: {output_filepath}")
        print(f"Original size: {original_size_kb:.2f} KB")
        print(f"Encoded size: {encoded_size_kb:.2f} KB (Base64 adds ~33% overhead)")
        print(f"\nSuccess! The Base64 encoded content is saved to '{output_filepath}'")

    except Exception as e:
        print(f"An error occurred while writing the output file: {e}")

    # The function finishes without an explicit return, which implies return None
    # but the primary goal is the side-effect (creating the file).