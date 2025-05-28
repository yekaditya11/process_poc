/**
 * AI Insights Page
 * AI-generated summaries and recommendations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  Chip,
  Alert,
  Skeleton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  ExpandMore,
  Psychology,
  TrendingUp,
  Warning,
  Lightbulb,
  Download,
  Refresh,
  DateRange,
  ExpandLess,
} from '@mui/icons-material';

import DateRangePicker from '../components/DateRangePicker';
import ApiService from '../services/api';

const AIInsights = () => {
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [daysBack, setDaysBack] = useState(30);
  const [selectedModule, setSelectedModule] = useState('comprehensive');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [useCustomDateRange, setUseCustomDateRange] = useState(false);

  const fetchAISummary = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use custom date range if available, otherwise use daysBack
      let effectiveDaysBack = daysBack;
      if (useCustomDateRange && fromDate && toDate) {
        effectiveDaysBack = Math.ceil((new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24)) + 1;
      }

      let response;
      if (selectedModule === 'comprehensive') {
        response = await ApiService.getComprehensiveSummary(null, effectiveDaysBack, false);
      } else {
        response = await ApiService.getModuleSummary(selectedModule, null, effectiveDaysBack);
      }

      setSummaryData(response.data);
    } catch (err) {
      console.error('Error fetching AI summary:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAISummary();
  }, [daysBack, selectedModule, useCustomDateRange, fromDate, toDate]);

  const handleDateRangeChange = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
  };

  const handleDateRangeApply = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
    setUseCustomDateRange(true);
  };

  const handleDateRangeReset = () => {
    setFromDate('');
    setToDate('');
    setUseCustomDateRange(false);
    setDaysBack(30);
  };

  const handleExport = () => {
    if (!summaryData) return;

    const dataStr = JSON.stringify(summaryData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ai-insights-${selectedModule}-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderBulletPoints = (content) => {
    if (!content || typeof content !== 'string') return null;

    // Split content by bullet points and filter out empty lines
    const bulletPoints = content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .filter(line => line.startsWith('•') || line.startsWith('-') || line.startsWith('*'));

    if (bulletPoints.length === 0) {
      // If no bullet points found, display as regular text
      return (
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {content}
        </Typography>
      );
    }

    return (
      <Box component="ul" sx={{ pl: 0, m: 0 }}>
        {bulletPoints.map((point, index) => (
          <Box
            key={index}
            component="li"
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              mb: 1.5,
              listStyle: 'none',
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                mt: 0.75,
                mr: 2,
                flexShrink: 0,
              }}
            />
            <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
              {point.replace(/^[•\-*]\s*/, '')}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  };

  const renderSummarySection = (title, content, icon, severity = 'info') => {
    if (!content) return null;

    return (
      <Card sx={{ mb: 2 }}>
        <CardHeader
          avatar={icon}
          title={title}
          sx={{ pb: 1 }}
        />
        <CardContent sx={{ pt: 0 }}>
          {typeof content === 'string' ? (
            renderBulletPoints(content)
          ) : (
            <Alert severity={severity} sx={{ mt: 1 }}>
              <Typography variant="body2">
                {JSON.stringify(content, null, 2)}
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderLoadingSkeleton = () => (
    <Box>
      {[1, 2, 3, 4].map((item) => (
        <Card key={item} sx={{ mb: 2 }}>
          <CardContent>
            <Skeleton variant="text" width="40%" height={32} />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="80%" />
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  return (
    <Box p={3}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Safety Insights
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          AI-powered analysis and recommendations for safety management
        </Typography>

        {/* Controls */}
        <Box display="flex" gap={2} mt={3} flexWrap="wrap" alignItems="center">
          {!useCustomDateRange && (
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Analysis Period</InputLabel>
              <Select
                value={daysBack}
                label="Analysis Period"
                onChange={(e) => {
                  setDaysBack(e.target.value);
                  setUseCustomDateRange(false);
                }}
              >
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
                <MenuItem value={90}>Last 90 days</MenuItem>
                <MenuItem value={365}>Last year</MenuItem>
              </Select>
            </FormControl>
          )}

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Module</InputLabel>
            <Select
              value={selectedModule}
              label="Module"
              onChange={(e) => setSelectedModule(e.target.value)}
            >
              <MenuItem value="comprehensive">All Modules</MenuItem>
              <MenuItem value="permit">Permit to Work</MenuItem>
              <MenuItem value="incident">Incident Management</MenuItem>
              <MenuItem value="action">Action Tracking</MenuItem>
              <MenuItem value="inspection">Inspection Tracking</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant={showDatePicker ? "contained" : "outlined"}
            startIcon={<DateRange />}
            endIcon={showDatePicker ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setShowDatePicker(!showDatePicker)}
            size="small"
          >
            Custom Date Range
          </Button>

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchAISummary}
            disabled={loading}
          >
            Refresh
          </Button>

          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
            disabled={!summaryData}
          >
            Export
          </Button>
        </Box>

        {/* Date Range Picker */}
        <Collapse in={showDatePicker}>
          <Box mt={2}>
            <DateRangePicker
              fromDate={fromDate}
              toDate={toDate}
              onDateChange={handleDateRangeChange}
              onApply={handleDateRangeApply}
              onReset={handleDateRangeReset}
              disabled={loading}
              showApplyButton={true}
            />
          </Box>
        </Collapse>
      </Box>

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading && renderLoadingSkeleton()}

      {/* AI Summary Content */}
      {!loading && summaryData && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {/* Executive Summary */}
            {summaryData.ai_summary?.executive_summary &&
              renderSummarySection(
                'Executive Summary',
                summaryData.ai_summary.executive_summary,
                <Psychology color="primary" />,
                'info'
              )
            }

            {/* Strategic Insights & Recommendations */}
            {summaryData.ai_summary?.insights_and_recommendations && (
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Lightbulb color="info" />
                    <Typography variant="h6">Strategic Insights & Recommendations</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {renderBulletPoints(summaryData.ai_summary.insights_and_recommendations)}
                </AccordionDetails>
              </Accordion>
            )}

            {/* Module-specific summaries */}
            {summaryData.ai_summary?.module_summaries?.permit_to_work &&
              renderSummarySection(
                'Permit to Work Insights',
                summaryData.ai_summary.module_summaries.permit_to_work,
                <Psychology color="primary" />
              )
            }

            {summaryData.ai_summary?.module_summaries?.incident_management &&
              renderSummarySection(
                'Incident Management Insights',
                summaryData.ai_summary.module_summaries.incident_management,
                <Psychology color="error" />
              )
            }

            {summaryData.ai_summary?.module_summaries?.action_tracking &&
              renderSummarySection(
                'Action Tracking Insights',
                summaryData.ai_summary.module_summaries.action_tracking,
                <Psychology color="warning" />
              )
            }

            {summaryData.ai_summary?.module_summaries?.inspection_tracking &&
              renderSummarySection(
                'Inspection Tracking Insights',
                summaryData.ai_summary.module_summaries.inspection_tracking,
                <Psychology color="success" />
              )
            }

            {/* Alerts and Priorities */}
            {summaryData.ai_summary?.alerts_and_priorities && summaryData.ai_summary.alerts_and_priorities.length > 0 && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Warning color="warning" />
                    <Typography variant="h6">Alerts & Priorities</Typography>
                    <Chip
                      label={summaryData.ai_summary.alerts_and_priorities.length}
                      size="small"
                      color="warning"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    {summaryData.ai_summary.alerts_and_priorities.map((alert, index) => (
                      <Alert
                        key={index}
                        severity={alert.priority === 'critical' ? 'error' : alert.priority === 'high' ? 'warning' : 'info'}
                        sx={{ mb: 2 }}
                      >
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            {alert.title}
                          </Typography>
                          <Typography variant="body2" gutterBottom>
                            {alert.description}
                          </Typography>
                          {alert.recommended_action && (
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              Action: {alert.recommended_action}
                            </Typography>
                          )}
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={alert.category} size="small" />
                            <Chip label={alert.priority} size="small" color={
                              alert.priority === 'critical' ? 'error' :
                              alert.priority === 'high' ? 'warning' : 'default'
                            } />
                          </Box>
                        </Box>
                      </Alert>
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Summary Info */}
            {summaryData.summary_info && (
              <Card sx={{ mt: 3, bgcolor: 'grey.50' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Details
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    <Chip
                      label={`Period: ${summaryData.summary_info.analysis_period_days || daysBack} days`}
                      size="small"
                    />
                    <Chip
                      label={`Generated: ${new Date(summaryData.summary_info.generated_at).toLocaleString()}`}
                      size="small"
                    />
                    {summaryData.summary_info.modules_analyzed && (
                      <Chip
                        label={`Modules: ${summaryData.summary_info.modules_analyzed.length}`}
                        size="small"
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default AIInsights;
