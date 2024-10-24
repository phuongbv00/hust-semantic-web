import re
import urllib.parse

def decode_uri_in_ntriples_with_regex(input_path, output_path):
    # Regular expression to match URIs within angle brackets
    uri_pattern = re.compile(r'<([^>]+)>')
    
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Find all URIs using regex
            decoded_line = line
            uris = uri_pattern.findall(line)
            
            # Decode each found URI
            for uri in uris:
                decoded_uri = urllib.parse.unquote(uri)
                # Replace encoded URI with decoded URI in the line
                decoded_line = decoded_line.replace(f'<{uri}>', f'<{decoded_uri}>')
            
            # Write the decoded line to the output file
            outfile.write(decoded_line)

# Example usage
input_path = input("Enter the input N-Triples file path: ")
output_path = input("Enter the output file path: ")
decode_uri_in_ntriples_with_regex(input_path, output_path)
