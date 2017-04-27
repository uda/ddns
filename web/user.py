def klein_routes(app):
    """
    :param web.klein.Klein app:
    """
    app.route('/')(index)
    app.route('/<string:user>')(profile)


def index(request):
    return 'Hello, user!'


def profile(request, user):
    return 'Hello, {}!'.format(user)
