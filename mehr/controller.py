class Controller(object):
    app = None

    def __init__(self, app):
        self.app = app
        self.set_routes()

    def set_routes(self):
        raise NotImplementedError()
