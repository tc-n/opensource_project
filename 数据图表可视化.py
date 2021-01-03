#数据图表可视化

import numpy as np
import pandas as pd
import pymysql
import pyecharts.options as opts
from pyecharts.charts import Line  # 折线图
from pyecharts.charts import Bar  # 条形图
from pyecharts.charts import Pie  # 饼图
from pyecharts.globals import ThemeType


# 用来生成每年票房和时间的关系图以及每年票房前十柱状图
def createYearlyPic(name):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='tiger',
        port=3306,
        db='pluto'
    )

    data = pd.read_sql('select 年度排名, 电影名称, 票房, 上映时间 from ' + name + '票房数据', conn)

    # 字符串类型数据的处理
    data.dropna(axis=0, subset=['上映时间'], inplace=True)  # 删除上映时间中的缺失值,并替换原数据表
    data = data[data['上映时间'].str.contains(name)]  # 只保留特定年份的数据
    # 将字符串类型的时间数据转化成datetime64类型 .dt.date用来去掉时间，只保留日期
    data['上映时间'] = pd.to_datetime(data['上映时间']).dt.date
    # print(data['上映时间'])

    # 影票数据 单位万 由字符串类型转化成float64类型
    data['票房'] = data['票房'].str.replace('亿', 'e5')
    data['票房'] = data['票房'].str.strip('万')
    data['票房'] = data['票房'].astype(np.float64)

    # 统计上映时间缺失值的数量
    # print(data['上映时间'].isnull().value_counts())

    # 删除上映时间中的缺失值,并替换原数据表
    data.dropna(axis=0, subset=['上映时间'], inplace=True)

    daily_data = data.groupby('上映时间')['票房'].sum()  # 根据上映时间进行分组，然后求票房列的和

    # 线性关系图
    l1 = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.PURPLE_PASSION,
                                     width='1200px',
                                     height='800px'
                                     ))
            .add_xaxis(xaxis_data=daily_data.index)
            .add_yaxis(
            series_name="票房",
            y_axis=daily_data.values,
            symbol_size=8,  # 标记的大小
            is_hover_animation=True,  # 是否开启 hover 在拐点标志上的提示动画效果
            label_opts=opts.LabelOpts(is_show=False),  # 标签配置项
            linestyle_opts=opts.LineStyleOpts(width=1.5, color='rgb(175,238,238)'),  # 线条颜色
            is_smooth=True,
            itemstyle_opts=opts.ItemStyleOpts(color='rgb(240,255,255)')  # 点的颜色
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title=name + "票房时间关系图", subtitle="数据来自电影票房网", pos_left="center",
                title_link="http://58921.com/alltime/" + str(name),  # 主标题的超链接
                # 主副标题文字格式
                title_textstyle_opts=opts.TextStyleOpts(font_family='monospace', font_size=25),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=15)
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),  # 'axis': 坐标轴触发提示信息

            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=True,
                    is_realtime=True,  # 拖动时，实时更新系列的视图
                    range_start=0,  # 数据窗口范围的起始百分比
                    range_end=100
                )
            ],

            xaxis_opts=opts.AxisOpts(
                name='时间',
                type_="category",  # 'category': 类目轴，适用于离散的类目数据，为该类型时必须通过 data 设置类目数据
                boundary_gap=False,  # 坐标轴两边留白策略
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),  # 坐标轴刻度线配置项
            ),
            yaxis_opts=opts.AxisOpts(max_='dataMax', name="票房(万元)"),  # 可以设置成特殊值 'dataMax'，此时取数据在该轴上的最大值作为最大刻度
            legend_opts=opts.LegendOpts(pos_left="left"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature={
                    "dataZoom": {"yAxisIndex": "none"},  # 数据区域缩放
                    "restore": {},  # 配置项还原
                    "saveAsImage": {},  # 保存为图片
                },
            )
        )
    )
    l1.render(name + "票房时间关系图.html")

    # 票房前十柱状图
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.CHALK,
                                    width='1200px',
                                    height='800px'
                                    ))
        .add_xaxis(xaxis_data=data['电影名称'][0:9].tolist())
        .add_yaxis(
            series_name="票房",
            y_axis=data['票房'][0:9].tolist(),
            itemstyle_opts=opts.ItemStyleOpts(color='rgb(240,255,255)'),
            category_gap=40
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=name + "年度票房前十电影",
                                      pos_left="right",
                                      title_link="http://58921.com/alltime/" + str(name),  # 主标题的超链接
                                      # 主副标题文字格式
                                      title_textstyle_opts=opts.TextStyleOpts(font_family='monospace', font_size=30),
                                      ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=20),
                name='电影名称',
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),  # 坐标轴刻度线配置项
            ),
            yaxis_opts=opts.AxisOpts(max_='dataMax', name="票房(万元)"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left='1%',
                feature={
                    "dataZoom": {"yAxisIndex": "none"},  # 数据区域缩放
                    "restore": {},  # 配置项还原
                    "saveAsImage": {},  # 保存为图片
                },
            )
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="min", name="最小值"),
                    opts.MarkLineItem(type_="max", name="最大值"),
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
    )
    c.render(name + "年度票房前十电影.html")


