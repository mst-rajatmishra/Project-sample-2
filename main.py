import json
from pdfrw import PdfReader, PdfWriter, PdfDict

# Load JSON data from a file
# This JSON file contains the data that will be used to fill the PDF form.
try:
    with open('data.json') as data_file:
        data = json.load(data_file)  # Load and parse the JSON data
except FileNotFoundError:
    print("Error: data.json file not found.")
    exit()  # Exit the program if the file is not found
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from data.json.")
    exit()  # Exit the program if the JSON is invalid

# Load the lookup table that maps PDF fields to JSON paths
# The lookup table tells the program which data from the JSON file corresponds to each form field in the PDF.
try:
    with open('lookup_table.json') as lookup_file:
        lookup_table = json.load(lookup_file)  # Load and parse the lookup table
except FileNotFoundError:
    print("Error: lookup_table.json file not found.")
    exit()  # Exit the program if the lookup table file is not found
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from lookup_table.json.")
    exit()  # Exit the program if the lookup table JSON is invalid

# Function to extract a value from the nested JSON data using a path
# The path is a string that tells the function how to navigate through the JSON structure to find the desired value.
def get_value_from_path(data, path):
    keys = path.split('->')  # Split the path into individual keys using '->' as a separator
    value = data  # Start with the root of the JSON data
    for key in keys:
        key = key.strip()  # Remove any surrounding whitespace from the key
        if isinstance(value, list):  # Check if the current value is a list (array)
            try:
                index = int(key)  # Convert the key to an integer index
                value = value[index]  # Access the list element by index
            except (ValueError, IndexError):
                return None  # Return None if the key is not a valid index or is out of bounds
        else:
            value = value.get(key)  # Access the dictionary value by key
        if value is None:
            return None  # Return None if the key does not exist in the current level of the JSON
    return value  # Return the found value

# Load the PDF template that will be filled with data
template_pdf = 'form_App Application 2024.pdf'
output_pdf = 'filled_form.pdf'

try:
    pdf = PdfReader(template_pdf)  # Read the PDF file
except FileNotFoundError:
    
    print(f"Error: {template_pdf} file not found.")
    exit()  # Exit the program if the PDF file is not found

# Create a PDF writer object to save the filled PDF later
writer = PdfWriter()

# Iterate through each page in the PDF
for page in pdf.pages:
    annotations = page.get('/Annots')  # Get the annotations (form fields) from the page
    if annotations:
        for annotation in annotations:
            field = annotation.get('/T')  # Get the field name (the title of the form field)
            if field:
                field_name = field[1:-1].strip()  # Remove parentheses and trim whitespace
                print(f"Found field in PDF: '{field_name}'")  # Output the field name for debugging

                # Normalize the field name for comparison (optional)
                normalized_field = field_name.strip()

                # Check if the field name exists in the lookup table
                if normalized_field in lookup_table:
                    json_path = lookup_table[normalized_field]  # Get the corresponding JSON path
                    value = get_value_from_path(data, json_path)  # Get the value from the JSON data
                    if value is not None:
                        print(f"Filling field '{field_name}' with value '{value}'")  # Debug output
                        annotation.update(
                            PdfDict(V=value)  # Update the PDF form field with the value from JSON
                        )
                    else:
                        print(f"No value found for field '{field_name}' in JSON data")  # Debug output
                else:
                    print(f"Field '{field_name}' not found in lookup table")

    writer.addpage(page)  # Add the modified page to the PDF writer

# Save the filled PDF to a new file
try:
    writer.write(output_pdf)  # Write the filled PDF to the output file
    print(f"PDF form filled and saved as {output_pdf}")
except Exception as e:
    print(f"Error saving filled PDF: {e}")  # Handle any errors that occur during saving
