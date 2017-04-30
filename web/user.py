def user_index(request):
    return 'Hello, user!'


def user_view(request, user):
    return 'Hello, {}!'.format(user)