# 生成每年导演平均票房的前十名的柱状图
def createDirPic(name):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='tiger',
        port=3306,
        db='pluto'
    )

    data = pd.read_sql('select 导演, 票房 from ' + str(name) + '票房数据', conn)

    # 将有多名导演的电影的导演数据分开
    data_new = data.drop(['导演'], axis=1).join(
        data['导演'].str.split('  ', expand=True).stack().reset_index(level=1, drop=True).rename('导演')
    )

    # 删除表中导演的缺失值,并替换原数据表
    data_new.dropna(axis=0, subset=['导演'], inplace=True)
    # 以导演名称为分组条件分组

    # 影票数据 单位万 由字符串类型转化成float64类型
    data_new['票房'] = data_new['票房'].str.replace('亿', 'e5')
    data_new['票房'] = data_new['票房'].str.strip('万')
    data_new['票房'] = data_new['票房'].astype(np.float64)

    data_new.drop_duplicates(subset=["票房"], keep='first', inplace=True)  # 删除重复项
    daily_data = data_new.groupby('导演')['票房'].mean().sort_values(ascending=False)
    # 根据上映时间进行分组，然后求票房列的平均值,mean()

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.CHALK,
                                    width='1200px',
                                    height='800px'
                                    ))
            .add_xaxis(xaxis_data=daily_data[0:19].index.tolist())
            .add_yaxis(
            series_name="票房",
            y_axis=daily_data[0:19].values.tolist(),
            itemstyle_opts=opts.ItemStyleOpts(color='rgb(240,255,255)'),
            category_gap=18
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title=str(name) + "年度平均票房前二十的导演",
                                      pos_left="right",
                                      title_link="http://58921.com/alltime/" + str(name),  # 主标题的超链接
                                      # 主副标题文字格式
                                      title_textstyle_opts=opts.TextStyleOpts(font_family='monospace', font_size=30),
                                      ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=30),
                name='导演名称',
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),  # 坐标轴刻度线配置项
            ),
            yaxis_opts=opts.AxisOpts(max_='dataMax', name="票房(万元)"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left='1%',
                feature={
                    "dataZoom": {"yAxisIndex": "none"},  # 数据区域缩放
                    "restore": {},  # 配置项还原
                    "saveAsImage": {},  # 保存为图片
                },
            )
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="min", name="最小值"),
                    opts.MarkLineItem(type_="max", name="最大值"),
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
    )
    c.render(str(name) + "年度平均票房前二十的导演.html")


