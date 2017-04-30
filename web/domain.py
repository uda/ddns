def domain_index(request):
    return 'Domain list'


def domain_view(request, name):
    return 'Domain: {}'.format(name)
