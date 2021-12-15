# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 19:00:00 2021

@author: amirs
"""

import numpy as np
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=stylesheet)


df1 = pd.read_csv('generationAnnualState.csv', index_col= False)
df2 =  pd.read_csv('emissionsAnnualState.csv', index_col= False)

df1.State = [aa.replace('Total','TOTAL') for aa in df1.State]
df2.Source = [aa.replace('All Sources','Total') for aa in df2.Source]

df1['YearStr'] = df1.Year
df2['YearStr'] = df2.Year

df1['GenTWh'] = round(df1.Generation/1000000,1) 
df2['CO2mmt'] = round(df2.CO2/1000000,1) 

df1.Year = pd.to_datetime(df1.Year, format = "%Y")
df2.Year = pd.to_datetime(df2.Year, format = "%Y")

energySources = ['Wind',
 'Geothermal',
 'Natural Gas',
 'Nuclear',
 'Hydroelectric Conventional',
 'Wood and Wood Derived Fuels',
 'Solar Thermal and Photovoltaic',
 'Petroleum',
 'Coal',
 'Total']

PAGE_SIZE = 5

stateNames = sorted(set(df1.State))

style_dict = dict(width='50%',
                  height='25px',
                  textAlign='center',
                  fontSize=20)

# =============================================================================
# APP Layout
# =============================================================================
app.layout = html.Div([

    html.H1("An Overview of US Energy Production & CO2 Emissions", style={'text-align': 'center'}),
    html.H2("1990 - 2020", style={'text-align': 'center'}),
    html.A('Data Source',
           href='https://www.eia.gov/',
           target='_blank'),
    html.Br(),
    html.H5("Select a Year:", style={'width': "100%",'text-align': 'left'}),
    dcc.Dropdown(id="slct_year",
                 options = [dict([('label', str(year)), ('value', year)]) for year in np.arange(1990,2021)],
                 multi=False,
                 value=1990,
                 style={'width': "33%"}
                 ),
    html.H5("Select an Energy Source:", style={'width': "100%",'text-align': 'left'}),
    dcc.Dropdown(id="slct_source",
                 options = [dict([('label', source), ('value', source)]) for source in energySources],
                 multi=False,
                 value='Total',
                 style={'width': "33%"}
                 ),
    html.H6("The map below shows the power generation in tera watt hours (TWh) in US States for the selected Year and the selected Energy Source.", style={'width': "100%",'text-align': 'left'}),
    html.H6("Hover over the map for State specific information.", style={'width': "100%",'text-align': 'left'}),
    dcc.Graph(id='gen_map', figure={}, 
              style = {'width': "100%"}),
    html.H6("Table below shows Energy and Emissions information for the top 10 States in the selected year and the selected energy source.", style={'width': "100%",'text-align': 'left'}),
    dash_table.DataTable(
        id='table_div',
        columns=[
        {"name": i, "id": i} for i in ['State', 'Source', 'Year', 'Power Generation (million MWh)',
                                       'Percent of US Total', 'CO2 Emissions (million MT)','Percent of US CO2']
        ],
        style_cell={                
            'maxWidth': 50
        },
        style_table = {'width': "100%"},
        style_data={
        'color': 'black',
        'backgroundColor': 'white'
        },
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(220, 220, 220)',
        }
        ],
        style_header={
        'backgroundColor': 'black',
        'color': 'white',
        'fontWeight': 'bold' 
        },
        page_size=PAGE_SIZE
   ),
   html.Br(),
   html.H6("Select a State", style={'width': "100%",'text-align': 'left'}),
    
   dcc.Dropdown(id="slct_state",
                 options = [dict([('label', state), ('value', state)]) for state in stateNames],
                 multi=False,
                 value= 'US-TOTAL',
                 style={'width': "50%",'x' : 0.5,'xanchor':'center'}
                 ),
   html.H6("The bar charts below show the energy production and CO2 emissions between 1990 and 2020 for a selected State or US-Total.", style={'width': "100%",'text-align': 'left'}),
   html.H6("Interact with each visualization to explore the environmental impact of different energy sources or to obtain insight on how US energy production resources are changing.", style={'width': "100%",'text-align': 'left'}),
   
   dcc.Graph(id='gen_bar', 
             style = {'width': "50%",'float':'left'}), 
   dcc.Graph(id='emis_bar', 
             style = {'width': "50%",'float':'right'}), 
])

# =============================================================================
# callbacks 
# =============================================================================
server = app.server

# Power Generation Map
@app.callback(
     Output(component_id='gen_map', component_property='figure'),
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_source', component_property='value')]
)
def update_genMap(year_slctd,source_slctd):

    df11 = df1.copy()
    df11 = df11[df11["Year"] == pd.to_datetime(year_slctd, format = "%Y")]
    df11 = df11[df11["Source"] == source_slctd]
    df11 = df11[df11["Producer"] == 'Total Electric Power Industry']
    df11 = df11[['us' not in state.lower() for state in df11['State']]]
    

    # Plotly Express
    fig = px.choropleth(
        data_frame=df11,
        locationmode='USA-states',
        locations='State',
        scope="usa",
        color='GenTWh',
        hover_data=['State','YearStr','GenTWh'],
        color_continuous_scale = px.colors.sequential.Reds,
        labels={'GenTWh': 'TWh'},
        width= 1500,
        height = 600,
        # template='plotly_dark',
        title = 'Energy Source: ' + source_slctd + '     Year: ' + str(year_slctd)  
        
    )
    fig.update_layout(
    # font_family="Times New Roman",
    font_color="black",
    font_size = 14,
    # title_font_family="Times New Roman",
    title_font_color="black",
    legend_title_font_color="black",
    title = {'x': 0.48,'xanchor':'center'},
    font = dict(size = 16),
    paper_bgcolor = "#D3D3D3"
    )
    return fig

# Table update
@app.callback(
    Output(component_id="table_div", component_property="data"),
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_source', component_property='value')]
)

def update_table(year_slctd,source_slctd):
    df11 = df1.copy()
    df11 = df11[df11["Year"] == pd.to_datetime(year_slctd, format = "%Y")]
    df11 = df11[df11["Source"] == source_slctd]
    df11 = df11[df11["Producer"] == 'Total Electric Power Industry']
    df11 = df11[['us' not in state.lower() for state in df11['State']]]
    df11 = df11[['State','Source','YearStr','GenTWh']].sort_values('GenTWh',ascending = False)
    df11['GenPct'] = round(100 * df11.GenTWh / sum(df11.GenTWh),1)
    df11.rename(columns={'GenTWh': 'Power Generation (million MWh)','YearStr': 'Year','GenPct':'Percent of US Total'}, inplace=True)
    
    
    df22 = df2.copy()
    df22 = df22[df22["Year"] == pd.to_datetime(year_slctd, format = "%Y")]
    df22 = df22[df22["Source"] == source_slctd]
    df22 = df22[df22["Producer"] == 'Total Electric Power Industry']
    df22 = df22[['us' not in state.lower() for state in df22['State']]]
    
    if len(df22) == 0:
        d = {'State': stateNames, 'CO2mmt': np.zeros(len(stateNames)), 'emisPct': np.zeros(len(stateNames))}
        df22 = pd.DataFrame(data=d)
    else:
        df22['emisPct'] = round(100 * df22.CO2 / sum(df22.CO2),1)
        
    df22 = df22.loc[:,['State','CO2mmt','emisPct']].sort_values('CO2mmt',ascending = False)
    
    df22.rename(columns={'CO2mmt': 'CO2 Emissions (million MT)','emisPct':'Percent of US CO2'}, inplace=True)
    df22.loc[df22['Percent of US CO2'].isna(),'Percent of US CO2'] = 0
    df11 = df11.merge(df22, left_on='State', right_on='State').head(10)
    return df11.to_dict('records')



# Generation bar chart update
@app.callback(
    Output(component_id='gen_bar', component_property='figure'),
    Input(component_id='slct_state', component_property='value')
)
def update_genBar(state_slctd):

    df11 = df1.copy()
    df11 = df11[df11["State"] == state_slctd]
    df11 = df11[df11["Producer"] == 'Total Electric Power Industry']
    
    df11 = df11[df11.Source != 'Other Gases']
    df11 = df11[df11.Source != 'Other Biomass']
    df11 = df11[df11.Source != 'Other']
    df11 = df11[df11.Source != 'Pumped Storage']
    df11 = df11[df11.Source != 'Total']
    
    
    df11 = df11.loc[:,['YearStr','Source','GenTWh']]
    fig = px.bar(
        df11,
        x="YearStr",
        y="GenTWh",
        color="Source",
        title=  state_slctd+ ' Energy Production by Source in: ')
    
    fig.update_layout(
        font_color="black",
        font_size = 12,
        title_font_color="Black",
        title_font_size = 18,
        legend_title_font_color="green",
        title = {'x': 0.05,'xanchor':'left'},
        paper_bgcolor = "#D3D3D3",
        xaxis_title="",
        yaxis_title="Energy Production (TWh)",
        legend_title="Energy Source",

    )
    return fig

# Emissions bar chart update
@app.callback(
    Output(component_id='emis_bar', component_property='figure'),
    Input(component_id='slct_state', component_property='value')
)
def update_emisBar(state_slctd):

    df22 = df2.copy()
    df22 = df22[df22["State"] == state_slctd]
    df22 = df22[df22["Producer"] == 'Total Electric Power Industry']
    
    df22 = df22[df22.Source != 'Other Gases']
    df22 = df22[df22.Source != 'Other Biomass']
    df22 = df22[df22.Source != 'Other']
    df22 = df22[df22.Source != 'Pumped Storage']
    df22 = df22[df22.Source != 'Total']
    
    
    df22 = df22.loc[:,['YearStr','Source','CO2mmt']]
    fig = px.bar(
        df22,
        x="YearStr",
        y="CO2mmt",
        color="Source",
        title= state_slctd + ' CO2 Emissions by Source in: ' )
    
    fig.update_layout(
        font_color="black",
        font_size = 12,
        title_font_color="Black",
        title_font_size = 18,
        legend_title_font_color="green",
        title = {'x': 0.05,'xanchor':'left'},
        paper_bgcolor = "#ADD8E6",
        xaxis_title="",
        yaxis_title="CO2 Emissions (million MT)",
        legend_title="Emission Source",

    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)