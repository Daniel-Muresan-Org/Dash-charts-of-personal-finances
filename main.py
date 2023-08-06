import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Assuming you have already read the CSV and have a DataFrame called 'df'
df = pd.read_csv('./breakdown.csv')

# Check the DataFrame and column names
print(df.head())
print(df.columns)

# Convert 'date' column to datetime format if needed
df['date'] = pd.to_datetime(df['date'])

# Remove commas from 'abs amount' column and convert to numeric
df['abs amount'] = df['abs amount'].str.replace(',', '').astype(float)

# Sort the DataFrame by the 'date' column
df = df.sort_values(by='date')

# Compute the cumulative sum over time
df['cumulative_sum'] = df['abs amount'].cumsum()

# Set up the Dash app
app = dash.Dash(__name__)

# Define the options for the timeframe selection dropdown
timeframe_options = [
    {'label': 'Yearly', 'value': 'yearly'},
    {'label': 'Quarterly', 'value': 'quarterly'},
    {'label': 'Monthly', 'value': 'monthly'},
    {'label': 'Daily', 'value': 'daily'}
]

app.layout = html.Div([
    dcc.Graph(id='line-chart'),
    dcc.Dropdown(
        id='timeframe-selector',
        options=timeframe_options,
        value='yearly',
        style={'width': '50%'}
    )
])

@app.callback(
    Output('line-chart', 'figure'),
    Input('timeframe-selector', 'value')
)
def update_chart(timeframe):
    if timeframe == 'yearly':
        # Group the DataFrame by year and sum 'abs amount' and 'cumulative_sum' for each year
        grouped_df = df.groupby(df['date'].dt.year).agg({
            'abs amount': 'sum',
            'cumulative_sum': 'max'
        }).reset_index()

        # Set 'date' as the index to use .index for the x-axis values
        grouped_df.set_index('date', inplace=True)
        x = grouped_df.index

    elif timeframe == 'quarterly':
        # Group the DataFrame by quarter and sum 'abs amount' and 'cumulative_sum' for each quarter
        grouped_df = df.groupby(df['date'].dt.to_period('Q').dt.start_time).agg({
            'abs amount': 'sum',
            'cumulative_sum': 'max'
        }).reset_index()

        # Set 'date' as the index to use .index for the x-axis values
        grouped_df.set_index('date', inplace=True)
        x = grouped_df.index

    elif timeframe == 'monthly':
        # Group the DataFrame by month and sum 'abs amount' and 'cumulative_sum' for each month
        grouped_df = df.groupby(df['date'].dt.to_period('M').dt.start_time).agg({
            'abs amount': 'sum',
            'cumulative_sum': 'max'
        }).reset_index()

        # Set 'date' as the index to use .index for the x-axis values
        grouped_df.set_index('date', inplace=True)
        x = grouped_df.index

    else:  # Daily view
        grouped_df = df
        x = df['date']

    # Create the line chart with two y-axes
    trace1 = go.Scatter(
        x=x,
        y=grouped_df['abs amount'],
        mode='lines+markers',
        name='Abs Amount',
        line=dict(color='blue')
    )

    trace2 = go.Scatter(
        x=x,
        y=grouped_df['cumulative_sum'],
        mode='lines',  # Use 'lines' instead of 'lines+markers'
        name='Cumulative Sum',
        line=dict(color='orange'),
        yaxis='y2'  # Use the second y-axis for this trace
    )

    layout = go.Layout(
        title='Abs Amount and Cumulative Sum over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Abs Amount'),
        yaxis2=dict(
            title='Cumulative Sum',
            overlaying='y',
            side='right'
        ),
        hovermode='closest'
    )

    return {'data': [trace1, trace2], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
