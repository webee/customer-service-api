from app import app_clients


def get_client(app):
    return app_clients.get_client(app.appid, app.appkey, app.urls)
