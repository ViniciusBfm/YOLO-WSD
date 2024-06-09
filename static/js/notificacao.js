var graphs = {{ graphJSON | safe }};
Plotly.newPlot('grafico', graphs.data, graphs.layout);