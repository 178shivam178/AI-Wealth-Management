from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import dash_table
import re
import dash
from django_plotly_dash import DjangoDash
from home.models import TransactionInfo

external_stylesheets = ["/static/css/sb-admin-2.min.css"]

home_page_app = DjangoDash('HomePage', external_stylesheets=external_stylesheets)

avg_spent_colors = ['royalblue', '#AF460F', '#1CC5DC', '#FF67E7']

home_page_app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.Div(
                html.Div(
                    html.Div(children=[
                        html.Div(
                            html.Div(
                                dcc.Graph(
                                    id='pie_chart',
                                    figure={}
                                ),
                                className="char-area"
                            ),
                            className="card-body"
                        )
                    ]),
                    className="card shadow mb-4"
                ),
                className="col-xl-12 col-lg-12 col-md-12"
            ),
            width=6  # Half of the screen (left side)
        ),
        dbc.Col(
            html.Div(
                html.Div(
                    dcc.Graph(
                        id='credit_debit_chart',
                        figure={}
                    ),
                    className="char-area"
                ),
                className="card shadow mb-4"
            ),
            width=6  # Half of the screen (right side)
        ),
    ]),
    dbc.Row([
        html.Div(
            html.Div(
                html.Div(children=[
                    html.Div(
                        "Email Overview",
                        id="email-table-header",
                        title="Email Overview",
                        className="card-header py-3 d-flex flex-row align-items-center justify-content-between m-0 font-weight-bold text-primary"
                    ),
                    html.Div(
                        html.Div(
                            dash_table.DataTable(
                                id='email-table',
                                sort_action='native',
                                filter_action='native',
                                style_data={'whiteSpace': 'normal'},
                                style_table={'height': '400px', 'overflowY': 'auto', 'overflowX': 'auto'},
                                style_cell={'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},
                                page_size=10,
                                export_format='xlsx',
                                export_headers='display',
                                css=[
                                    {"selector": ".show-hide", "rule": "margin-bottom:.5rem!important;color: #fff;background-color: #4e73df;border-color: #4e73df;padding: .25rem .5rem;font-size: .875rem;line-height: 1.5;border-radius: .2rem;border: 1px solid transparent;"},
                                    {"selector": ".export", "rule": "margin-bottom:.5rem!important;color: #fff;background-color: #4e73df;border-color: #4e73df;padding: .25rem .5rem;font-size: .875rem;line-height: 1.5;border-radius: .2rem;border: 1px solid transparent;"}
                                ]
                            ),
                            className="char-area"
                        ),
                        className="card-body"
                    )
                ]),
                className="card shadow mb-4"
            ),
            className="col-xl-12 col-lg-12 col-md-12"
        ),
    ]),
])

@home_page_app.callback(
    Output('pie_chart', 'figure'),
    Input('pie_chart', 'children')
)
def update_pie_chart(children):
    email_out = list(TransactionInfo.objects.filter().values())
    email_out_data_df = pd.DataFrame(email_out)
    counts = email_out_data_df['label'].value_counts()

    fig = go.Figure(
        data=[go.Pie(labels=counts.index, values=counts.values, hole=0.4)]
    )

    fig.update_layout(
        title_text='Amount Distribution',
        annotations=[dict(text='Labels', x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=True,
        plot_bgcolor='#ffffff'
    )

    return fig

@home_page_app.callback(
    Output('credit_debit_chart', 'figure'),
    Input('credit_debit_chart', 'children')
)
def update_credit_debit_chart(children):
    # Fetch data from the database
    transaction_data = list(TransactionInfo.objects.filter().values('TransactionDate', 'debit', 'credit'))
    df = pd.DataFrame(transaction_data)
    
    # Convert TransactionDate to datetime format
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    
    # Group by date and sum the Debit and Credit columns
    df_daily_totals = df.groupby('TransactionDate').agg({'debit': 'sum', 'credit': 'sum'}).reset_index()
    
    # Create the line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_daily_totals['TransactionDate'], y=df_daily_totals['debit'],
        mode='lines+markers', name='Total Debit', line=dict(color='red')
    ))

    fig.add_trace(go.Scatter(
        x=df_daily_totals['TransactionDate'], y=df_daily_totals['credit'],
        mode='lines+markers', name='Total Credit', line=dict(color='green')
    ))

    fig.update_layout(
        title='Total Credited and Debited Amounts per Day',
        xaxis_title='Date',
        yaxis_title='Amount',
        plot_bgcolor='#ffffff',
        hovermode='x unified'
    )

    return fig

@home_page_app.callback(
    Output('email-table', 'data'),
    Output('email-table', 'columns'),
    Input('email-table', 'data_previous'),
    Input('email-table', 'columns_previous')
)
def update_email_table(data_previous, columns_previous):
    # Replace this with your actual data retrieval logic
    result = list(TransactionInfo.objects.filter().values())
    df_all = pd.DataFrame(result)
    
    # Create the columns configuration
    all_columns = [{"name": re.sub("_", " ", i.capitalize()), "id": i, "hideable": True} for i in df_all.columns]
    
    return df_all.to_dict('records'), all_columns
