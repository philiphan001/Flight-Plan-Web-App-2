import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict
import pandas as pd
import numpy as np

class FinancialPlotter:
    @staticmethod
    def _create_animation_frames(data: List[float], x_vals: List[int], name: str, color: str) -> List[go.Frame]:
        """Helper method to create animation frames for growing bars"""
        frames = []
        for i in range(10):  # 10 frames for smooth animation
            frame_data = [val * (i + 1) / 10 for val in data]
            frames.append(
                go.Frame(
                    data=[go.Bar(x=x_vals, y=frame_data, name=name, marker_color=color)],
                    name=f"frame{i}"
                )
            )
        return frames

    @staticmethod
    def plot_net_worth(years: List[int], net_worth: List[float], 
                      assets: List[float], liabilities: List[float],
                      savings: List[float] = None) -> None:
        # Create the plot with initial zero values
        fig = go.Figure()

        # Add initial bars with zero height
        fig.add_trace(go.Bar(x=years, y=[0] * len(assets),
                           name='Assets',
                           marker_color='#27AE60'))

        fig.add_trace(go.Bar(x=years, y=[0] * len(liabilities),
                           name='Liabilities',
                           marker_color='#E74C3C'))

        # Add net worth line with initial zero values
        fig.add_trace(go.Scatter(x=years, y=[0] * len(net_worth),
                               mode='lines+markers',
                               name='Net Worth',
                               line=dict(color='#2E86C1', width=2)))

        # Create animation frames
        frames = []
        frames.extend(FinancialPlotter._create_animation_frames(assets, years, 'Assets', '#27AE60'))
        frames.extend(FinancialPlotter._create_animation_frames([-x for x in liabilities], years, 'Liabilities', '#E74C3C'))

        # Add frames for net worth line
        for i in range(10):
            frame_data = [val * (i + 1) / 10 for val in net_worth]
            frames.append(
                go.Frame(
                    data=[
                        go.Bar(x=years, y=[val * (i + 1) / 10 for val in assets], name='Assets', marker_color='#27AE60'),
                        go.Bar(x=years, y=[-val * (i + 1) / 10 for val in liabilities], name='Liabilities', marker_color='#E74C3C'),
                        go.Scatter(x=years, y=frame_data, mode='lines+markers', name='Net Worth', line=dict(color='#2E86C1', width=2))
                    ],
                    name=f"frame{i+20}"
                )
            )

        # Update layout with animation settings
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
            ),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                }]
            }],
            frames=frames
        )

        # Auto-play animation using Streamlit's javascript injection
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <script>
                const frame = document.querySelector('iframe');
                frame.contentWindow.document.querySelector('button[data-title="Play"]').click();
            </script>
            """,
            unsafe_allow_html=True
        )

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
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Create cumulative sums for income stacking
        cumsum = np.zeros(len(years))
        colors = {'Primary Income': '#27AE60', 'Spouse Income': '#2ECC71', 'Part-Time Work': '#82E0AA'}

        # Add initial bars with zero height
        for income_type, values in income_streams.items():
            fig.add_trace(
                go.Bar(
                    x=years,
                    y=[0] * len(values),
                    name=income_type,
                    marker_color=colors.get(income_type, '#27AE60'),
                    base=cumsum,  # Start from previous cumulative sum
                    offsetgroup=0  # Same offsetgroup for stacking
                ),
                secondary_y=False
            )
            cumsum += np.array(values)  # Update cumulative sum
        fig.add_trace(
            go.Bar(
                x=years,
                y=[0] * len(total_expenses),
                name="Total Expenses",
                marker_color='#E74C3C',
                offsetgroup=1  # Different offsetgroup to prevent stacking with income
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=years,
                y=[0] * len(cash_flow),
                name="Net Cash Flow",
                line=dict(color='#2E86C1', width=2)
            ),
            secondary_y=True
        )

        frames = []
        for income_type, values in income_streams.items():
            frames.extend(FinancialPlotter._create_animation_frames(values, years, income_type, colors.get(income_type, '#27AE60')))
        frames.extend(FinancialPlotter._create_animation_frames(total_expenses, years, "Total Expenses", '#E74C3C'))
        for i in range(10):
            frame_data = [val * (i + 1) / 10 for val in cash_flow]
            frames.append(
                go.Frame(
                    data=[
                        go.Bar(x=years, y=[val * (i + 1) / 10 for val in income], name='Total Income', marker_color='#27AE60'),
                        go.Bar(x=years, y=[val * (i + 1) / 10 for val in total_expenses], name='Total Expenses', marker_color='#E74C3C'),
                        go.Scatter(x=years, y=frame_data, mode='lines+markers', name='Net Cash Flow', line=dict(color='#2E86C1', width=2))
                    ],
                    name=f"frame{i + len(frames)}"
                )
            )


        fig.update_layout(
            title='Income, Expenses, and Cash Flow Projection',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='group',  # Group bars by offsetgroup
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            bargap=0.15,
            bargroupgap=0.1,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                }]
            }],
            frames=frames
        )
        fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
        fig.update_yaxes(title_text="Net Cash Flow ($)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <script>
                const frame = document.querySelector('iframe');
                frame.contentWindow.document.querySelector('button[data-title="Play"]').click();
            </script>
            """,
            unsafe_allow_html=True
        )

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
        fig.add_trace(go.Scatter(x=years, y=[0] * len(assets),
                               mode='lines+markers',
                               name='Assets',
                               line=dict(color='#27AE60', width=2)))
        fig.add_trace(go.Scatter(x=years, y=[0] * len(liabilities),
                               mode='lines+markers',
                               name='Liabilities',
                               line=dict(color='#E74C3C', width=2)))

        frames = []
        frames.extend(FinancialPlotter._create_animation_frames(assets, years, 'Assets', '#27AE60'))
        frames.extend(FinancialPlotter._create_animation_frames(liabilities, years, 'Liabilities', '#E74C3C'))
        for i in range(10):
            frame_data_assets = [val * (i + 1) / 10 for val in assets]
            frame_data_liabilities = [val * (i + 1) / 10 for val in liabilities]
            frames.append(
                go.Frame(
                    data=[
                        go.Scatter(x=years, y=frame_data_assets, mode='lines+markers', name='Assets', line=dict(color='#27AE60', width=2)),
                        go.Scatter(x=years, y=frame_data_liabilities, mode='lines+markers', name='Liabilities', line=dict(color='#E74C3C', width=2))
                    ],
                    name=f"frame{i + len(frames)}"
                )
            )
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
            ),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                }]
            }],
            frames=frames
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <script>
                const frame = document.querySelector('iframe');
                frame.contentWindow.document.querySelector('button[data-title="Play"]').click();
            </script>
            """,
            unsafe_allow_html=True
        )


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

        # Add initial bars with zero height
        fig.add_trace(go.Bar(
            x=years,
            y=[0] * len(home_value),
            name='Home Value',
            marker_color='#27AE60',
            offsetgroup='value'
        ))

        fig.add_trace(go.Bar(
            x=years,
            y=[0] * len(mortgage_balance),
            name='Mortgage Balance',
            marker_color='#E74C3C',
            offsetgroup='mortgage'
        ))

        fig.add_trace(go.Bar(
            x=years,
            y=[0] * len(equity),
            name='Home Equity',
            marker_color='#2E86C1',
            offsetgroup='equity'
        ))

        frames = []
        frames.extend(FinancialPlotter._create_animation_frames(home_value, years, 'Home Value', '#27AE60'))
        frames.extend(FinancialPlotter._create_animation_frames(mortgage_balance, years, 'Mortgage Balance', '#E74C3C'))
        frames.extend(FinancialPlotter._create_animation_frames(equity, years, 'Home Equity', '#2E86C1'))


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
            bargroupgap=0.1,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                }]
            }],
            frames=frames
        )
        st.plotly_chart(fig)
        st.markdown(
            """
            <script>
                const frame = document.querySelector('iframe');
                frame.contentWindow.document.querySelector('button[data-title="Play"]').click();
            </script>
            """,
            unsafe_allow_html=True
        )

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
    
    @staticmethod
    def plot_career_roadmap(career_data: Dict) -> None:
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
                y=[0] * len(years),
                text=milestones,
                mode='lines+markers+text',
                name=primary_path.get('title', 'Primary Path'),
                line=dict(color='#2E86C1', width=3),
                textposition="top center"
            )
        )
        frames = []
        for i in range(10):
            frame_data = [val * (i+1)/10 for val in salaries]
            frames.append(
                go.Frame(
                    data=[go.Scatter(x=years, y=[val * (i+1)/10 for val in range(len(years))], text=milestones, mode='lines+markers+text', name=primary_path.get('title', 'Primary Path'), line=dict(color='#2E86C1', width=3), textposition="top center")],
                    name=f"frame{i + len(frames)}"
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
                        y=[0] * len(alt_years),
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
            ),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                }]
            }],
            frames=frames
        )

        # Remove y-axis labels since we're using relative positioning
        fig.update_yaxes(showticklabels=False)

        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <script>
                const frame = document.querySelector('iframe');
                frame.contentWindow.document.querySelector('button[data-title="Play"]').click();
            </script>
            """,
            unsafe_allow_html=True
        )

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