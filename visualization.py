import dash
from dash import Dash, dcc, html, dash_table, Input,Output,callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

# Load and preprocess the data
try:
    df = pd.read_excel('Vestas_SCADA_Alarm_Logs_2025.xls')
except FileNotFoundError:
    print("Error: Excel file not found. Ensure 'Vestas_SCADA_Alarm_Logs_2025.xls' is in the project directory.")
    exit()


# Convert date columns to datetime
df['Detected'] = pd.to_datetime(df['Detected'], errors='coerce')
df['Device acknowledged'] = pd.to_datetime(df['Device acknowledged'], errors='coerce')
df['Reset/Run'] = pd.to_datetime(df['Reset/Run'], errors='coerce')

# Calculate duration in hours
df['Duration_Hours'] = (df['Reset/Run'] - df['Detected']).dt.total_seconds() / 3600


# Extract Short Description 
df['Short_Description'] = df['Description'].apply(lambda x: x.split(':')[0].strip() if isinstance(x, str) and ':' in x else x)

# Prepare data 

line_data = df[df['Event type'] == 'Alarm log (A)'].groupby(df['Detected'].dt.date).size().reset_index(name='Count').sort_values('Count', ascending=False)
bar_data = df[df['Event type'] == 'Alarm log (A)'].groupby('Short_Description')['Duration_Hours'].sum().reset_index().sort_values('Duration_Hours', ascending=False).head(10)
pie_data = df[df['Event type'] == 'Alarm log (A)'].groupby('Short_Description').size().reset_index(name='Count').sort_values('Count', ascending=False).head(5)

# Get unique values for dropdowns
units = [{'label': 'All', 'value': 'All'}] + [{'label': u, 'value': u} for u in df['Unit'].dropna().unique()]
severities = [{'label': 'All', 'value': 'All'}] + [{'label': str(s), 'value': s} for s in df['Severity'].dropna().unique()]

#Chart colours
renewable_colors = ['#43A047', '#2E7D32', '#66BB6A', '#81C784', '#26A69A', '#0277BD']

#create the charts
#Line Chart
line_fig = px.line(
    line_data,
    x='Detected',
    y='Count',
    title='Daily Alarm Count',
    labels={'Detected': 'Date', 'Count': 'Number of Alarms'},
    color_discrete_sequence=['#0277BD']
)
line_fig.update_traces(fill='tozeroy')
line_fig.update_layout(
    template='plotly_white',
    title_x=0.5,
    showlegend=False,
    yaxis=dict(range=[0, None])
)

#Bar Chart
bar_fig = px.bar(
    bar_data,
    x='Short_Description',
    y='Duration_Hours',
    title='Total Alarm Duration by Descriptiion',
    labels={'Short_Description': 'Alarm Description', 'Duration_Hours': 'Total Duration (Hours)'},
    color='Short_Description',
    color_discrete_sequence = renewable_colors
)
bar_fig.update_layout(
    template='plotly_white',
    title_x=0.5,
    showlegend=False,
    yaxis=dict(range=[0, None])
)

