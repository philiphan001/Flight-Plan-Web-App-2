import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict

class FinancialPlotter:
    @staticmethod
    def plot_net_worth(years: List[int], net_worth: List[float], 
                      assets: List[float], liabilities: List[float],
                      savings: List[float] = None) -> None:
        fig = go.Figure()

        # Add assets as positive bars
        fig.add_trace(go.Bar(x=years, y=assets,
                            name='Assets',
                            marker_color='#27AE60'))

        # Add liabilities as negative bars
        fig.add_trace(go.Bar(x=years, y=[-x for x in liabilities],
                            name='Liabilities',
                            marker_color='#E74C3C'))

        # Add net worth line on top
        fig.add_trace(go.Scatter(x=years, y=net_worth,
                                mode='lines+markers',
                                name='Net Worth',
                                line=dict(color='#2E86C1', width=2)))

        # Add savings line if provided
        if savings:
            fig.add_trace(go.Scatter(x=years, y=savings,
                                   mode='lines',
                                   name='Savings',
                                   line=dict(color='#F1C40F', width=2, dash='dot')))

        fig.update_layout(
            title='Net Worth Components',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='relative',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )
        st.plotly_chart(fig)

    @staticmethod
    def plot_cash_flow(years: List[int], income: List[float], 
                       expenses: Dict[str, List[float]], total_expenses: List[float],
                       cash_flow: List[float], income_streams: Dict[str, List[float]] = None) -> None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add stacked income bars in one group
        colors = {'Primary Income': '#27AE60', 'Spouse Income': '#2ECC71'}
        for income_type, values in income_streams.items():
            fig.add_trace(
                go.Bar(x=years, y=values,
                      name=income_type,
                      marker_color=colors.get(income_type, '#27AE60'),
                      offsetgroup="income"),  # Group all income bars together
                secondary_y=False
            )

        # Add expenses bar
        fig.add_trace(
            go.Bar(x=years, y=total_expenses,
                  name="Total Expenses",
                  marker_color='#E74C3C',
                  offsetgroup="expenses"),  # Different group for expenses
            secondary_y=False
        )

        # Add cash flow line
        fig.add_trace(
            go.Scatter(x=years, y=cash_flow,
                      name="Net Savings",
                      line=dict(color='#2E86C1', width=2)),
            secondary_y=True
        )

        fig.update_layout(
            title='Income, Expenses, and Cash Flow Projection',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='relative',  # Stack bars within groups
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            bargroupgap=0.2  # Add gap between income/expense groups
        )

        # Update axes labels
        fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
        fig.update_yaxes(title_text="Net Savings ($)", secondary_y=True)

        st.plotly_chart(fig)

    @staticmethod
    def plot_assets_liabilities(years: List[int], assets: List[float], 
                              liabilities: List[float], savings: List[float] = None) -> None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=assets,
                                mode='lines+markers',
                                name='Assets',
                                line=dict(color='#27AE60', width=2)))
        fig.add_trace(go.Scatter(x=years, y=liabilities,
                                mode='lines+markers',
                                name='Liabilities',
                                line=dict(color='#E74C3C', width=2)))

        # Add savings line if provided
        if savings:
            fig.add_trace(go.Scatter(x=years, y=savings,
                                   mode='lines',
                                   name='Savings',
                                   line=dict(color='#F1C40F', width=2, dash='dot')))

        fig.update_layout(
            title='Assets and Liabilities Projection',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )
        st.plotly_chart(fig)