/**
 * AI Insights Test Component
 * Simple test component to verify AI insights functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel
} from '@mui/material';
import ApiService from '../../services/api';

const AIInsightsTest = () => {
  const [aiEnabled, setAiEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const testAIAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing AI Analysis...');
      
      // Test incident investigation AI analysis
      const response = await ApiService.getIncidentInvestigationAIAnalysis(null, 30, true);
      console.log('🧪 AI Response:', response);
      
      setResult(response);
    } catch (err) {
      console.error('🧪 AI Test Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testHealthCheck = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing Health Check...');
      const response = await ApiService.healthCheck();
      console.log('🧪 Health Response:', response);
      setResult(response);
    } catch (err) {
      console.error('🧪 Health Test Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testModuleData = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing Module Data...');
      const response = await ApiService.getIncidentInvestigationModuleKPIs(null, null, null, 30);
      console.log('🧪 Module Data Response:', response);
      setResult(response);
    } catch (err) {
      console.error('🧪 Module Data Test Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🧪 AI Insights Test Component
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        Use this component to test AI insights functionality step by step.
      </Typography>

      {/* AI Toggle Test */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            1. AI Toggle Test
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={aiEnabled}
                onChange={(e) => {
                  setAiEnabled(e.target.checked);
                  console.log('🧪 AI Toggle:', e.target.checked);
                }}
              />
            }
            label={`AI Insights ${aiEnabled ? 'Enabled' : 'Disabled'}`}
          />
          {aiEnabled && (
            <Alert severity="success" sx={{ mt: 2 }}>
              ✅ AI Toggle is working! State: {aiEnabled.toString()}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* API Tests */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            2. API Connection Tests
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
            <Button 
              variant="outlined" 
              onClick={testHealthCheck}
              disabled={loading}
            >
              Test Health Check
            </Button>
            <Button 
              variant="outlined" 
              onClick={testModuleData}
              disabled={loading}
            >
              Test Module Data
            </Button>
            <Button 
              variant="contained" 
              onClick={testAIAnalysis}
              disabled={loading}
            >
              Test AI Analysis
            </Button>
          </Box>
          
          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress size={20} />
              <Typography>Testing...</Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">❌ Error:</Typography>
          <Typography>{error}</Typography>
        </Alert>
      )}

      {result && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              ✅ Test Result:
            </Typography>
            <Box sx={{ 
              bgcolor: '#f5f5f5', 
              p: 2, 
              borderRadius: 1, 
              maxHeight: 400, 
              overflow: 'auto' 
            }}>
              <pre style={{ margin: 0, fontSize: '12px' }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📋 Testing Instructions:
          </Typography>
          <Typography component="div">
            <ol>
              <li><strong>Toggle AI Switch</strong> - Should show green success message</li>
              <li><strong>Test Health Check</strong> - Should return server status</li>
              <li><strong>Test Module Data</strong> - Should return KPI data</li>
              <li><strong>Test AI Analysis</strong> - Should return AI insights</li>
            </ol>
          </Typography>
          <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
            Check the browser console for detailed logs. If any test fails, 
            check the error message and ensure the backend server is running.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AIInsightsTest;
