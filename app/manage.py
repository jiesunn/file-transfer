import sys

from flask import session, redirect, url_for, request

sys.path.append(r"/usr/src")

from app import create_app

app = create_app()


@app.before_request
def print_request_info():
    url = request.path.split('/')
    if len(url) >= 2:
        if url[1] != 'login':
            if 'sub' not in session:
                return redirect(url_for('http.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)
