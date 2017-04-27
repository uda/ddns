def klein_routes(app):
    """
    :param web.klein.Klein app:
    """
    app.route('/')(index)
    app.route('/a/<string:page>')(page_a)


def index(request):
    return 'Hello, world!'


async def page_a(request, page):
    return 'Page {}'.format(page)
