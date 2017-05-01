from twisted.internet import defer


def user_index(request):
    return 'Hello, user!'


def user_login_form(request):
    return 'User login <form action="/user/login" method="post"><button type="submit">Login</button></form>'


def user_login(request):
    request.redirect('/')
    return defer.succeed(None)


def user_view(request, user):
    return 'Hello, {}!'.format(user)
