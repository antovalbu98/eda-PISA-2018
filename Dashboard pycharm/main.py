import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  #css: archivo con toda la parte bonita y de
                                                                       #colores de una web
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)   #cargar un estilo css

from datos import dftotales

fig = px.choropleth(dftotales, locations=dftotales.index.get_level_values(0),
                    color="Adjusted net national income per capita (constant 2010 US$) [NY.ADJ.NNTY.PC.KD]",
                    hover_name=dftotales.index,
                    color_continuous_scale='Burg',
                   title = "Adjusted net national income per capita (constant 2010 US$)",
                   labels = {"Adjusted net national income per capita (constant 2010 US$) [NY.ADJ.NNTY.PC.KD]" : "US$"})

fig2  = px.choropleth(dftotales, locations=dftotales.index.get_level_values(0),
                    color="PISA Index Mean",
                    hover_name=dftotales.index,
                      title = "PISA Index Mean",
                    color_continuous_scale='Burg')

trace1 = go.Bar(x = dftotales.sort_values('PISA Index Mean', ascending = True)['PISA Index Mean'].values,
               y = dftotales.sort_values('PISA Index Mean', ascending = True)['Country'].values,
                orientation= "h",
                name = 'Ranking',
                marker = dict(color = 'rgba(200, 100, 5, 0.5)',
                             line = dict(color = 'rgb(0, 0, 0)',
                                        width = 1))
               )


data = [trace1]
layout = go.Layout(barmode = "group",
                  title = 'PISA Ranking')
fig3 = go.Figure(data = data, layout = layout)
fig3.update_xaxes(tickangle = 0)



fig3 = go.Figure(data = data, layout = layout)



app.layout = html.Div(children=[
    html.H1(children="Educación, mercado laboral y economia"),    #cabecera

    html.Div(children= "Mapa con ingresos medios per capita, mapa con resultados medios PISA y ranking PISA"),                                #texto. children es lo que el elemento lleva dentro


    dcc.Graph(
        id='incomemap',                             #dcc: core components
        figure=fig,
        style={"height" : "100vh", "width" : "100vh"}
    ),
    dcc.Graph(
        id='pisamap',
        figure=fig2,
        style={"height" : "100vh", "width" : "100vh"}
    ),
    dcc.Graph(
            id='ranking',                             #dcc: core components
            figure=fig3,
        style={"height" : "200vh", "width" : "100vh"}
        ),
])

from dash.dependencies import Input, Output, State
@app.callback(
    Output('incomemap', 'figure'),
    Output('pisamap', 'figure'),
    Output('ranking', 'figure'),
[Input('ranking', 'figure')])

def update_graphs_selector(selected_type):
    filtered_df = dftotales[dftotales["Country"].isin(selected_type)]

    fig = px.histogram(filtered_df, x="Rating", range_x=[0.8, 5.2])
    fig2 = px.box(filtered_df, x="Category", y="Rating", color="Category", range_y=[0.8, 5.2])

    fig.update_layout()
    fig2.update_layout()

    return fig, fig2
    


if __name__ == '__main__':
    app.run_server(debug=True)
