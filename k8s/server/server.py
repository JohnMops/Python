from flask import Flask, render_template, request, jsonify


def run_server(conn, port, host, db_client, namespace_list):
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

    @app.route('/api/v1/update_deployment', methods=['PUT'])
    def api_update_deployment():
        data = request.get_json()
        db_client.update_deployment(data)



    app.run(debug=True, port=port, host=host)



