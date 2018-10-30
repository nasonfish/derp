from derp import app, config

# if the application is run
if __name__ == '__main__':
    app.secret_key = str(app.config['APP_SECRET_KEY'])
    app.debug = app.config['DEBUG']
    app.run(port=app.config['PORT'], host=app.config['HOST'])
