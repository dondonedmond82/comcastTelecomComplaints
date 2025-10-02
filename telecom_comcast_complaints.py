# app.py
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

# ---------------------------------------------------
# Load dataset
df = pd.read_csv("comcast_telecom_complaints_data.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Convert TotalCharges to numeric
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df = df.dropna(subset=['TotalCharges'])

# ---------------------------------------------------
# Initialize Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Telco Customer Dashboard"

# ---------------------------------------------------
# APP LAYOUT WITH TABS
app.layout = html.Div([
    html.H2("Telco Customer Dashboard", style={"textAlign": "center", "marginTop": "20px"}),

    dcc.Tabs(id="tabs", value='tab-home', children=[
        dcc.Tab(label='Home', value='tab-home'),
        dcc.Tab(label='Bar & Pie', value='tab-bar-pie'),
        dcc.Tab(label='Line & Scatter', value='tab-line-scatter'),
        dcc.Tab(label='Heatmap', value='tab-heatmap'),
    ]),

    html.Div(id='tabs-content', style={"marginTop": "20px"})
])

# ---------------------------------------------------
# CALLBACK: Tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'tab-home':
        return html.Div([
            html.P("Welcome! Use the tabs to explore insights about Telco customers.",
                   style={"textAlign": "center", "fontSize": "18px"})
        ])
    
    elif tab == 'tab-bar-pie':
        return html.Div([
            html.H3("Bar & Pie Charts", style={"textAlign": "center"}),
            dcc.Dropdown(
                id="bar_pie_gender",
                options=[{"label": g, "value": g} for g in df["gender"].unique()],
                value="Male",
                clearable=False,
                style={"width": "50%", "margin": "auto"}
            ),
            html.Div([
                dcc.Graph(id="bar_chart", style={"flex": "1", "minWidth": "400px"}),
                dcc.Graph(id="pie_chart", style={"flex": "1", "minWidth": "400px"})
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"})
        ])
    
    elif tab == 'tab-line-scatter':
        return html.Div([
            html.H3("Line & Scatter Insights", style={"textAlign": "center"}),
            dcc.Dropdown(
                id="line_scatter_gender",
                options=[{"label": g, "value": g} for g in df["gender"].unique()],
                value="Male",
                clearable=False,
                style={"width": "50%", "margin": "auto"}
            ),
            html.Div([
                dcc.Graph(id="line_chart", style={"flex": "1", "minWidth": "400px"}),
                dcc.Graph(id="scatter_chart", style={"flex": "1", "minWidth": "400px"})
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}),
            html.Div(id="page2_insight", style={
                "marginTop": "20px",
                "padding": "10px",
                "backgroundColor": "#f8f9fa",
                "border": "1px solid #ddd"
            }),
            html.Button("More Insights", id="more_insights_btn", n_clicks=0, style={"marginTop": "20px"}),
            html.Div(id="more_insights_output", style={
                "marginTop": "10px",
                "padding": "10px",
                "backgroundColor": "#e9ecef",
                "border": "1px solid #ccc"
            })
        ])
    
    elif tab == 'tab-heatmap':
        return html.Div([
            html.H3("Heatmap Analysis", style={"textAlign": "center"}),
            dcc.Graph(
                id="heatmap_chart",
                figure=px.density_heatmap(
                    df,
                    x="InternetService",
                    y="PaymentMethod",
                    z="MonthlyCharges",
                    title="Heatmap of Monthly Charges by Service & Payment",
                    nbinsx=5,
                    nbinsy=5
                )
            )
        ])

# ---------------------------------------------------
# CALLBACKS FOR BAR & PIE
@app.callback(
    [Output("bar_chart", "figure"),
     Output("pie_chart", "figure")],
    Input("bar_pie_gender", "value")
)
def update_bar_pie(selected_gender):
    dff = df[df["gender"] == selected_gender]

    bar_fig = px.bar(dff, x="InternetService", y="MonthlyCharges", color="Contract",
                     title=f"Monthly Charges by Internet Service ({selected_gender})")
    pie_fig = px.pie(dff, names="Contract", values="MonthlyCharges",
                     title=f"Contract Type Distribution ({selected_gender})")
    return bar_fig, pie_fig

# CALLBACKS FOR LINE & SCATTER
@app.callback(
    [Output("line_chart", "figure"),
     Output("scatter_chart", "figure"),
     Output("page2_insight", "children")],
    Input("line_scatter_gender", "value")
)
def update_line_scatter(selected_gender):
    dff = df[df["gender"] == selected_gender]

    line_fig = px.line(dff, x="tenure", y="MonthlyCharges",
                       title=f"Monthly Charges over Tenure ({selected_gender})")

    scatter_fig = px.scatter(dff, x="tenure", y="TotalCharges",
                             size="MonthlyCharges", color="InternetService",
                             title=f"Total vs Tenure ({selected_gender})")

    avg_monthly = round(dff["MonthlyCharges"].mean(), 2)
    avg_total = round(dff["TotalCharges"].mean(), 2)
    insight = f"For {selected_gender} customers, average monthly charges are ${avg_monthly}, average total charges are ${avg_total}."
    return line_fig, scatter_fig, insight

# CALLBACK: More Insights button
@app.callback(
    Output("more_insights_output", "children"),
    Input("more_insights_btn", "n_clicks"),
    State("line_scatter_gender", "value")
)
def more_insights(n_clicks, selected_gender):
    if n_clicks == 0:
        return ""
    dff = df[df["gender"] == selected_gender]
    churn_rate = round((dff['Churn'].value_counts(normalize=True).get('Yes',0))*100,2)
    max_monthly = round(dff['MonthlyCharges'].max(), 2)
    max_total = round(dff['TotalCharges'].max(), 2)
    return f"Additional Insights: Churn Rate = {churn_rate}%, Max Monthly Charges = ${max_monthly}, Max Total Charges = ${max_total}"

# ---------------------------------------------------
# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
