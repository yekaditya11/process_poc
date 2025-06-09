"""
ECharts Chart Generator
Generates interactive Apache ECharts configurations for the conversational AI
Version: 2024-12-07 - Enhanced interactivity with zoom, brush, and animations
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EChartsGenerator:
    """Generate interactive ECharts configurations for various chart types"""
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def generate_chart(self, chart_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate ECharts configuration from chart data
        
        Args:
            chart_data: Dictionary containing chart type, title, and data
            
        Returns:
            Dictionary with ECharts configuration or None if error
        """
        if not chart_data:
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
            logger.error(f"Error generating ECharts chart: {str(e)}")
            return None
    
    def _create_bar_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create interactive bar chart configuration"""
        try:
            # Extract data
            categories = [item.get('name', item.get('label', f'Item {i}')) for i, item in enumerate(data)]
            values = [item.get('value', item.get('y', 0)) for item in data]
            
            config = {
                'title': {
                    'text': title,
                    'left': 'center',
                    'textStyle': {
                        'color': '#092f57',
                        'fontSize': 16,
                        'fontWeight': 'bold'
                    }
                },
                'tooltip': {
                    'trigger': 'axis',
                    'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                    'borderColor': '#ddd',
                    'borderWidth': 1,
                    'textStyle': {
                        'color': '#333'
                    },
                    'axisPointer': {
                        'type': 'shadow'
                    }
                },
                'grid': {
                    'left': '3%',
                    'right': '4%',
                    'bottom': '15%',
                    'containLabel': True
                },
                'xAxis': {
                    'type': 'category',
                    'data': categories,
                    'axisLabel': {
                        'color': '#666',
                        'rotate': 45 if len(categories) > 6 else 0,
                        'interval': 0
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    }
                },
                'yAxis': {
                    'type': 'value',
                    'axisLabel': {
                        'color': '#666'
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'color': '#f0f0f0'
                        }
                    }
                },
                'series': [{
                    'type': 'bar',
                    'data': [
                        {
                            'value': value,
                            'itemStyle': {
                                'color': data[i].get('color', self.color_palette[i % len(self.color_palette)])
                            }
                        } for i, value in enumerate(values)
                    ],
                    'emphasis': {
                        'itemStyle': {
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    'animationDelay': 100
                }],
                'dataZoom': [
                    {
                        'type': 'inside',
                        'start': 0,
                        'end': 100
                    },
                    {
                        'start': 0,
                        'end': 100,
                        'height': 30,
                        'bottom': 50
                    }
                ],
                'animation': True,
                'animationDuration': 1000,
                'animationEasing': 'cubicOut'
            }
            
            return {
                'type': 'echarts',
                'echarts_config': config,
                'title': title,
                'chart_type': 'bar'
            }
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return None
    
    def _create_pie_chart(self, title: str, data: List[Dict], donut: bool = False) -> Dict[str, Any]:
        """Create interactive pie/donut chart configuration"""
        try:
            # Prepare data
            pie_data = []
            for i, item in enumerate(data):
                pie_data.append({
                    'name': item.get('name', item.get('label', f'Item {i}')),
                    'value': item.get('value', item.get('y', 0)),
                    'itemStyle': {
                        'color': item.get('color', self.color_palette[i % len(self.color_palette)])
                    }
                })
            
            config = {
                'title': {
                    'text': title,
                    'left': 'center',
                    'textStyle': {
                        'color': '#092f57',
                        'fontSize': 16,
                        'fontWeight': 'bold'
                    }
                },
                'tooltip': {
                    'trigger': 'item',
                    'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                    'borderColor': '#ddd',
                    'borderWidth': 1,
                    'textStyle': {
                        'color': '#333'
                    },
                    'formatter': '{b}: {c} ({d}%)'
                },
                'legend': {
                    'orient': 'horizontal',
                    'bottom': 10,
                    'textStyle': {
                        'color': '#666'
                    }
                },
                'series': [{
                    'type': 'pie',
                    'radius': ['40%', '70%'] if donut else '70%',
                    'center': ['50%', '50%'],
                    'data': pie_data,
                    'emphasis': {
                        'itemStyle': {
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    'label': {
                        'show': True,
                        'formatter': '{b}: {c} ({d}%)',
                        'color': '#333'
                    },
                    'animationType': 'scale',
                    'animationEasing': 'elasticOut'
                }],
                'animation': True,
                'animationDuration': 1000
            }
            
            return {
                'type': 'echarts',
                'echarts_config': config,
                'title': title,
                'chart_type': 'donut' if donut else 'pie'
            }
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {str(e)}")
            return None
    
    def _create_line_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create interactive line chart configuration"""
        try:
            # Extract data
            categories = [item.get('name', item.get('label', f'Point {i}')) for i, item in enumerate(data)]
            values = [item.get('value', item.get('y', 0)) for item in data]
            
            config = {
                'title': {
                    'text': title,
                    'left': 'center',
                    'textStyle': {
                        'color': '#092f57',
                        'fontSize': 16,
                        'fontWeight': 'bold'
                    }
                },
                'tooltip': {
                    'trigger': 'axis',
                    'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                    'borderColor': '#ddd',
                    'borderWidth': 1,
                    'textStyle': {
                        'color': '#333'
                    }
                },
                'grid': {
                    'left': '3%',
                    'right': '4%',
                    'bottom': '15%',
                    'containLabel': True
                },
                'xAxis': {
                    'type': 'category',
                    'data': categories,
                    'axisLabel': {
                        'color': '#666'
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    }
                },
                'yAxis': {
                    'type': 'value',
                    'axisLabel': {
                        'color': '#666'
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'color': '#f0f0f0'
                        }
                    }
                },
                'series': [{
                    'type': 'line',
                    'data': values,
                    'smooth': True,
                    'lineStyle': {
                        'color': '#1976d2',
                        'width': 3
                    },
                    'itemStyle': {
                        'color': '#1976d2'
                    },
                    'areaStyle': {
                        'color': {
                            'type': 'linear',
                            'x': 0,
                            'y': 0,
                            'x2': 0,
                            'y2': 1,
                            'colorStops': [
                                {'offset': 0, 'color': 'rgba(25, 118, 210, 0.3)'},
                                {'offset': 1, 'color': 'rgba(25, 118, 210, 0.05)'}
                            ]
                        }
                    },
                    'emphasis': {
                        'focus': 'series'
                    }
                }],
                'dataZoom': [
                    {
                        'type': 'inside',
                        'start': 0,
                        'end': 100
                    }
                ],
                'animation': True,
                'animationDuration': 1000,
                'animationEasing': 'cubicOut'
            }
            
            return {
                'type': 'echarts',
                'echarts_config': config,
                'title': title,
                'chart_type': 'line'
            }
            
        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            return None
    
    def _create_scatter_chart(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create interactive scatter chart configuration"""
        try:
            # Prepare scatter data
            scatter_data = []
            for i, item in enumerate(data):
                x_val = item.get('x', i)
                y_val = item.get('value', item.get('y', 0))
                scatter_data.append([x_val, y_val])
            
            config = {
                'title': {
                    'text': title,
                    'left': 'center',
                    'textStyle': {
                        'color': '#092f57',
                        'fontSize': 16,
                        'fontWeight': 'bold'
                    }
                },
                'tooltip': {
                    'trigger': 'item',
                    'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                    'borderColor': '#ddd',
                    'borderWidth': 1,
                    'textStyle': {
                        'color': '#333'
                    },
                    'formatter': 'X: {c[0]}<br/>Y: {c[1]}'
                },
                'grid': {
                    'left': '3%',
                    'right': '4%',
                    'bottom': '15%',
                    'containLabel': True
                },
                'xAxis': {
                    'type': 'value',
                    'axisLabel': {
                        'color': '#666'
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'color': '#f0f0f0'
                        }
                    }
                },
                'yAxis': {
                    'type': 'value',
                    'axisLabel': {
                        'color': '#666'
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#ddd'
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'color': '#f0f0f0'
                        }
                    }
                },
                'series': [{
                    'type': 'scatter',
                    'data': scatter_data,
                    'symbolSize': 10,
                    'itemStyle': {
                        'color': '#1976d2'
                    },
                    'emphasis': {
                        'itemStyle': {
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }],
                'brush': {
                    'toolbox': ['rect', 'polygon', 'clear'],
                    'xAxisIndex': 0
                },
                'animation': True,
                'animationDuration': 1000,
                'animationEasing': 'cubicOut'
            }
            
            return {
                'type': 'echarts',
                'echarts_config': config,
                'title': title,
                'chart_type': 'scatter'
            }
            
        except Exception as e:
            logger.error(f"Error creating scatter chart: {str(e)}")
            return None
    
    def _create_heatmap(self, title: str, data: List[Dict]) -> Dict[str, Any]:
        """Create interactive heatmap configuration"""
        try:
            # This is a placeholder for heatmap implementation
            # Convert to bar chart for now
            return self._create_bar_chart(title, data)
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            return None
