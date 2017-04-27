from web import main, user, domain
from web.klein import Klein

app = Klein()

app.module_route(main)
app.module_route(user, subroute='/user')
app.module_route(domain.Domain(), subroute='/domain')

app.run("localhost", 8080)