pie_fig = px.pie(
    pie_data,
    names='Short_Description',
    values='Count',
    title='Top 5 Alarms by Short Description',
    color_discrete_sequence = renewable_colors
)
pie_fig.update_layout(
    template='plotly_white',
    title_x=0.5,
    legend=dict(orientation='v', yanchor='middle', y=0.5, xanchor='right', x=1.2)
)
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    # Title
    dbc.Row([
        dbc.Col(
            html.Img(
                src='https://images.unsplash.com/photo-1596386461350-326ccb383e9f?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&q=80',
                style={'height': '100px', 'marginRight': '20px'}
            ),
            width=2, className='d-flex align-items-center'
        ),
        dbc.Col(
            html.H1('Vestas Wind Turbines Alarm Dashboard', style={'fontSize': '36px'}),
            width=10, className='text-center text-white d-flex align-items-center'
        )
    ], className='p-3 my-4', style={'backgroundColor': '#388E3C', 'borderRadius': '5px'}),
    
    
    # Description
    dbc.Row([
        dbc.Col(
            html.P(
                "This dashboard provides an interactive analysis of SCADA alarm logs for Vestas wind turbines in Ngong Wind  "
                " Farm from July 2020 to June 2025. It includes data on alarm codes, descriptions, detection times, durations, event types, "
                "and severity levels. Use the dropdowns to filter by unit, event type, severity, or date range, and explore the data "
                "through interactive line, bar, and pie charts, as well as a detailed table.",style={'fontSize': '20px', 'color': '#FFFFFF', 'textAlign': 'justify'},
                className='text-center mt-3'
            )
        )
    ],className='p-3 my-4',style = {'backgroundColor': '#388E3C', 'borderRadius': '5px'}),

    # Dropdowns
    dbc.Row([
    # Unit Selector
        dbc.Col([
            html.H5('Select Unit', className='mb-3', style={'fontSize': '22px','color': '#1B5E20' }),
                dcc.Dropdown(
            id='unit-dropdown',
            options=units,
            value='All',
            style={'width': '100%', 'fontSize': '18px', 'backgroundColor': '#E8F5E9',
                                'color': '#1B5E20', 'borderRadius': '8px', 'padding': '8px'}
        )
    ],  md=3, className='p-3 mb-4 rounded shadow-sm', style={'backgroundColor': '#C8E6C9', 'marginRight': '20px'}),
    
    # Severity Selector
        dbc.Col([
            html.H5('Select Severity', className='mb-3', style={'fontSize': '22px'}),
                dcc.Dropdown(
            id='severity-dropdown',
            options=severities,
            value='All',
            style={'width': '100%', 'fontSize': '18px', 'backgroundColor': '#E8F5E9',
                                'color': '#1B5E20', 'borderRadius': '8px', 'padding': '8px'}
        )
    ],  md=3, className='p-3 mb-4 rounded shadow-sm', style={'backgroundColor': '#C8E6C9', 'marginRight': '20px'}),

    # Date Range Selector
        dbc.Col([
            dbc.Label("Select Date Range", html_for="date-range-picker", style={'fontSize': '22px', 'color': '#1B5E20'}),
            dcc.DatePickerRange(id='date-range-picker',
                                start_date=pd.Timestamp('2020-07-01'),
                                end_date=pd.Timestamp('2025-06-30'),
                                display_format='DD/MM/YYYY',
                                style={'width': '100%', 'fontSize': '18px', 'backgroundColor': '#E8F5E9',
                                       'color': '#1B5E20', 'borderRadius': '8px', 'padding': '10px',
                                       'border': '2px solid #81C784'})
        ], md=3, className='p-3 mb-4 rounded shadow-sm', style={'backgroundColor': '#C8E6C9'})
    ], className='p-3 my-5 g-4 justify-content-between'),

    
    # Charts
    dbc.Row([
        # Line Chart: Daily Alarm Count
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Daily Alarm Count'),
                dbc.CardBody([
                    dcc.Graph(id='line-chart', figure=line_fig)
                ])
            ], className='shadow-sm')
        ], md=4, className='mb-4 mt-4'),
        # Bar Chart: Total Duration by Description
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Total Alarm Duration by Description'),
                dbc.CardBody([
                    dcc.Graph(id='bar-chart', figure=bar_fig)
                ])
            ], className='shadow-sm')
        ], md=4, className='mb-4 mt-4'),
        # Pie Chart: Top 5 Alarms by Short Description
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Top 5 Alarms by Short Description'),
                dbc.CardBody([
                    dcc.Graph(id='pie-chart', figure=pie_fig)
                ])
            ], className='shadow-sm')
        ], md=4, className='mb-4 mt-4')
    ], justify='center', className='p-3 my-4'),

    # Table
    dbc.Row([
        dbc.Col([
            html.H5('Complete Alarm Log',className='text-center mb-3'),
            dash_table.DataTable(
            id='alarm-table',
            columns=[{'name': col, 'id': col} for col in ['Unit', 'Code', 'Description', 'Detected', 'Duration', 'Event type', 'Severity']],
            data=df[['Unit', 'Code', 'Description', 'Detected', 'Duration', 'Event type', 'Severity']].to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '18px'},
            style_header={'backgroundColor': '#388E3C', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '20px'},
            filter_action='native',
            sort_action='native'
        )], className='bg-light rounded shadow-sm p-3')
    ], className='p-3 my-4', style={'backgroundColor': '#388E3C', 'borderRadius': '5px'})
], fluid=True)

@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('alarm-table', 'data')],
    [Input('unit-dropdown', 'value'),
     Input('severity-dropdown', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_dashboard(unit, severity, start_date, end_date):
    # 1️ Apply all filters once
    filtered_df = df.copy()

    if unit != 'All':
        filtered_df = filtered_df[filtered_df['Unit'] == unit]
    if severity != 'All':
        filtered_df = filtered_df[filtered_df['Severity'] == severity]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['Detected'] >= pd.to_datetime(start_date)) &
            (filtered_df['Detected'] <= pd.to_datetime(end_date))
        ]

    # Only alarm logs
    alarm_df = filtered_df[filtered_df['Event type'] == 'Alarm log (A)']

    # 2️ Line Chart - Daily Alarm Count
    line_data = alarm_df.groupby(alarm_df['Detected'].dt.date).size().reset_index(name='Count')
    line_data.rename(columns={'Detected': 'Date'}, inplace=True)
    line_fig = px.line(line_data, x='Date', y='Count',
                       title='Daily Alarm Count',
                       labels={'Date': 'Date', 'Count': 'Number of Alarms'},
                       color_discrete_sequence=['#0277BD'])
    line_fig.update_traces(fill='tozeroy')
    line_fig.update_layout(template='plotly_white', title_x=0.5, showlegend=False)

    # 3️ Bar Chart - Top 10 Alarms by Duration
    bar_data = alarm_df.groupby('Short_Description', as_index=False)['Duration_Hours'] \
                       .sum().sort_values(by='Duration_Hours', ascending=False).head(10)
    bar_fig = px.bar(bar_data, x='Short_Description', y='Duration_Hours',
                     title='Total Alarm Duration by Description',
                     labels={'Short_Description': 'Alarm Description',
                             'Duration_Hours': 'Total Duration (Hours)'},
                     color='Short_Description', color_discrete_sequence=renewable_colors)
    bar_fig.update_layout(template='plotly_white', title_x=0.5, showlegend=False)

    # 4️ Pie Chart - Top 5 Alarms by Count
    pie_data = alarm_df.groupby('Short_Description').size().reset_index(name='Count') \
                       .sort_values('Count', ascending=False).head(5)
    pie_fig = px.pie(pie_data, names='Short_Description', values='Count',
                     title='Top 5 Alarms by Short Description',color_discrete_sequence=renewable_colors)
    pie_fig.update_layout(template='plotly_white', title_x=0.5)

    # 5️ Table Data
    table_data = filtered_df[['Unit', 'Code', 'Description', 'Detected',
                               'Duration', 'Event type', 'Severity']].to_dict('records')

    return line_fig, bar_fig, pie_fig, table_data



# Run the app
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=port, debug=True)




























































































    
    
   
