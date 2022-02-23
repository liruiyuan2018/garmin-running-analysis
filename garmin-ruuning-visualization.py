import pandas as pd

from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.ranges import Range1d
from bokeh.models.axes import LinearAxis

from lxml import etree
from dateutil import parser


# Get data from .tcx
tree = etree.parse("activity_4019358445.tcx")
root = tree.getroot()

points = root.findall('.//Trackpoint', root.nsmap)

all_data = []

for pt in points:
    t = pt.find('./Time', root.nsmap)
    
    bmp1 = pt.find('./HeartRateBpm/Value', root.nsmap)
    if bmp1 == None :
        bmp = bmp
    else:
      bmp = bmp1  
   # 以心率为例子，可能得到的部分节点没有心率，取上个心率值补全，其它节点也需要检查
    cad = pt.find('./Extensions/ns3:TPX/ns3:RunCadence', root.nsmap)
    dis = pt.find('./DistanceMeters', root.nsmap)
    spd = pt.find('./Extensions/ns3:TPX/ns3:Speed', root.nsmap)
    
    all_data.append( { 'time' : parser.parse(t.text),
                       'bmp' : int(float((bmp.text)),
                      # 这里用int 报错，需改为int(float())
                       'cad' : float(cad.text),
                       'dis' : float(dis.text),
                       'spd' : float(spd.text) 
                     } 
                   )


# Visualize
output_file("final.html")

source = ColumnDataSource(data=dict(
    time=[x['time'] for x in all_data],
    bmp=[x['bmp'] for x in all_data],
    # dis=[x['dis'] for x in all_data],
    # cad=[x['cad'] for x in all_data],
    # spd=[x['spd'] for x in all_data]
))
#  用ColummnDataSource似乎才能搞定TOOLTIPS                      
                      
                      
df = pd.DataFrame(all_data)

hover = HoverTool(
    tooltips=[
        ( '@time', '@time{%R}'),
        ( 'bmp', '@bmp{000.}'),
        ( 'cad', '@cad'),
        ( 'spd', '@spd')
    ],

    formatters={
        'time' : 'datetime',
    },

    mode='vline'
)

p = figure(x_axis_type="datetime", plot_width=600, plot_height=300, tools=[hover], title="all-data_time_hover")

# range for each data field
p.y_range = Range1d(0, 220)  # bmp
p.extra_y_ranges = {"cad": Range1d(start=0, end=140),   # RunCadence
                    "spd": Range1d(start=0, end=10.0) }  # Speed

# add the extra range to the right of the plot
p.add_layout(LinearAxis(y_range_name="cad"), 'right')
p.add_layout(LinearAxis(y_range_name="spd"), 'right')

# set axis text color
p.yaxis[0].major_label_text_color = "red"  
p.yaxis[1].major_label_text_color = "blue"  
p.yaxis[2].major_label_text_color = "purple"  


## plot !
p.line(“time”, "bmp", legend_label='cad',source=source, line_color="red", muted_color='red', muted_alpha=0.2)  #新版本需要用legend_label 

p.line("time", "cad", legend_label='cad', line_color="blue", muted_color='blue', muted_alpha=0.2, y_range_name='cad')

p.line("time", "spd", legend_label='spd', color="purple", muted_color='purple', muted_alpha=0.2, y_range_name='spd')


# setting for legend
p.legend.location = "top_right"
p.legend.click_policy="mute"



show(p)

