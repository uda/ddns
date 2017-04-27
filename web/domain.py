class Domain(object):
    app = None

    def klein_routes(self, app):
        self.app = app

        self.index = app.route('/')(self.index)
        self.get = app.route('/view/<string:name>')(self.get)

    def index(self, request):
        return 'Domain list'

    def get(self, request, name):
        return 'Domain: {}'.format(name)
