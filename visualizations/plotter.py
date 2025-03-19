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
        # Create the plot
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

        # Create and display the data table
        df = pd.DataFrame({
            'Year': years,
            'Total Assets': ['${:,.0f}'.format(x) for x in assets],
            'Total Liabilities': ['${:,.0f}'.format(x) for x in liabilities],
            'Net Worth': ['${:,.0f}'.format(x) for x in net_worth],
        })
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def plot_cash_flow(years: List[int], income: List[float], 
                      expenses: Dict[str, List[float]], total_expenses: List[float],
                      cash_flow: List[float], income_streams: Dict[str, List[float]] = None) -> None:
        """Plot cash flow with stacked income streams and separate expenses."""
        # Create figure with subplots - one for cash flow, one for expense pie chart
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.7, 0.3],
            specs=[[{"secondary_y": True}, {"type": "pie"}]],
            subplot_titles=('Income, Expenses, and Cash Flow Projection', 'Latest Year Expense Breakdown')
        )

        # Create cumulative sums for income stacking
        cumsum = np.zeros(len(years))
        colors = {'Primary Income': '#27AE60', 'Spouse Income': '#2ECC71', 'Part-Time Work': '#82E0AA'}

        # Add income streams as stacked bars
        for income_type, values in income_streams.items():
            fig.add_trace(
                go.Bar(
                    x=years,
                    y=values,
                    name=income_type,
                    marker_color=colors.get(income_type, '#27AE60'),
                    base=cumsum,  # Start from previous cumulative sum
                    offsetgroup=0  # Same offsetgroup for stacking
                ),
                row=1, col=1,
                secondary_y=False
            )
            cumsum += np.array(values)  # Update cumulative sum

        # Add expenses as separate bar
        fig.add_trace(
            go.Bar(
                x=years,
                y=total_expenses,
                name="Total Expenses",
                marker_color='#E74C3C',
                offsetgroup=1  # Different offsetgroup to prevent stacking with income
            ),
            row=1, col=1,
            secondary_y=False
        )

        # Add net cash flow line
        fig.add_trace(
            go.Scatter(
                x=years,
                y=cash_flow,
                name="Net Cash Flow",
                line=dict(color='#2E86C1', width=2)
            ),
            row=1, col=1,
            secondary_y=True
        )

        # Add pie chart for latest year expenses
        latest_year_expenses = {}
        for category, values in expenses.items():
            if values[-1] > 0:  # Only include non-zero expenses
                latest_year_expenses[category] = values[-1]

        # Sort expenses by value for better visualization
        sorted_expenses = dict(sorted(latest_year_expenses.items(), key=lambda x: x[1], reverse=True))

        fig.add_trace(
            go.Pie(
                labels=list(sorted_expenses.keys()),
                values=list(sorted_expenses.values()),
                textinfo='percent+label',
                hole=0.3,
                marker=dict(colors=['#E74C3C', '#C0392B', '#CD6155', '#EC7063', '#F1948A', '#F5B7B1'])
            ),
            row=1, col=2
        )

        # Update layout
        fig.update_layout(
            height=600,  # Increase height to accommodate both charts
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

        # Update axes
        fig.update_yaxes(title_text="Amount ($)", secondary_y=False, row=1, col=1)
        fig.update_yaxes(title_text="Net Cash Flow ($)", secondary_y=True, row=1, col=1)
        fig.update_xaxes(title_text="Year", row=1, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Create and display tables for income and expenses
        df_income = pd.DataFrame({
            'Year': years,
            'Total Income': ['${:,.0f}'.format(x) for x in income],
            'Total Expenses': ['${:,.0f}'.format(x) for x in total_expenses],
            'Net Cash Flow': ['${:,.0f}'.format(x) for x in cash_flow],
        })

        # Add individual income streams
        for stream_name, values in income_streams.items():
            df_income[stream_name] = ['${:,.0f}'.format(x) for x in values]

        st.subheader("Income and Cash Flow Details")
        st.dataframe(df_income, use_container_width=True)

        # Create and display expenses breakdown
        expense_data = {'Year': years}
        for category, values in expenses.items():
            expense_data[category] = ['${:,.0f}'.format(x) for x in values]

        df_expenses = pd.DataFrame(expense_data)
        st.subheader("Expense Breakdown")
        st.dataframe(df_expenses, use_container_width=True)

    @staticmethod
    def plot_assets_liabilities(years: List[int], assets: List[float], 
                              liabilities: List[float], asset_breakdown: Dict[str, List[float]] = None,
                              liability_breakdown: Dict[str, List[float]] = None) -> None:
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

        # Create and display assets breakdown table
        if asset_breakdown:
            asset_data = {'Year': years}
            for category, values in asset_breakdown.items():
                asset_data[category] = ['${:,.0f}'.format(x) for x in values]
            df_assets = pd.DataFrame(asset_data)
            st.subheader("Assets Breakdown")
            st.dataframe(df_assets, use_container_width=True)

        # Create and display liabilities breakdown table
        if liability_breakdown:
            liability_data = {'Year': years}
            for category, values in liability_breakdown.items():
                liability_data[category] = ['${:,.0f}'.format(x) for x in values]
            df_liabilities = pd.DataFrame(liability_data)
            st.subheader("Liabilities Breakdown")
            st.dataframe(df_liabilities, use_container_width=True)

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

        # Create and display home value breakdown table
        df_home = pd.DataFrame({
            'Year': years,
            'Home Value': ['${:,.0f}'.format(x) for x in home_value],
            'Mortgage Balance': ['${:,.0f}'.format(x) for x in mortgage_balance],
            'Home Equity': ['${:,.0f}'.format(x) for x in equity],
        })
        st.dataframe(df_home, use_container_width=True)

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

        # Create and display salary data table
        st.dataframe(salary_data.style.format("${:,.0f}"), use_container_width=True)
    
    def plot_career_roadmap(self, career_data: Dict) -> None:
        """
        Create an interactive visualization of the career roadmap.

        Args:
            career_data: Dictionary containing career path information
        """
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Process primary path
        primary_path = career_data.get('primary_path', {})
        timeline = primary_path.get('timeline', [])

        years = [milestone['year'] for milestone in timeline]
        milestones = [milestone['milestone'] for milestone in timeline]
        salaries = [milestone['estimated_salary'] for milestone in timeline]

        # Add primary path as a line with list for y-values
        fig.add_trace(
            go.Scatter(
                x=years,
                y=list(range(len(years))),  # Convert range to list
                text=milestones,
                mode='lines+markers+text',
                name=primary_path.get('title', 'Primary Path'),
                line=dict(color='#2E86C1', width=3),
                textposition="top center"
            )
        )

        # Add alternative paths
        alt_paths = career_data.get('alternative_paths', [])
        colors = ['#27AE60', '#E67E22', '#8E44AD']  # Different colors for alternative paths

        for idx, path in enumerate(alt_paths):
            if 'timeline' in path:
                alt_years = [milestone['year'] for milestone in path['timeline']]
                alt_milestones = [milestone['milestone'] for milestone in path['timeline']]

                # Create y-values as a list with proper spacing
                y_values = [i + (idx + 1) * 2 for i in range(len(alt_years))]

                fig.add_trace(
                    go.Scatter(
                        x=alt_years,
                        y=y_values,  # Use calculated list
                        text=alt_milestones,
                        mode='lines+markers+text',
                        name=path.get('title', f'Alternative Path {idx + 1}'),
                        line=dict(color=colors[idx % len(colors)], width=2, dash='dash'),
                        textposition="bottom center"
                    )
                )

        # Update layout
        fig.update_layout(
            title='Career Path Roadmap',
            xaxis_title='Year',
            showlegend=True,
            height=600,
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )

        # Remove y-axis labels since we're using relative positioning
        fig.update_yaxes(showticklabels=False)

        st.plotly_chart(fig, use_container_width=True)

        # Display additional information
        st.subheader("Primary Career Path Details")
        st.write(primary_path.get('description', ''))

        # Create a table with timeline details
        df_timeline = pd.DataFrame(timeline)
        if not df_timeline.empty:
            st.dataframe(df_timeline, use_container_width=True)

        # Display alternative paths
        if alt_paths:
            st.subheader("Alternative Career Paths")
            for path in alt_paths:
                st.write(f"**{path.get('title', 'Alternative Path')}**")
                st.write(path.get('description', ''))