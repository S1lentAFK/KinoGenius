import os
import json
from googletrans import Translator

# Define the base path and years
base_path = r'movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']

# Create a list of directories
directories = [os.path.join(base_path, year) for year in years]

# Create a translator object
translator = Translator()

# Mapping dictionary for character replacement
char_mapping = {'č': 'c', 'ć': 'c', 'š': 's', 'đ': 'd', 'ž': 'z'}


# Function to replace characters in a string
def replace_characters(text):
    for char, repl in char_mapping.items():
        text = text.replace(char, repl)
    return text


# Function to translate the description in a JSON file
def translate_description(json_file_path):
    print("Translating:", json_file_path)
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Check if the 'description' field exists and is not None
    if 'description' in data and data['description']:
        # Replace special characters
        description = replace_characters(data['description'])

        # Translate the description
        translated_description = translator.translate(description, src="en", dest="hr").text

        # Update the description in the JSON data
        data['description'] = translated_description

        # Write back the updated JSON data to the file
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Translation complete for:", json_file_path)
    else:
        print("No description found or description is None for:", json_file_path)


# Loop through all directories and JSON files
for directory in directories:
    print("Processing directory:", directory)
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(directory, filename)
            try:
                translate_description(json_file_path)
            except Exception as e:
                print("Error translating", json_file_path, ":", e)
