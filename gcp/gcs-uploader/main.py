from google.cloud import storage
import os

bucket_filter_key: str = '<bucket_key_word_search>'
files_to_upload_path: str = '<path_to_source_folder>'

def list_gcs_buckets() -> list:
    """
    Function will retrieve all the buckets with the specified 
    keyword

    Returns:
        list: returns a list containing the bucket names
    """
    bucket_list: list = []
    storage_client: storage = storage.Client()

    buckets: list = list(storage_client.list_buckets())

    for bucket in buckets:
        if bucket_filter_key in bucket.name:
            bucket_list.append(bucket.name)
    
    return bucket_list

def upload_files_to_gcs(bucket_list: list, files_to_upload_path: str) -> None:
    """
    Function is taking a list of bucket names that were retrieved in the 
    previous function and uploades files in a specified path to each bucket
    Args:
        bucket_list (list): list of buckets to upload to
        files_to_upload_path (str): path to your source folder with the 
        files to upload
    """
    storage_client = storage.Client()

    for bucket in bucket_list:
        bucket: str = storage_client.get_bucket(bucket)
        for root, _, files in os.walk(files_to_upload_path):
            for file in files:
                print(f'Will upload {file} to {bucket.name}')
                file_path: str = os.path.join(root, file)
                blob = bucket.blob(os.path.relpath(file_path, files_to_upload_path))
                blob.upload_from_filename(file_path)
                print(f'File {file} uploaded to {bucket.name}.')

def is_folder_empty(folder_path: str) -> bool:
    """Check if the folder is empty."""
    return not any(os.scandir(folder_path))

if __name__ == "__main__":
    buckets_to_upload = list_gcs_buckets()
    if not buckets_to_upload:
        print("No buckets with the specified keyword")
    elif is_folder_empty(folder_path=files_to_upload_path):
        print("No files in the source folder")
    else: 
        upload_files_to_gcs(bucket_list=buckets_to_upload,
                           files_to_upload_path=files_to_upload_path)
