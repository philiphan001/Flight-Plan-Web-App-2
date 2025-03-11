import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict

class FinancialPlotter:
    @staticmethod
    def plot_net_worth(years: List[int], net_worth: List[float], 
                      assets: List[float], liabilities: List[float]) -> None:
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
                       cash_flow: List[float]) -> None:
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add income bar
        fig.add_trace(
            go.Bar(x=years, y=income, name="Income", marker_color='#27AE60'),
            secondary_y=False
        )

        # Add stacked expense bars for each category
        colors = ['#E74C3C', '#F39C12', '#8E44AD', '#3498DB', '#16A085', 
                 '#D35400', '#2C3E50', '#7F8C8D', '#C0392B']

        # Sort expense categories to ensure consistent ordering
        expense_items = sorted(expenses.items())

        # Prioritize certain categories to appear at the bottom of the stack
        priority_categories = ['Mortgage Payment', 'Rent']
        for category in priority_categories:
            for item in expense_items:
                if item[0] == category:
                    expense_items.remove(item)
                    expense_items.insert(0, item)
                    break

        for (category, values), color in zip(expense_items, colors):
            fig.add_trace(
                go.Bar(x=years, y=values, name=category, marker_color=color),
                secondary_y=False
            )

        # Add cash flow line
        fig.add_trace(
            go.Scatter(x=years, y=cash_flow, name="Net Savings", 
                      line=dict(color='#2E86C1', width=2)),
            secondary_y=True
        )

        fig.update_layout(
            title='Income, Expenses, and Cash Flow Projection',
            barmode='stack',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )
        fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
        fig.update_yaxes(title_text="Net Savings ($)", secondary_y=True)

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