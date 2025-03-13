import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict
import pandas as pd
import numpy as np

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

        # Update layout
        fig.update_layout(
            title='Income, Expenses, and Cash Flow Projection',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='stack',  # Stack the income bars only
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            bargap=0.15,  # Gap between bars
            bargroupgap=0.2  # Gap between bar groups (income vs expenses)
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

    @staticmethod
    def plot_home_value_breakdown(years: List[int], home_value: List[float], 
                                mortgage_balance: List[float]) -> None:
        """Plot the home value components over time."""
        fig = go.Figure()

        # Calculate equity (home value minus mortgage)
        equity = [v - m for v, m in zip(home_value, mortgage_balance)]

        # Add home value bar
        fig.add_trace(go.Bar(
            x=years,
            y=home_value,
            name='Home Value',
            marker_color='#27AE60',
            offsetgroup='value'
        ))

        # Add mortgage balance bar
        fig.add_trace(go.Bar(
            x=years,
            y=mortgage_balance,
            name='Mortgage Balance',
            marker_color='#E74C3C',
            offsetgroup='mortgage'
        ))

        # Add equity bar
        fig.add_trace(go.Bar(
            x=years,
            y=equity,
            name='Home Equity',
            marker_color='#2E86C1',
            offsetgroup='equity'
        ))

        fig.update_layout(
            title='Home Value Components Over Time',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='group',  # Place bars side by side
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            bargap=0.15,
            bargroupgap=0.1
        )

        st.plotly_chart(fig)

    @staticmethod
    def plot_salary_heatmap(
        salary_data: pd.DataFrame,
        locations: List[str],
        occupations: List[str],
        title: str = "Salary Distribution by Location and Occupation"
    ) -> None:
        """
        Create an interactive heatmap showing salary distribution across locations and occupations.

        Args:
            salary_data: DataFrame with salary values
            locations: List of location names
            occupations: List of occupation titles
            title: Title for the plot
        """
        # Create the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=salary_data.values,
            x=locations,
            y=occupations,
            hoverongaps=False,
            hovertemplate="Location: %{x}<br>" +
                         "Occupation: %{y}<br>" +
                         "Salary: $%{z:,.0f}<extra></extra>",
            colorscale='Viridis',
            colorbar=dict(
                title=dict(
                    text='Annual Salary ($)',
                    side='right'
                ),
                thickness=20,
                tickformat='$,.0f'
            )
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title='Location',
                tickangle=45,
                side='bottom'
            ),
            yaxis=dict(
                title='Occupation',
                autorange='reversed'  # Reverse y-axis to match traditional heatmap layout
            ),
            height=600,
            margin=dict(t=80, r=50, b=100, l=150),  # Adjust margins for better layout
            template='plotly_white'
        )

        # Add annotations for salary values
        annotations = []
        for i, occupation in enumerate(occupations):
            for j, location in enumerate(locations):
                annotations.append(
                    dict(
                        text=f"${salary_data.iloc[i, j]:,.0f}",
                        x=location,
                        y=occupation,
                        showarrow=False,
                        font=dict(
                            color='white' if salary_data.iloc[i, j] > salary_data.values.mean() else 'black',
                            size=10
                        )
                    )
                )
        fig.update_layout(annotations=annotations)

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)