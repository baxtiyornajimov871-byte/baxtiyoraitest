from flask import Flask
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

from .config import Config
from .extensions import db, jwt, migrate, limiter