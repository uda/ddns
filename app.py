from web import main, user, domain
from klein import Klein

app = Klein()

main.main_index = app.route('/')(main.main_index)

with app.subroute('/user') as app:
    user.user_index = app.route('/')(user.user_index)
    user.user_login_form = app.route('/login', methods=['GET'])(user.user_login_form)
    user.user_login = app.route('/login', methods=['POST'])(user.user_login)
    user.user_view = app.route('/view/<string:user>')(user.user_view)

with app.subroute('/domain') as app:
    domain.domain_index = app.route('/')(domain.domain_index)
    domain.domain_view = app.route('/view/<string:name>')(domain.domain_view)

app.run("localhost", 8080)
