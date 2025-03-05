import os
from dotenv import load_dotenv

# this will be used to access the .env file
load_dotenv()

# set up a class for all the necessary configurations for this app
class Settings:
    # this secret key is necessary for the app, it is used for creating JWT tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # this is the algorithm for encoding passwords to preven passwords from showing directly in the database
    ALGORITHM: str = "HS256"
    # how long the token will expire after login (this will be encoded in the JWT token)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60 # 30 days
    # importing the MongoDB connection string from the .env file
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    # get the "ENV" variable from the .env, if it's not defined, default to "development" 
    ENV: str = os.getenv("ENV", "development")