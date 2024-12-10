
from app import upload_to_bucket
from google.cloud import storage

# Explicitly set the credentials
client = storage.Client.from_service_account_json('/Users/aradulescu/.config/google/optimum-entity-444217-n2-eb651fc775a4.json')

# Use the client to interact with GCS
buckets = list(client.list_buckets())
print("Buckets:", buckets)

upload_to_bucket(
    bucket_name='dere-1',
    source_file_name='test_file.txt',
    destination_blob_name='test_file_in_bucket.txt'
)
