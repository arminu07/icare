import csv

# Read the test CSV file
with open('test_sample.csv', 'r') as f:
    content = f.read()

# Parse it
decoded_file = content.splitlines()
csv_reader = csv.DictReader(decoded_file)
medical_data = list(csv_reader)

print(f"✓ CSV file parsed successfully")
print(f"✓ Records found: {len(medical_data)}")
print(f"✓ Headers: {list(medical_data[0].keys())}")
print(f"✓ First record: {medical_data[0]}")
