import plotly.graph_objects as go
import plotly.express as px


def lineChart(df,template='none',x='al_periodo',y='ACTIVO'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df[y],mode='lines',name=y,hovertemplate='<br><b>Periodo</b>:%{x}'+'<br><b>Importe</b>: %{y:$.2f}<br>'))
    fig.update_layout(template = template,title=y)
    fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=14,
        font_family="sans-serif"
        ),
    )
    fig.update_xaxes(type='category')
    return fig

def scatterLine(title,df_data,df_train,primera_partida,segunda_partida,moneda,inicio,fin,inicio_test):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_data.index, y=df_data[primera_partida],
                        mode='lines',
                        name=primera_partida))
    fig.add_trace(go.Scatter(x=df_train.index, y=df_train[segunda_partida],
                        line=dict(color='black', width=4, dash='dot'),
                        name='Pronóstico'))
    fig.update_layout( title=title,template='none',yaxis_title=moneda,margin=dict(l=60, r=20, t=80, b=40),)#
    fig.update_layout(legend=dict(yanchor="top",y=1.02,xanchor="left",x=0.01,bgcolor="#F1F2F7",orientation="h",))
    fig.update_xaxes(rangeslider_visible=True)
    fig.add_vrect(x0=inicio, x1=fin, 
              annotation_text="pronóstico", annotation_position="top left",
              fillcolor="blue", opacity=0.25, line_width=0)
    if inicio!=inicio_test:
        fig.add_vrect(x0=inicio_test, x1=inicio, 
                annotation_text="", annotation_position="top right",
                fillcolor="green", opacity=0.25, line_width=0)
    return fig