import base64  # Add this import statement

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from textwrap import wrap
from flask_caching import Cache
import io
# Initialize Dash app and Flask server
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Initialize Flask-Caching
cache = Cache(server, config={'CACHE_TYPE': 'simple'})

# Function to visualize blastn results
@cache.memoize()
def visualize_blastn_results(file_contents):
    # Convert file contents to DataFrame
    file_like_object = io.BytesIO(file_contents)
    # Convert file-like object to DataFrame
    df = pd.read_csv(file_like_object, comment='#', sep="\t", header=None)
    df['line_num'] = df.reset_index().index + 1
    df.columns = ["F" + str(i) for i in range(16)]
    # Initialize dictionary to store data
    dic = {}
    num = 0
    # Iterate through DataFrame rows
    for index, row in df.iterrows():
        x1 = row["F6"]
        x2 = row["F7"]
        y1 = row["F8"]
        y2 = row["F9"]
        seq_q = row["F12"]
        line_number = row[15]

        # Store data in dictionary
        dic[num] = [x1, y1, seq_q, line_number]
        num += 1
        dic[num] = [x2, y2, seq_q, line_number]
        num += 1

    # Convert dictionary to DataFrame
    df1 = pd.DataFrame(dic).T
    df1.columns = ["Pos" + str(i) for i in range(2)] + ["seq_q", "No"]
    df1 = df1.sort_values(by="No")

    # Create Plotly figure
    fig = px.line(df1, x="Pos0", y="Pos1", title="Blastn Results",
                  color="seq_q", width=500, height=500, markers=True, symbol="No")
    fig.update_layout(
        showlegend=False,
        width=1000,
        height=1000,
        plot_bgcolor="#fff",
        uniformtext_minsize=1,
        uniformtext_mode='hide',
        xaxis=dict(zeroline=False),
        yaxis=dict(zeroline=False),
        paper_bgcolor="white",
        title_xanchor="center",
        title_xref="paper",
        title_x=0.5,
        title_yanchor='top'
    )
    fig.update_geos(framecolor="black", framewidth=5)
    fig.update_xaxes(showline=True, linewidth=3, linecolor='black', title=None)
    fig.update_yaxes(showline=True, linewidth=3, linecolor='black', title=None)

    return fig

# Define Dash layout
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])

# Callback to update output
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Call the visualization function with file contents
        fig = visualize_blastn_results(decoded)

        return dcc.Graph(
            id='blastn-plot',
            figure=fig
        )

if __name__ == '__main__':
    app.run_server(debug=True)

