from app import app, sckio

if __name__ == '__main__':
    sckio.run(app, host='0.0.0.0', debug=False)