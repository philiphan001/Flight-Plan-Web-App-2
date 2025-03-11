import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List

class FinancialPlotter:
    @staticmethod
    def plot_net_worth(years: List[int], net_worth: List[float]) -> None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=net_worth,
                                mode='lines+markers',
                                name='Net Worth',
                                line=dict(color='#2E86C1', width=2)))
        fig.update_layout(
            title='Net Worth Projection',
            xaxis_title='Year',
            yaxis_title='Net Worth ($)',
            template='plotly_white'
        )
        st.plotly_chart(fig)

    @staticmethod
    def plot_cash_flow(years: List[int], income: List[float], 
                       expenses: List[float], cash_flow: List[float]) -> None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(x=years, y=income, name="Income", marker_color='#27AE60'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=years, y=expenses, name="Expenses", marker_color='#E74C3C'),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=years, y=cash_flow, name="Cash Flow", 
                      line=dict(color='#2E86C1', width=2)),
            secondary_y=True
        )

        fig.update_layout(
            title='Income, Expenses, and Cash Flow Projection',
            barmode='group',
            template='plotly_white'
        )
        fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
        fig.update_yaxes(title_text="Cash Flow ($)", secondary_y=True)

        st.plotly_chart(fig)

    @staticmethod
    def plot_assets_liabilities(years: List[int], assets: List[float], 
                              liabilities: List[float]) -> None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=assets,
                                mode='lines+markers',
                                name='Assets',
                                line=dict(color='#27AE60', width=2)))
        fig.add_trace(go.Scatter(x=years, y=liabilities,
                                mode='lines+markers',
                                name='Liabilities',
                                line=dict(color='#E74C3C', width=2)))
        fig.update_layout(
            title='Assets and Liabilities Projection',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            template='plotly_white'
        )
        st.plotly_chart(fig)
    @staticmethod
    def plot_milestones(years: List[int], net_worth: List[float], 
                      milestones: Dict[int, List[str]]) -> None:
        """Create a plot showing milestones on the net worth trajectory."""
        fig = go.Figure()
        
        # Add net worth line
        fig.add_trace(go.Scatter(x=years, y=net_worth,
                               mode='lines+markers',
                               name='Net Worth',
                               line=dict(color='#2E86C1', width=2)))
        
        # Add milestone markers
        for year, milestone_list in milestones.items():
            for name in milestone_list:
                fig.add_annotation(
                    x=year,
                    y=net_worth[year],
                    text=name,
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#E74C3C",
                    arrowsize=1,
                    arrowwidth=1,
                    ax=-40,
                    ay=-40
                )
        
        fig.update_layout(
            title='Net Worth with Life Milestones',
            xaxis_title='Year',
            yaxis_title='Net Worth ($)',
            template='plotly_white'
        )
        st.plotly_chart(fig)
