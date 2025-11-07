from flask import Flask
from app import app as flask_app

# This is the Vercel entrypoint
app = flask_app

if __name__ == '__main__':
    app.run()