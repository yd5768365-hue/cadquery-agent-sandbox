import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """创建指标卡片"""
    import streamlit as st
    
    if delta:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )
    else:
        st.metric(label=title, value=value)

def create_time_series_chart(dates, values, title="时间序列", y_label="值"):
    """创建时间序列图表"""
    df = pd.DataFrame({
        '日期': dates,
        y_label: values
    })
    
    fig = px.line(
        df, 
        x='日期', 
        y=y_label,
        title=title,
        markers=True
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_pie_chart(labels, values, title="分布图"):
    """创建饼图"""
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        marker=dict(
            colors=px.colors.qualitative.Set3
        )
    )])
    
    fig.update_layout(
        title=title,
        showlegend=True,
        height=350
    )
    
    return fig

def create_bar_chart(categories, values, title="柱状图", y_label="值"):
    """创建柱状图"""
    df = pd.DataFrame({
        '类别': categories,
        y_label: values
    })
    
    fig = px.bar(
        df,
        x='类别',
        y=y_label,
        title=title,
        color=y_label,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        height=350
    )
    
    return fig

def create_scatter_plot(x_data, y_data, x_label="X", y_label="Y", title="散点图"):
    """创建散点图"""
    df = pd.DataFrame({
        x_label: x_data,
        y_label: y_data
    })
    
    fig = px.scatter(
        df,
        x=x_label,
        y=y_label,
        title=title,
        trendline="ols",
        trendline_color_override="red"
    )
    
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    
    return fig

def create_heatmap(data, x_labels, y_labels, title="热力图"):
    """创建热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='RdBu_r',
        text=data,
        texttemplate='%{text:.2f}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=title,
        height=400
    )
    
    return fig

def create_histogram(data, bins=30, title="分布直方图", x_label="值"):
    """创建直方图"""
    fig = go.Figure(data=[go.Histogram(
        x=data,
        nbinsx=bins,
        marker_color='rgb(55, 83, 109)'
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title="频次",
        bargap=0.1
    )
    
    return fig

def create_box_plot(data_dict, title="箱线图"):
    """创建箱线图"""
    fig = go.Figure()
    
    for name, data in data_dict.items():
        fig.add_trace(go.Box(
            y=data,
            name=name,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title=title,
        yaxis_title="值",
        showlegend=True
    )
    
    return fig

def create_3d_scatter(x, y, z, color_data=None, title="3D 散点图"):
    """创建 3D 散点图"""
    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=5,
            color=color_data if color_data is not None else z,
            colorscale='Viridis',
            showscale=True,
            opacity=0.8
        )
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        height=600
    )
    
    return fig