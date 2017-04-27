from klein import Klein as BaseKlein


class Klein(BaseKlein):
    modules = {}

    def module_route(self, module, subroute=None):
        routes = getattr(module, 'klein_routes')
        if not routes:
            raise ValueError('Module {} does not have a klein_routes method'.format(module.__name__))
        if subroute:
            with self.subroute(subroute) as app:
                routes(app)
        else:
            routes(self)
