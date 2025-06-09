/**
 * Date Picker Filter Component
 * Provides date range selection with predefined options
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Popover,
  ClickAwayListener,
  Paper,
} from '@mui/material';
import {
  DateRange as DateRangeIcon,
  Clear as ClearIcon,
  Today as TodayIcon,
  Check as CheckIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';
// Note: Using basic TextField for date input instead of MUI DatePicker to avoid additional dependencies
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
// import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
// import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const DatePickerFilter = ({
  dateRange,
  onDateRangeChange,
  showDaysBackOption = true,
  label = "Date Filter",
  compact = false
}) => {
  const [filterType, setFilterType] = useState('daysBack');
  // Local state for custom date selection to prevent premature API calls
  const [localCustomDates, setLocalCustomDates] = useState({
    startDate: null,
    endDate: null
  });
  // State for calendar dropdown
  const [calendarAnchorEl, setCalendarAnchorEl] = useState(null);
  const isCalendarOpen = Boolean(calendarAnchorEl);

  // Sync local custom dates with incoming dateRange prop when it changes externally
  useEffect(() => {
    if (dateRange.startDate || dateRange.endDate) {
      setLocalCustomDates({
        startDate: dateRange.startDate,
        endDate: dateRange.endDate
      });
    }
  }, [dateRange.startDate, dateRange.endDate]);

  // Predefined date range options
  const daysBackOptions = [
    { value: 7, label: 'Last 7 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 90, label: 'Last 90 days' },
    { value: 180, label: 'Last 6 months' },
    { value: 365, label: 'Last year' },
    { value: 730, label: 'Last 2 years' },
  ];

  // Handle filter type change
  const handleFilterTypeChange = (event) => {
    const newType = event.target.value;
    setFilterType(newType);

    if (newType === 'daysBack') {
      // Reset to default days back and clear local custom dates
      setLocalCustomDates({ startDate: null, endDate: null });
      onDateRangeChange({
        startDate: null,
        endDate: null,
        daysBack: 365
      });
    } else {
      // Reset to custom date range and clear local custom dates
      setLocalCustomDates({ startDate: null, endDate: null });
      // Don't trigger API call yet for custom range
    }
  };

  // Handle days back change
  const handleDaysBackChange = (event) => {
    const daysBack = event.target.value;
    onDateRangeChange({
      startDate: null,
      endDate: null,
      daysBack: daysBack
    });
  };

  // Handle start date change - only update local state, don't trigger API call yet
  const handleStartDateChange = (newDate) => {
    setLocalCustomDates({
      ...localCustomDates,
      startDate: newDate
    });
  };

  // Handle end date change - only update local state, don't trigger API call yet
  const handleEndDateChange = (newDate) => {
    setLocalCustomDates({
      ...localCustomDates,
      endDate: newDate
    });
  };

  // Handle apply custom date range
  const handleApplyCustomRange = () => {
    if (localCustomDates.startDate && localCustomDates.endDate) {
      onDateRangeChange({
        startDate: localCustomDates.startDate,
        endDate: localCustomDates.endDate,
        daysBack: null
      });
      setCalendarAnchorEl(null); // Close the calendar dropdown
    }
  };

  // Handle calendar button click
  const handleCalendarClick = (event) => {
    setCalendarAnchorEl(event.currentTarget);
    setFilterType('custom');
  };

  // Handle calendar close
  const handleCalendarClose = () => {
    setCalendarAnchorEl(null);
  };

  // Clear date filters
  const handleClear = () => {
    setLocalCustomDates({ startDate: null, endDate: null });
    onDateRangeChange({
      startDate: null,
      endDate: null,
      daysBack: 365
    });
    setFilterType('daysBack');
  };

  // Set to today
  const handleToday = () => {
    const today = new Date();
    setLocalCustomDates({ startDate: today, endDate: today });
    onDateRangeChange({
      startDate: today,
      endDate: today,
      daysBack: null
    });
    setFilterType('custom');
  };

  // Compact layout for dashboard header
  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* Single dropdown with predefined options only */}
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <Select
            value={`days_${dateRange.daysBack || 365}`}
            onChange={(e) => {
              const value = e.target.value;
              if (value.startsWith('days_')) {
                const days = parseInt(value.replace('days_', ''));
                setFilterType('daysBack');
                setCalendarAnchorEl(null); // Close calendar if open
                onDateRangeChange({
                  startDate: null,
                  endDate: null,
                  daysBack: days
                });
              }
            }}
            displayEmpty
            sx={{
              bgcolor: 'white',
              border: '1px solid #e5e7eb',
              '& .MuiOutlinedInput-notchedOutline': {
                border: 'none',
              },
              '&:hover': {
                bgcolor: '#f8fafc',
              },
              '& .MuiSelect-select': {
                py: 1,
                px: 1.5,
              }
            }}
          >
            {daysBackOptions.map((option) => (
              <MenuItem key={`days_${option.value}`} value={`days_${option.value}`}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Calendar Button for Custom Range */}
        <Tooltip title="Custom Date Range">
          <IconButton
            onClick={handleCalendarClick}
            size="small"
            sx={{
              bgcolor: isCalendarOpen ? '#092f57' : 'white',
              color: isCalendarOpen ? 'white' : '#092f57',
              border: '1px solid #e5e7eb',
              p: 1.5,
              '&:hover': {
                bgcolor: isCalendarOpen ? '#0a3a6b' : '#f8fafc',
              },
            }}
          >
            <CalendarIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Tooltip>

        {/* Calendar Dropdown Popover */}
        <Popover
          open={isCalendarOpen}
          anchorEl={calendarAnchorEl}
          onClose={handleCalendarClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'left',
          }}
        >
          <ClickAwayListener onClickAway={handleCalendarClose}>
            <Paper sx={{ p: 2, minWidth: 400 }}>
              <Typography variant="subtitle2" sx={{ mb: 2, color: '#092f57', fontWeight: 600 }}>
                Select Custom Date Range
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                {/* Start Date */}
                <TextField
                  type="date"
                  size="small"
                  label="Start Date"
                  value={localCustomDates.startDate ? localCustomDates.startDate.toISOString().split('T')[0] : ''}
                  onChange={(e) => handleStartDateChange(e.target.value ? new Date(e.target.value) : null)}
                  InputLabelProps={{ shrink: true }}
                  inputProps={{
                    max: localCustomDates.endDate ? localCustomDates.endDate.toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
                  }}
                  sx={{ flex: 1 }}
                />

                {/* End Date */}
                <TextField
                  type="date"
                  size="small"
                  label="End Date"
                  value={localCustomDates.endDate ? localCustomDates.endDate.toISOString().split('T')[0] : ''}
                  onChange={(e) => handleEndDateChange(e.target.value ? new Date(e.target.value) : null)}
                  InputLabelProps={{ shrink: true }}
                  inputProps={{
                    min: localCustomDates.startDate ? localCustomDates.startDate.toISOString().split('T')[0] : undefined,
                    max: new Date().toISOString().split('T')[0]
                  }}
                  sx={{ flex: 1 }}
                />
              </Box>

              {/* Warning/Info Messages */}
              {(!localCustomDates.startDate || !localCustomDates.endDate) && (
                <Typography variant="caption" color="warning.main" sx={{ display: 'block', mb: 2 }}>
                  ⚠️ Please select both start and end dates
                </Typography>
              )}

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleCalendarClose}
                  sx={{ color: '#6b7280', borderColor: '#d1d5db' }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleApplyCustomRange}
                  disabled={!localCustomDates.startDate || !localCustomDates.endDate}
                  startIcon={<CheckIcon />}
                  sx={{
                    bgcolor: '#092f57',
                    '&:hover': {
                      bgcolor: '#0a3a6b',
                    },
                    '&:disabled': {
                      bgcolor: '#e5e7eb',
                      color: '#9ca3af',
                    },
                  }}
                >
                  Apply
                </Button>
              </Box>
            </Paper>
          </ClickAwayListener>
        </Popover>
      </Box>
    );
  }

  // Full layout for other uses
  return (
    <Box sx={{ width: '100%' }}>
        <Grid container spacing={2} alignItems="center">
          {/* Filter Type Selection */}
          <Grid item xs={12} sm={4}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl fullWidth size="small">
                <InputLabel>Time Period</InputLabel>
                <Select
                  value={dateRange.daysBack || 365}
                  onChange={handleDaysBackChange}
                  label="Time Period"
                >
                  {daysBackOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Calendar Button for Custom Range */}
              <Tooltip title="Custom Date Range">
                <IconButton
                  onClick={handleCalendarClick}
                  size="small"
                  sx={{
                    bgcolor: isCalendarOpen ? '#092f57' : 'white',
                    color: isCalendarOpen ? 'white' : '#092f57',
                    border: '1px solid #e5e7eb',
                    p: 1.5,
                    '&:hover': {
                      bgcolor: isCalendarOpen ? '#0a3a6b' : '#f8fafc',
                    },
                  }}
                >
                  <CalendarIcon sx={{ fontSize: 20 }} />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>



          {/* Action Buttons */}
          <Grid item xs={12} sm={8}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Tooltip title="Set to Today">
                <IconButton onClick={handleToday} size="small">
                  <TodayIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Clear Filters">
                <IconButton onClick={handleClear} size="small">
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>

        {/* Calendar Dropdown Popover for Full Layout */}
        <Popover
          open={isCalendarOpen}
          anchorEl={calendarAnchorEl}
          onClose={handleCalendarClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'left',
          }}
        >
          <ClickAwayListener onClickAway={handleCalendarClose}>
            <Paper sx={{ p: 2, minWidth: 400 }}>
              <Typography variant="subtitle2" sx={{ mb: 2, color: '#092f57', fontWeight: 600 }}>
                Select Custom Date Range
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                {/* Start Date */}
                <TextField
                  type="date"
                  size="small"
                  label="Start Date"
                  value={localCustomDates.startDate ? localCustomDates.startDate.toISOString().split('T')[0] : ''}
                  onChange={(e) => handleStartDateChange(e.target.value ? new Date(e.target.value) : null)}
                  InputLabelProps={{ shrink: true }}
                  inputProps={{
                    max: localCustomDates.endDate ? localCustomDates.endDate.toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
                  }}
                  sx={{ flex: 1 }}
                />

                {/* End Date */}
                <TextField
                  type="date"
                  size="small"
                  label="End Date"
                  value={localCustomDates.endDate ? localCustomDates.endDate.toISOString().split('T')[0] : ''}
                  onChange={(e) => handleEndDateChange(e.target.value ? new Date(e.target.value) : null)}
                  InputLabelProps={{ shrink: true }}
                  inputProps={{
                    min: localCustomDates.startDate ? localCustomDates.startDate.toISOString().split('T')[0] : undefined,
                    max: new Date().toISOString().split('T')[0]
                  }}
                  sx={{ flex: 1 }}
                />
              </Box>

              {/* Warning/Info Messages */}
              {(!localCustomDates.startDate || !localCustomDates.endDate) && (
                <Typography variant="caption" color="warning.main" sx={{ display: 'block', mb: 2 }}>
                  ⚠️ Please select both start and end dates
                </Typography>
              )}

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleCalendarClose}
                  sx={{ color: '#6b7280', borderColor: '#d1d5db' }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleApplyCustomRange}
                  disabled={!localCustomDates.startDate || !localCustomDates.endDate}
                  startIcon={<CheckIcon />}
                  sx={{
                    bgcolor: '#092f57',
                    '&:hover': {
                      bgcolor: '#0a3a6b',
                    },
                    '&:disabled': {
                      bgcolor: '#e5e7eb',
                      color: '#9ca3af',
                    },
                  }}
                >
                  Apply
                </Button>
              </Box>
            </Paper>
          </ClickAwayListener>
        </Popover>



        {/* Current Filter Display */}
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <DateRangeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            Current filter:
          </Typography>

          {filterType === 'daysBack' && dateRange.daysBack ? (
            <Chip
              label={`Last ${dateRange.daysBack} days`}
              size="small"
              color="primary"
              variant="outlined"
            />
          ) : filterType === 'custom' && dateRange.startDate && dateRange.endDate ? (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label={`From: ${dateRange.startDate.toLocaleDateString()}`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`To: ${dateRange.endDate.toLocaleDateString()}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
          ) : filterType === 'custom' && (dateRange.startDate || dateRange.endDate) ? (
            <Chip
              label="Incomplete date range"
              size="small"
              color="warning"
              variant="outlined"
            />
          ) : (
            <Chip
              label="Using default range (Last 365 days)"
              size="small"
              color="default"
              variant="outlined"
            />
          )}
        </Box>
      </Box>
  );
};

export default DatePickerFilter;
