#  主要用来比较GARMIN导出的数据和POLAR数据心率值的
from matplotlib.pyplot import title
import pandas as pd

from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.ranges import Range1d
from bokeh.models.axes import LinearAxis
from bokeh.io import export_png
from time import strftime
from time import gmtime
from lxml import etree
from dateutil import parser

# Get data from .tcx
tree = etree.parse("garmin.tcx")
tree_polar = etree.parse("polar.tcx")
all_data = []
all_data_polar = []

root = tree.getroot()
root_polar = tree_polar.getroot()
points = root.findall('.//Trackpoint', root.nsmap)
points_polar = root_polar.findall('.//Trackpoint', root.nsmap)

for pt in points:
    t = pt.find('./Time', root.nsmap)
    bmp1 = pt.find('./HeartRateBpm/Value', root.nsmap)
    if bmp1 is None:
        bmp = bmp
    else:
        bmp = bmp1
    all_data.append({'time': parser.parse(t.text),
                        'bmp': int(float(bmp.text)),
                        }

                        )

for pt in points_polar:
    t = pt.find('./Time', root_polar.nsmap)
    bmp1 = pt.find('./HeartRateBpm/Value', root_polar.nsmap)
    if bmp1 is None:
        bmp = bmp
    else:
        bmp = bmp1

    all_data_polar.append({'time': parser.parse(t.text),
                    'bmp': int(float(bmp.text)),
                            }

                            )

# Visualize
output_file("garmin_polar.html")

source = ColumnDataSource(data=dict(
    time=[x['time'] for x in all_data],
    bmp=[x['bmp'] for x in all_data],
))

source_polar = ColumnDataSource(data=dict(
    time=[x['time'] for x in all_data_polar],
    bmp=[x['bmp'] for x in all_data_polar],
))

# df = pd.DataFrame(all_data)

hover = HoverTool(
    tooltips=[
        ('time', '@time{%T}'),
        # ％T https://docs.bokeh.org/en/latest/docs/reference/models/formatters.html#bokeh.models.NumeralTickFormatter
        # 24小时格式显示时间
        ('心率', '@bmp{0,0}'),
    ],

    formatters={
        "@time": "datetime",
    },

    mode='vline'
)

p = figure(x_axis_type="datetime", plot_width=1600, plot_height=800,
           tools=[hover], title="HR")  # 图的宽度和高度，像素值

# range for each data field
p.y_range = Range1d(80, 180)  # bmp
p.extra_y_ranges = {"HR_POLAR": Range1d(start=80, end=180),   
                    }  

# add the extra range to the right of the plot
p.add_layout(LinearAxis(y_range_name="HR_POLAR"), 'right')
# p.add_layout(LinearAxis(y_range_name="spd"), 'right')

# set axis text color
p.yaxis[0].major_label_text_color = "red"
p.yaxis[1].major_label_text_color = "blue"
# p.yaxis[2].major_label_text_color = "purple"


# plot !
#  p.line(df['time'], df['bmp'], legend='bmp', line_color="green", muted_color='green', muted_alpha=0.2)

p.line("time", "bmp", source=source, legend_label='garmin心率',
       line_color="red", muted_color='red', muted_alpha=0.2)

# p.line("time", "cad", source=source, legend_label='步频', line_color="blue", muted_color='blue', muted_alpha=0.2, y_range_name="cad")

p.line("time", "bmp", source=source_polar, legend_label='polar心率', color="blue",
       muted_color='blue', muted_alpha=0.2, y_range_name="HR_POLAR")

p.ygrid.minor_grid_line_color = 'navy'
p.ygrid.minor_grid_line_alpha = 0.1
p.ygrid.minor_grid_line_dash = [6, 4]
# setting for legend
p.legend.location = "top_right"
p.legend.click_policy = "mute"
export_png(p, filename="garmin_polar.png")   #保存成png

show(p)
