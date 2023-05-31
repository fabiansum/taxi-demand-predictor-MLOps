import os, uuid, sys
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings

import os
from azure.storage.filedatalake import DataLakeFileClient

import src.config as config


import os
from azure.storage.filedatalake import DataLakeFileClient, DataLakeServiceClient

def upload_files_to_directory_bulk(year: str):
    try:
        storage_account_name = config.ADLS_NAME
        sas_token_key = config.SAS_TOKEN
        file_system_name = config.FS_NAME
        directory_name = "bronze/green/tripdata"
        local_base_directory = "data/raw/parquet"

        # Create a DataLakeFileClient instance
        credential = sas_token_key
        service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", storage_account_name), credential=credential)

        file_system_client = service_client.get_file_system_client(file_system=file_system_name)
        
        # Get the base directory client
        base_directory_client = file_system_client.get_directory_client(directory_name)

        # Get the year path based on the input year
        year_path = os.path.join(local_base_directory, f"year={year}")

        if not os.path.isdir(year_path):
            raise ValueError(f"No directory found for year {year}.")

        # Get the year directory client
        year_directory_client = base_directory_client.get_sub_directory_client(f"year={year}")

        # Iterate over the subdirectories (months) for the specified year
        for month_folder in os.listdir(year_path):
            month_path = os.path.join(year_path, month_folder)

            if not os.path.isdir(month_path):
                continue

            # Get the month directory client
            month_directory_client = year_directory_client.get_sub_directory_client(month_folder)

            # Iterate over the parquet files in each month directory
            for file_name in os.listdir(month_path):
                file_path = os.path.join(month_path, file_name)

                if not file_name.endswith(".parquet"):
                    continue

                # Get the file client
                file_client = month_directory_client.get_file_client(file_name)

                # Open and upload the file
                with open(file_path, "rb") as local_file:
                    file_client.upload_data(local_file, overwrite=True)

        print("Files uploaded successfully.")

    except Exception as e:
        print(e)


