from web import main, user, domain
from klein import Klein

app = Klein()

app.route('/')(main.main_index)

with app.subroute('/user') as app:
    app.route('/')(user.user_index)
    app.route('/view/<string:user>')(user.user_view)

with app.subroute('/domain') as app:
    app.route('/')(domain.domain_index)
    app.route('/view/<string:name>')(domain.domain_view)

app.run("localhost", 8080)
