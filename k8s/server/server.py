from flask import Flask, render_template


def run_server(conn, port, host):
    app = Flask(__name__)

    @app.route('/namespaces')
    def namespaces():
        cur = conn.cursor()
        cur.execute('SELECT * FROM namespaces')
        data = cur.fetchall()
        return render_template('namespaces.html', output_data=data)


    @app.route('/deployments')
    def deployments():
        cur = conn.cursor()
        cur.execute('SELECT * FROM deployments')
        data = cur.fetchall()
        return render_template('deployments.html', output_data=data)

    app.run(debug=True, port=port, host=host)



