z
import plotly

from plotly.graph_objs import Scatter, Layout

fig = py.get_figure('https://plot.ly/~jackp/8715', raw=True)

# import plotly.io as pio
# static_image_bytes = pio.to_image(fig, format='png')
# pio.write_image(fig, file='plotly_static_image.png', format='png')

plotly.offline.plot({
"data": [
    Scatter(x=[1, 2, 3, 4], y=[4, 1, 3, 7])
],
"layout": Layout(
    title="hello world"
)
}, filename="assets/plotsito.html", auto_open=False)