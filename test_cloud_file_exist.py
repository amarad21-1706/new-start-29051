from google.cloud import storage
import os

# Check credentials
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
print(f"Using credentials file: {credentials_path}")

# Initialize the client
client = storage.Client()

# List buckets
buckets = list(client.list_buckets())
print("Buckets in the project:")
for bucket in buckets:
    print(bucket.name)
