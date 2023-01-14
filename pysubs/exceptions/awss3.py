class S3InvalidUploadSource(Exception):
    """Raise when upload sources are not provided for Aws S3 uploads."""


class S3InvalidDownloadFileUrl(Exception):
    """Raise when the file url/path for downloading is not given"""