# 生成每年演员平均票房的前十名的柱状图
def createActPic(name):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='tiger',
        port=3306,
        db='pluto'
    )

    data = pd.read_sql('select 主演, 票房 from ' + str(name) + '票房数据', conn)

    # 将有多名主演的电影的主演数据分开
    data_new = data.drop(['主演'], axis=1).join(
        data['主演'].str.split(' ', expand=True).stack().reset_index(level=1, drop=True).rename('主演')
    )

    # 删除表中主演的缺失值,并替换原数据表
    data_new.dropna(axis=0, subset=['主演'], inplace=True)
    # 以主演名称为分组条件分组

    # 影票数据 单位万 由字符串类型转化成float64类型
    data_new['票房'] = data_new['票房'].str.replace('亿', 'e5')
    data_new['票房'] = data_new['票房'].str.strip('万')
    data_new['票房'] = data_new['票房'].astype(np.float64)

    data_new.drop_duplicates(subset=["票房"], keep='first', inplace=True)  # 删除重复项
    daily_data = data_new.groupby(['主演'])['票房'].mean().sort_values(ascending=False)
    # 根据上映时间进行分组，然后求票房列的平均值,mean()

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.CHALK,
                                    width='1200px',
                                    height='800px'
                                    ))
            .add_xaxis(xaxis_data=daily_data[0:19].index.tolist())
            .add_yaxis(
            series_name="票房",
            y_axis=daily_data[0:19].values.tolist(),
            itemstyle_opts=opts.ItemStyleOpts(color='rgb(240,255,255)'),
            category_gap=18
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title=str(name) + "年度平均票房前二十的主演",
                                      pos_left="right",
                                      title_link="http://58921.com/alltime/" + str(name),  # 主标题的超链接
                                      # 主副标题文字格式
                                      title_textstyle_opts=opts.TextStyleOpts(font_family='monospace', font_size=30),
                                      ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=30),
                name='主演名称',
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),  # 坐标轴刻度线配置项
            ),
            yaxis_opts=opts.AxisOpts(max_='dataMax', name="票房(万元)"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left='1%',
                feature={
                    "dataZoom": {"yAxisIndex": "none"},  # 数据区域缩放
                    "restore": {},  # 配置项还原
                    "saveAsImage": {},  # 保存为图片
                },
            )
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="min", name="最小值"),
                    opts.MarkLineItem(type_="max", name="最大值"),
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
    )
    c.render(str(name) + "年度平均票房前二十的主演.html")


def createLebPic(name):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='tiger',
        port=3306,
        db='pluto'
    )

    data = pd.read_sql('select 类型, 票房 from ' + str(name) + '票房数据', conn)

    # 将有多种类型的电影的类型数据分开
    data_new = data.drop(['类型'], axis=1).join(
        data['类型'].str.split(' ', expand=True).stack().reset_index(level=1, drop=True).rename('类型')
    )

    # 删除表中没有类型数据的电影,并替换原数据表
    data_new.dropna(axis=0, subset=['类型'], inplace=True)
    # 以类型为分组条件分组

    # 影票数据 单位万 由字符串类型转化成float64类型
    data_new['票房'] = data_new['票房'].str.replace('亿', 'e5')
    data_new['票房'] = data_new['票房'].str.strip('万')
    data_new['票房'] = data_new['票房'].astype(np.float64)

    daily_data = data_new.groupby(['类型'])['票房'].sum()
    # [list(z) for z in zip(daily_data.index, daily_data.values)]

    data_pair = [list(z) for z in zip(daily_data.index, daily_data.values)]
    data_pair.sort(key=lambda x: x[1])

    (
        Pie(init_opts=opts.InitOpts(width="1200px", height="800px", bg_color="#2c343c"))
            .add(
            series_name="标签类型",
            data_pair=data_pair,
            rosetype="radius",
            radius="55%",
            center=["50%", "50%"],
            label_opts=opts.LabelOpts(is_show=False, position="center"),

        )
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title=str(name) + "电影各类型占比",
                pos_left="center",
                pos_top="20",
                title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
            .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{a} <br/>{b}:{d}%"
            ),
            label_opts=opts.LabelOpts(color="rgba(255, 255, 255, 0.3)"),
        )
            .render(str(name) + "电影各类型占比.html")
    )


def main():
    name = "2019"
    createYearlyPic(name)
    createDirPic(name)
    createActPic(name)
    createLebPic(name)


main()