import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Configuration
emails = [
    'email1@example.com',
    'email2@example.com',
    'email3@example.com'
]
input_directory = r'C:\Users\Priyam\Desktop\python\Final\data'
output_directory = input_directory  # Save the CSV files in the same directory


# Function to convert JSON to CSV using the API with multiple emails
def convert_json_to_csv_via_api(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as json_file:
        json_data = json_file.read()

    api_url = 'https://data.page/api/getcsv'
    post_fields = {'json': json_data}

    for email in emails:
        post_fields['email'] = email
        request = Request(api_url, urlencode(post_fields).encode(), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        })

        try:
            response = urlopen(request)
            csv_data = response.read().decode()
            with open(output_path, 'w', encoding='utf-8', newline='') as csv_file:
                csv_file.write(csv_data)
            print(f"Converted {input_path} to {output_path} using {email}")
            return  # Exit the function after successful conversion
        except HTTPError as e:
            if e.code == 413:  # Payload Too Large
                print(f"Email {email} exceeded 1MB limit. Trying next email.")
            else:
                print(f"Failed to convert {input_path} using {email}. Error: {e}")
                return
        except Exception as e:
            print(f"Failed to convert {input_path} using {email}. Error: {e}")
            return

    print(f"All emails failed to convert {input_path}. No valid CSV was created.")


# Get all JSON files in the input directory
json_files = [f for f in os.listdir(input_directory) if f.endswith('.json')]

# Convert each JSON file to CSV
for json_file in json_files:
    input_path = os.path.join(input_directory, json_file)
    output_path = os.path.join(output_directory, json_file.replace('.json', '.csv'))
    convert_json_to_csv_via_api(input_path, output_path)
