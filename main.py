import json
import sqlite3

from flask import Flask, jsonify,request

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/pipelineconfig/<int:product_id>')
def get_pipelineconfig(product_id):
    # Connect to SQLite database
    conn = sqlite3.connect('engdashboard.db')

    # Execute SQL query to retrieve PipelineConfig data for the specified Product_Id
    cursor = conn.execute('SELECT * FROM PipelineConfig WHERE Product_Id = ?', (product_id,))
    rows = cursor.fetchall()

    # Convert the retrieved data into a list of dictionaries
    pipelineconfig_data = []
    for row in rows:
        pipelineconfig_data.append({
            'Step_Id': row[0],
            'Product_Id': row[1],
            'Step_Name': row[2],
            'Parent_id': row[3],
            'Link': row[4],
            'meta_data': row[5]
        })

    # Close database connection
    conn.close()

    # Return the PipelineConfig data as a JSON response
    return jsonify(pipelineconfig_data)

# Define endpoint for getting step information list from PipelineConfig
@app.route('/pipelineconfig/<int:product_id>/steps')
def get_steps(product_id):
    # Connect to SQLite database
    conn = sqlite3.connect('engdashboard.db')

    # Execute SQL query to retrieve step information list for the specified Product_Id
    cursor = conn.execute('SELECT * FROM PipelineConfig WHERE Product_Id = ?', (product_id,))
    rows = cursor.fetchall()

    # Convert the retrieved data into a list of dictionaries
    step_info_list = []
    for row in rows:
        step_info_list.append({
            'Step_Id': row[0],
            'Product_Id': row[1],
            'Step_Name': row[2],
            'Parent_id': row[3],
            'Link': row[4],
            'meta_data': row[5]
        })

    # Close database connection
    conn.close()

    # Return the step information list as a JSON response
    return jsonify(step_info_list)


# Define endpoint for creating PipelineStatus entries for a given build and product_id
@app.route('/pipelinestatus/<int:build_id>/<int:product_id>/create')
def create_pipelinestatus(build_id, product_id):
    # Connect to SQLite database
    conn = sqlite3.connect('engdashboard.db')

    # Retrieve the step information list for the specified Product_Id
    cursor = conn.execute('SELECT * FROM PipelineConfig WHERE Product_Id = ?', (product_id,))
    rows = cursor.fetchall()

    # Create a new entry in the PipelineStatus table for each step with a 'pending' status
    for row in rows:
        step_id = row[0]
        status = 'pending'
        start_time = None
        end_time = None
        meta_data = None
        conn.execute('INSERT INTO PipelineStatus (Build_Id, Step_Id, Status, start_time, end_time, meta_data) VALUES (?, ?, ?, ?, ?, ?)',
                     (build_id, step_id, status, start_time, end_time, meta_data))

    # Commit changes to the database
    conn.commit()

    # Close database connection
    conn.close()

    # Return a success message
    return 'PipelineStatus entries created for build {} and product_id {}'.format(build_id, product_id)

@app.route('/pipelinestatus/<int:build_id>')
def get_pipeline_status(build_id):
    conn = sqlite3.connect('engdashboard.db')
    c = conn.cursor()
    c.execute("SELECT * FROM PipelineStatus WHERE Build_Id=?", (build_id,))
    rows = c.fetchall()
    conn.close()
    pipeline_status = []
    for row in rows:
        pipeline_status.append({
            'Build_Id': row[0],
            'Step_Id': row[1],
            'Status': row[2],
            'start-time': row[3],
            'end-time': row[4],
            'meta-data': row[5]
        })
    return jsonify(pipeline_status)

@app.route('/updatestatus/<int:build_id>/<int:step_id>', methods=['PUT'])
def update_status(build_id, step_id):
    data = json.loads(request.data, strict=False)
    status = data.get('Status')
    start_time = data.get('start-time')
    end_time = data.get('end-time')
    meta_data = data.get('meta-data')

    conn = sqlite3.connect('engdashboard.db')
    c = conn.cursor()
    query = "UPDATE PipelineStatus SET "
    placeholders = []
    if status is not None:
        query += "Status=?, "
        placeholders.append(status)
    if start_time is not None:
        query += "start-time=?, "
        placeholders.append(start_time)
    if end_time is not None:
        query += "end-time=?, "
        placeholders.append(end_time)
    if meta_data is not None:
        query += "meta-data=?, "
        placeholders.append(meta_data)
    query = query.rstrip(', ') + " WHERE Build_Id=? AND Step_Id=?"
    placeholders.extend([build_id, step_id])
    c.execute(query, tuple(placeholders))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Status updated successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
