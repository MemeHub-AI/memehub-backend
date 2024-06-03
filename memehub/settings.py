"""
Django settings for memehub project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from .settings_utils import get_database_config_from_url
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", '1234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("ENVIRONMENT").lower() == 'dev'
ENVIRONMENT = os.getenv("ENVIRONMENT").lower()

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'apps.resource',
    'apps.real_data',
    'apps.user',
    'apps.coin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'memehub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'memehub.wsgi.application'
ASGI_APPLICATION = 'memehub.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "remote": get_database_config_from_url(os.getenv("REMOTE_DATABASE_URL")),
    "resource": get_database_config_from_url(os.getenv("RESOURCE_DATABASE_URL")),
    'default': get_database_config_from_url(os.getenv("DATABASE_URL")),
}

DATABASE_ROUTERS = ['memehub.database_router.DatabaseAppsRouter']


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# pagesize
PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# s3 config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_ACCESS_SECRET_KEY = os.getenv("AWS_ACCESS_SECRET_KEY")
REGION_NAME = os.getenv("AWS_REGION_NAME")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# jwt salt
SALT = os.getenv("JWT_PRIVATE_KEY")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# data middleware
KAFKA_URL = os.getenv("KAFKA_URL")

RABBIT_HOST = os.getenv("RABBIT_HOST", "127.0.0.1")
RABBIT_SECRET = os.getenv("RABBIT_SECRET", "guest")
RABBIT_PORT = os.getenv("RABBIT_PORT")

# chain data

CHAINLIST = {
    "eth": {
        "id": "1",
        "name": "ethereum",
        "rpc": "https://eth.llamarpc.com",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": True,
    },
    "optimism": {
        "id": "10",
        "name": "optimism",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "bsc": {
        "id": "56",
        "name": "bsc",
        "rpc": "https://bsc-dataseed.bnbchain.org",
        "aggregator": "0xd381892392FD0AFa151e02d1D1883c0E4C5269F8",
        "contract_address": "",
        "native":{
            "decimals":18,
            "name":"BNB",
            "symbol":"BNB"
        },
        "explorer":"https://bscscan.com",
        "explorer_tx":"https://bscscan.com/tx",
        "is_supported": True,
    },
    "ftm": {
        "id": "250",
        "name": "fantom",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "zksync": {
        "id": "324",
        "name": "zksync",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "arbitrum": {
        "id": "42161",
        "name": "arbitrum",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "linea": {
        "id": "59144",
        "name": "linea",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "base": {
        "id": "8453",
        "name": "base",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "blast": {
        "id": "81457",
        "name": "blast",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "merlin-chain": {
        "id": "4200",
        "name": "merlin",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "bevm": {
        "id": "11501",
        "name": "bevm",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":0,
            "name":"",
            "symbol":""
        },
        "explorer":"",
        "explorer_tx":"",
        "is_supported": False,
    },
    "scroll": {
        "id": "534352",
        "name": "scroll",
        "rpc": "https://scroll-mainnet.rpc.grove.city/v1/a7a7c8e2",
        "aggregator": "0x33112b4EdD06FAa06e041c65CEd5b7e07330f025",
        "contract_address": "0x35Ce38AC48Dd3c7Bf6bd14dE8e81128d76E11885",
        "native":{
            "decimals":18,
            "name":"Ether",
            "symbol":"ETH"
        },
        "explorer":"https://scrollscan.com/",
        "explorer_tx":"https://scrollscan.com/tx",
        "is_supported": True,
    },
    "opbnb":{
        "id": "204",
        "name": "opbnb",
        "rpc": "https://opbnb-mainnet.nodereal.io/v1/ef196d9fb8d246aba50c5ccdd82f98fe",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":18,
            "name":"BNB",
            "symbol":"BNB"
        },
        "explorer":"https://mainnet.opbnbscan.com/",
        "explorer_tx":"https://mainnet.opbnbscan.com/tx",
        "is_supported": True,
    },
    "bsc_testnet": {
        "id": "97",
        "name": "bsc_testnet",
        "rpc": "https://data-seed-prebsc-1-s2.bnbchain.org:8545",
        "aggregator": "0xd381892392FD0AFa151e02d1D1883c0E4C5269F8",
        "contract_address": "",
        "native":{
            "decimals":18,
            "name":"BNB",
            "symbol":"tBNB"
        },
        "explorer":"https://testnet.bscscan.com",
        "explorer_tx":"https://testnet.bscscan.com/tx",
        "is_supported": False,
    },
    "opbnb_testnet":{
        "id": "5611",
        "name": "opbnb_testnet",
        "rpc": "https://opbnb-testnet-rpc.bnbchain.org",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":18,
            "name":"tBNB",
            "symbol":"tBNB"
        },
        "explorer":"https://testnet.opbnbscan.com/",
        "explorer_tx":"https://testnet.opbnbscan.com/tx",
        "is_supported": False,
    },
    "scroll_testnet":{
        "id": "534351",
        "name": "scroll_testnet",
        "rpc": "",
        "aggregator": "",
        "contract_address": "",
        "native":{
            "decimals":18,
            "name":"Ether",
            "symbol":"ETH"
        },
        "explorer":"https://testnet.opbnbscan.com/",
        "explorer_tx":"https://testnet.opbnbscan.com/tx",
        "is_supported": False,
    }
}

if ENVIRONMENT.lower() == "prod":
    CHAINLIST = {k: v for k, v in CHAINLIST.items() if "testnet" not in k}

CHAINID_MAPPING = {int(chain["id"]): chain["name"] for chain in CHAINLIST.values()}

SCANNER_URL = {
    "eth": "https://etherscan.io",
    "scroll": "https://scrollscan.com",
}


# cache config
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PWD = os.getenv("REDIS_PWD", "123456")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/{REDIS_PWD}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}
