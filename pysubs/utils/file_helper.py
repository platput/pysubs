def write_content_to_file(local_storage_path: str, file_content: str | bytes) -> str:
    """
    file utility helper function to save content to a file at the given path.
    :param local_storage_path:
    :param file_content:
    :return:
    """
    with open(local_storage_path, "wb") as video:
        video.write(file_content)
    return local_storage_path
