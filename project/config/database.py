import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection config
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', '141.164.52.125'),
    'database': os.getenv('MYSQL_DATABASE', 'harukcal2'),
    'user': os.getenv('MYSQL_USER', 'anra1'),
    'password': os.getenv('MYSQL_PASSWORD', 'your_password_here')
} 