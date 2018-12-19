from app import (
    app,
    github)
from config import Config

@app.route('/authorize')
def login():
    return github.authorize(scope=Config.scope)

if __name__ == '__main__':
   app.run()