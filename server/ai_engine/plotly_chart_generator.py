"""
Plotly Chart Generator for SafetyConnect AI
Generates interactive Plotly charts with colors and configurations
Updated to work with latest SafetyConnect data structure
"""

import json
import logging
from typing import Dict, Any, List, Optional

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.utils import PlotlyJSONEncoder
    PLOTLY_AVAILABLE = True
    print("✅ Plotly modules imported successfully")
except ImportError as e:
    PLOTLY_AVAILABLE = False
    print(f"❌ Plotly import failed: {e}")
    # Create dummy classes to prevent errors
    class DummyPlotly:
        pass
    go = DummyPlotly()
    px = DummyPlotly()
    PlotlyJSONEncoder = None

logger = logging.getLogger(__name__)

class PlotlyChartGenerator:
    """Generates Plotly charts with color schemes and interactive features"""

    # SafetyConnect color palette
    SAFETY_COLORS = [
        '#092f57',  # Primary blue
        '#2e7d32',  # Success green
        '#d32f2f',  # Danger red
        '#ff9800',  # Warning orange
        '#1976d2',  # Info blue
        '#9c27b0',  # Purple
        '#795548',  # Brown
        '#607d8b',  # Blue grey
    ]

    def __init__(self):
        self.color_palette = self.SAFETY_COLORS
        self.plotly_available = PLOTLY_AVAILABLE
        if not self.plotly_available:
            logger.warning("Plotly not available - chart generation will be disabled")
    
    def generate_chart_config(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Plotly chart configuration from chart data

        Args:
            chart_data: Dictionary containing chart type, title, data, etc.

        Returns:
            Plotly configuration dictionary ready for frontend
        """
        if not self.plotly_available:
            logger.warning("Plotly not available - cannot generate chart")
            return None

        try:
            chart_type = chart_data.get('type', 'bar').lower()
            title = chart_data.get('title', 'Chart')
            data = chart_data.get('data', [])

            if not data:
                return None
                
            # Generate chart based on type
            if chart_type == 'bar':
                return self._create_bar_chart(title, data)
            elif chart_type in ['pie', 'donut']:
                return self._create_pie_chart(title, data, donut=(chart_type == 'donut'))
            elif chart_type == 'line':
                return self._create_line_chart(title, data)
            elif chart_type == 'scatter':
                return self._create_scatter_chart(title, data)
            elif chart_type == 'heatmap':
                return self._create_heatmap(title, data)
            else:
                # Default to bar chart
                return self._create_bar_chart(title, data)
                
        except Exception as e:
            logger.error(f"Error generating Plotly chart: {str(e)}")
            return None

    def generate_safety_dashboard_chart(self, module_name: str, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate charts specifically for SafetyConnect dashboard modules"""
        try:
            if module_name == 'incidents':
                return self._create_incident_dashboard_chart(module_data)
            elif module_name == 'actions':
                return self._create_action_dashboard_chart(module_data)
            elif module_name == 'driver_safety':
                return self._create_driver_safety_dashboard_chart(module_data)
            elif module_name == 'observations':
                return self._create_observation_dashboard_chart(module_data)
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating {module_name} dashboard chart: {str(e)}")
            return None

    def _create_incident_dashboard_chart(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident-specific dashboard chart"""
        try:
            # Try to find incident types data
            if 'incident_types' in incident_data and incident_data['incident_types']:
                incident_types = incident_data['incident_types']
                data = []
                for incident_type, count in incident_types.items():
                    if isinstance(count, (int, float)) and count > 0:
                        data.append({'label': incident_type.replace('_', ' ').title(), 'value': count})

                if data:
                    return self._create_pie_chart('Incident Types Distribution', data, donut=True)

            # Fallback: create a simple bar chart with available numeric data
            data = []
            for key, value in incident_data.items():
                if isinstance(value, (int, float)) and value > 0:
                    data.append({'label': key.replace('_', ' ').title(), 'value': value})

            if data:
                return self._create_bar_chart('Incident Metrics', data)

            return None
        except Exception as e:
            logger.error(f"Error creating incident chart: {str(e)}")
            return None

    def _create_action_dashboard_chart(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create action-specific dashboard chart"""
        try:
            # Look for action status data
            data = []

            # Check for open/closed actions
            if 'open_actions' in action_data and 'closed_actions' in action_data:
                open_count = action_data.get('open_actions', 0)
                closed_count = action_data.get('closed_actions', 0)

                if open_count > 0 or closed_count > 0:
                    data = [
                        {'label': 'Open Actions', 'value': open_count},
                        {'label': 'Closed Actions', 'value': closed_count}
                    ]
                    return self._create_pie_chart('Action Status Distribution', data)

            # Fallback: create chart with available numeric data
            for key, value in action_data.items():
                if isinstance(value, (int, float)) and value > 0:
                    data.append({'label': key.replace('_', ' ').title(), 'value': value})

            if data:
                return self._create_bar_chart('Action Metrics', data)

            return None
        except Exception as e:
            logger.error(f"Error creating action chart: {str(e)}")
            return None

    def _create_driver_safety_dashboard_chart(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create driver safety-specific dashboard chart"""
        try:
            data = []

            # Look for completion data
            if 'daily_completions' in driver_data:
                daily = driver_data['daily_completions']
                if isinstance(daily, dict) and 'total_completed' in daily:
                    data.append({'label': 'Daily Completions', 'value': daily['total_completed']})

            if 'weekly_completions' in driver_data:
                weekly = driver_data['weekly_completions']
                if isinstance(weekly, dict) and 'total_completed' in weekly:
                    data.append({'label': 'Weekly Completions', 'value': weekly['total_completed']})

            # Look for vehicle fitness data
            if 'vehicles_deemed_unfit' in driver_data:
                unfit = driver_data['vehicles_deemed_unfit']
                if isinstance(unfit, dict) and 'total_unfit_vehicles' in unfit:
                    data.append({'label': 'Unfit Vehicles', 'value': unfit['total_unfit_vehicles']})

            if data:
                return self._create_bar_chart('Driver Safety Metrics', data)

            return None
        except Exception as e:
            logger.error(f"Error creating driver safety chart: {str(e)}")
            return None

    def _create_observation_dashboard_chart(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create observation-specific dashboard chart"""
        try:
            # Look for observations by area
            if 'observations_by_area' in observation_data:
                area_data = observation_data['observations_by_area']
                if isinstance(area_data, dict):
                    data = []
                    for area, count in area_data.items():
                        if isinstance(count, (int, float)) and count > 0 and area != 'total_observations':
                            data.append({'label': area.replace('_', ' ').title(), 'value': count})

                    if data:
                        return self._create_pie_chart('Observations by Area', data, donut=True)

            # Look for observation priority
            if 'observation_priority' in observation_data:
                priority_data = observation_data['observation_priority']
                if isinstance(priority_data, dict) and 'observations_by_priority' in priority_data:
                    priorities = priority_data['observations_by_priority']
                    data = []
                    for priority, count in priorities.items():
                        if isinstance(count, (int, float)) and count > 0:
                            data.append({'label': priority, 'value': count})

                    if data:
                        return self._create_bar_chart('Observations by Priority', data)

            return None
        except Exception as e:
            logger.error(f"Error creating observation chart: {str(e)}")
            return None
    
    def _create_bar_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create a colored bar chart"""
        names = [item.get('name', '') for item in data]
        values = [item.get('value', 0) for item in data]
        
        fig = go.Figure(data=[
            go.Bar(
                x=names,
                y=values,
                marker=dict(
                    color=self.color_palette[:len(data)],
                    line=dict(color='rgba(0,0,0,0.1)', width=1)
                ),
                text=values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#092f57')
            ),
            xaxis=dict(
                title='Category',
                tickangle=-45,
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='Value',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=50, r=50, t=80, b=100),
            height=400
        )
        
        return {
            'type': 'plotly',
            'config': json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
            'title': title,
            'chart_type': 'bar'
        }
    
    def _create_pie_chart(self, title: str, data: List[Dict], donut: bool = False) -> Dict[str, Any]:
        """Create a colored pie/donut chart"""
        names = [item.get('name', '') for item in data]
        values = [item.get('value', 0) for item in data]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=names,
                values=values,
                hole=0.4 if donut else 0,
                marker=dict(
                    colors=self.color_palette[:len(data)],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#092f57')
            ),
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        return {
            'type': 'plotly',
            'config': json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
            'title': title,
            'chart_type': 'donut' if donut else 'pie'
        }
    
    def _create_line_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create a colored line chart"""
        names = [item.get('name', '') for item in data]
        values = [item.get('value', 0) for item in data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=names,
                y=values,
                mode='lines+markers',
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(
                    color=self.color_palette[1],
                    size=8,
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#092f57')
            ),
            xaxis=dict(
                title='Category',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='Value',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=400
        )
        
        return {
            'type': 'plotly',
            'config': json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
            'title': title,
            'chart_type': 'line'
        }
    
    def _create_scatter_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create a colored scatter chart"""
        names = [item.get('name', '') for item in data]
        values = [item.get('value', 0) for item in data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=names,
                y=values,
                mode='markers',
                marker=dict(
                    color=self.color_palette[:len(data)],
                    size=12,
                    line=dict(color='white', width=2)
                ),
                text=names,
                hovertemplate='<b>%{text}</b><br>Value: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#092f57')
            ),
            xaxis=dict(
                title='Category',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='Value',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=400
        )
        
        return {
            'type': 'plotly',
            'config': json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
            'title': title,
            'chart_type': 'scatter'
        }
    
    def _create_heatmap(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create a heatmap (for matrix data)"""
        # This is a simplified heatmap - you might need to adapt based on your data structure
        names = [item.get('name', '') for item in data]
        values = [item.get('value', 0) for item in data]
        
        # Create a simple 1D heatmap
        fig = go.Figure(data=go.Heatmap(
            z=[values],
            x=names,
            y=['Value'],
            colorscale='RdYlBu_r',
            hoverongaps=False,
            hovertemplate='<b>%{x}</b><br>Value: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#092f57')
            ),
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=300
        )
        
        return {
            'type': 'plotly',
            'config': json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
            'title': title,
            'chart_type': 'heatmap'
        }
