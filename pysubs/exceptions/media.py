class UnsupportedMediaConversionError(Exception):
    """Raise when unsupported media conversion is attempted """


class UnsupportedMediaDownloadError(Exception):
    """Raise when unsupported media download is attempted """


class NotEnoughCreditsToPerformGenerationError(Exception):
    """Raise when enough credits are not available for user to perform subtitle generation"""
