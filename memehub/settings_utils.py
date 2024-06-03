from urllib.parse import urlparse


def get_database_config_from_url(url: str):
    """
    Extracts database configuration from a URL.
    """
    result = urlparse(url)
    return {
        'ENGINE': f'django.db.backends.{result.scheme.split("+")[0]}',
        'NAME': result.path[1:],
        'USER': result.username,
        'PASSWORD': result.password,
        'HOST': result.hostname,
        'PORT': result.port,
    }
