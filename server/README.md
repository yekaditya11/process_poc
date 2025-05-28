# AI Safety Summarizer

An AI-powered system that connects to your safety management databases and provides intelligent summaries for:
- **Permit to Work** (ProcessSafety DB)
- **Incident Management** (SafetyConnect DB)
- **Action Tracking** (SafetyConnect DB)
- **Inspection Tracking** (SafetyConnect DB)

## Features

### 🤖 AI-Powered Summarization
- Uses OpenAI GPT-4 for intelligent analysis
- Generates executive summaries and detailed insights
- Provides actionable recommendations
- Identifies trends and patterns across modules

### 📊 Comprehensive Data Analysis
- **Permit to Work**: Completion rates, overdue permits, template performance
- **Incident Management**: Incident trends, critical incidents, response effectiveness
- **Action Tracking**: Action completion, priority analysis, owner performance
- **Inspection Tracking**: Inspection compliance, overdue inspections, frequency analysis

### 🔗 Database Integration
- Connects to both ProcessSafety and SafetyConnect databases
- Real-time data extraction and analysis
- Supports customer-specific filtering
- Configurable time periods for analysis

### 🌐 Multiple Interfaces
- **Command Line Interface**: For batch processing and automation
- **REST API**: For integration with existing systems
- **Web Dashboard**: For real-time monitoring

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL databases (ProcessSafety and SafetyConnect)
- OpenAI API key

### Setup

1. **Clone or download the project**
```bash
cd ai_summarizer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials and OpenAI API key
```

4. **Set up environment variables in .env file:**
```env
# Database Configuration for ProcessSafety
PROCESS_SAFETY_DB_HOST=your_host
PROCESS_SAFETY_DB_PORT=5432
PROCESS_SAFETY_DB_NAME=processsafety
PROCESS_SAFETY_DB_USER=your_username
PROCESS_SAFETY_DB_PASSWORD=your_password

# Database Configuration for SafetyConnect
SAFETY_CONNECT_DB_HOST=your_host
SAFETY_CONNECT_DB_PORT=5432
SAFETY_CONNECT_DB_NAME=safetyconnect
SAFETY_CONNECT_DB_USER=your_username
SAFETY_CONNECT_DB_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Command Line Interface

#### Generate Comprehensive Summary
```bash
python main_app.py --days-back 30 --output summary.json
```

#### Generate Module-Specific Summary
```bash
# Permit to Work summary
python main_app.py --module permit --days-back 30

# Incident Management summary
python main_app.py --module incident --days-back 30

# Action Tracking summary
python main_app.py --module action --days-back 30

# Inspection Tracking summary
python main_app.py --module inspection --days-back 30
```

#### Filter by Customer
```bash
python main_app.py --customer-id "customer-uuid" --days-back 30
```

#### Quick Dashboard Data
```bash
python main_app.py --dashboard --customer-id "customer-uuid"
```

### Web API

#### Start the API Server
```bash
cd api
python web_api.py
```

The API will be available at `http://localhost:8000`

#### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

#### Key API Endpoints

**Comprehensive Summary**
```bash
POST /summary/comprehensive
{
  "customer_id": "optional-customer-id",
  "days_back": 30,
  "include_raw_data": false
}
```

**Module-Specific Summaries**
```bash
GET /summary/permit?customer_id=uuid&days_back=30
GET /summary/incident?customer_id=uuid&days_back=30
GET /summary/action?customer_id=uuid&days_back=30
GET /summary/inspection?customer_id=uuid&days_back=30
```

**Dashboard Data**
```bash
GET /dashboard?customer_id=uuid
```

**KPI Metrics**
```bash
GET /metrics/kpi?customer_id=uuid&days_back=30
```

## Project Structure

```
ai_summarizer/
├── config/
│   └── database_config.py          # Database connection configuration
├── data_extractors/
│   ├── permit_to_work_extractor.py # Permit to work data extraction
│   ├── incident_management_extractor.py # Incident data extraction
│   ├── action_tracking_extractor.py # Action tracking data extraction
│   └── inspection_tracking_extractor.py # Inspection data extraction
├── ai_engine/
│   └── summarization_engine.py     # AI summarization logic
├── api/
│   └── web_api.py                  # REST API endpoints
├── main_app.py                     # Main application orchestrator
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## Database Schema Requirements

The system expects the following key tables:

### ProcessSafety Database
- `ProcessSafetyAssignments`
- `ProcessSafetySchedules`
- `ProcessSafetyTemplatesCollections`
- `ProcessSafetyHistories`
- `SafetyPerformanceIndicators`
- `Users`, `UserProfiles`, `Customers`

### SafetyConnect Database
- `Incidents`
- `ActionTrackings`
- `InspectionTrackings`
- `InspectionAssignments`
- `ChecklistAnswers`, `ChecklistQuestions`, `CheckLists`
- `Users`, `UserProfiles`, `Customers`

## Sample Output

### Executive Summary Example
```json
{
  "summary_info": {
    "generated_at": "2024-01-15T10:30:00Z",
    "customer_id": "customer-123",
    "analysis_period_days": 30
  },
  "ai_summary": {
    "executive_summary": "Overall safety performance shows strong compliance with 94% permit completion rate. However, incident response times need improvement with average 3.2 days to action assignment...",
    "module_summaries": {
      "permit_to_work": "Permit system performing well with high completion rates...",
      "incident_management": "Incident trends show decrease in near-miss reporting...",
      "action_tracking": "Action completion rates improved by 15% this month...",
      "inspection_tracking": "Inspection compliance at 89%, with overdue items concentrated in..."
    },
    "insights_and_recommendations": "Cross-module analysis reveals correlation between permit delays and subsequent incidents...",
    "alerts_and_priorities": [
      {
        "priority": "critical",
        "category": "action",
        "title": "15 High-Priority Actions Overdue",
        "description": "Critical safety actions are overdue by average 12 days",
        "recommended_action": "Immediate escalation to management",
        "deadline": "2024-01-16"
      }
    ]
  }
}
```

## Customization

### Adding New Data Sources
1. Create a new extractor in `data_extractors/`
2. Follow the pattern of existing extractors
3. Update `main_app.py` to include the new extractor
4. Add corresponding AI summarization logic

### Modifying AI Prompts
Edit the prompt templates in `ai_engine/summarization_engine.py` to customize the AI analysis focus.

### Adding New API Endpoints
Extend `api/web_api.py` with additional endpoints as needed.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in `.env`
   - Ensure databases are accessible from your network
   - Check firewall settings

2. **OpenAI API Errors**
   - Verify API key is correct
   - Check API usage limits
   - Ensure sufficient credits

3. **Memory Issues with Large Datasets**
   - Reduce `days_back` parameter
   - Implement data pagination for large customers

### Logging
Logs are written to `ai_summarizer.log` and console. Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Security Considerations

- Store database credentials securely
- Use environment variables for sensitive data
- Implement proper authentication for API endpoints
- Consider data encryption for sensitive summaries
- Regularly rotate API keys

## Performance Optimization

- Use database connection pooling for high-volume usage
- Implement caching for frequently requested summaries
- Consider async processing for large datasets
- Monitor OpenAI API usage and costs

## Support

For issues and questions:
1. Check the logs for error details
2. Verify database connectivity
3. Test with smaller datasets first
4. Review API documentation at `/docs` endpoint
