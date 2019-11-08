import os
import random
import uuid

from azure.storage.filedatalake import (
    DataLakeServiceClient,
)


def directory_sample(filesystem_client):
    # create a parent directory
    dir_name = "testdir"
    print("Creating a directory named '{}'.".format(dir_name))
    directory_client = filesystem_client.create_directory(dir_name)

    # populate the directory with some child files
    create_child_files(directory_client, 35)

    # rename the directory
    new_dir_name = "testdir2"
    print("Renaming the directory named '{}' to '{}'.".format(dir_name, new_dir_name))
    new_directory = directory_client\
        .rename_directory(rename_destination=directory_client.file_system_name + '/' + new_dir_name)

    # display the properties of the new directory to make sure it was renamed successfully
    props = new_directory.get_directory_properties()
    print("Properties of the new directory named '{}' are: {}.".format(new_dir_name, props))

    # remove the newly renamed directory
    print("Removing the directory named '{}'.".format(new_dir_name))
    new_directory.delete_directory()


def create_child_files(directory_client, num_child_files):
    import concurrent.futures
    import itertools
    # Use a thread pool because it is too slow otherwise
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        def create_file():
            # generate a random name
            file_name = str(uuid.uuid4()).replace('-', '')
            directory_client.get_file_client(file_name).create_file()

        futures = {executor.submit(create_file) for _ in itertools.repeat(None, num_child_files)}
        concurrent.futures.wait(futures)
        print("Created {} files under the directory '{}'.".format(num_child_files, directory_client.path_name))


def run():
    account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")
    account_key = os.getenv('STORAGE_ACCOUNT_KEY', "")

    # set up the service client with the credentials from the environment variables
    service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
        "https",
        account_name
    ), credential=account_key)

    # generate a random name for testing purpose
    fs_name = "testfs{}".format(random.randint(1, 1000))
    print("Generating a test filesystem named '{}'.".format(fs_name))

    # create the filesystem
    filesystem_client = service_client.create_file_system(file_system=fs_name)

    # invoke the sample code
    try:
        directory_sample(filesystem_client)
    finally:
        # clean up the demo filesystem
        filesystem_client.delete_file_system()


if __name__ == '__main__':
    run()