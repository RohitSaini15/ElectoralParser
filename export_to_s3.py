import boto3
import argparse
import os

s3 = boto3.client('s3')
BUCKET_NAME = "familyjson-test"

def upload_file_to_s3(json_file_path,bucket_name,object_name = None):

    if not object_name:
        object_name = os.path.basename(json_file_path)

    try:
        response = s3.upload_file(json_file_path, BUCKET_NAME, f"family_{object_name}.json")
    except Exception as err:
        print(err)
        return False

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputjson",help = "path of the json file",required = True)
    args = parser.parse_args()

    json_file_path = args.inputjson

    result = upload_file_to_s3(json_file_path,BUCKET_NAME)
    
    if result:
        print("file uploaded successfully")

if __name__ == "__main__":
    main()
