/**
 * Date Range Picker Component
 * Allows users to select from date and to date for filtering data
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Typography,
  Paper,
  Divider,
} from '@mui/material';
import {
  DateRange,
  Today,
  CalendarMonth,
  Refresh,
} from '@mui/icons-material';

const DateRangePicker = ({
  fromDate,
  toDate,
  onDateChange,
  onApply,
  onReset,
  disabled = false,
  showPresets = true,
  showApplyButton = true,
}) => {
  const [localFromDate, setLocalFromDate] = useState(fromDate || '');
  const [localToDate, setLocalToDate] = useState(toDate || '');

  // Preset date ranges
  const presets = [
    {
      label: 'Last 7 days',
      value: 7,
      icon: <Today fontSize="small" />,
    },
    {
      label: 'Last 30 days',
      value: 30,
      icon: <CalendarMonth fontSize="small" />,
    },
    {
      label: 'Last 90 days',
      value: 90,
      icon: <DateRange fontSize="small" />,
    },
    {
      label: 'Last 6 months',
      value: 180,
      icon: <DateRange fontSize="small" />,
    },
    {
      label: 'Last year',
      value: 365,
      icon: <DateRange fontSize="small" />,
    },
  ];

  const handlePresetClick = (days) => {
    const toDate = new Date();
    const fromDate = new Date();
    fromDate.setDate(toDate.getDate() - days);

    const fromDateStr = fromDate.toISOString().split('T')[0];
    const toDateStr = toDate.toISOString().split('T')[0];

    setLocalFromDate(fromDateStr);
    setLocalToDate(toDateStr);

    if (onDateChange) {
      onDateChange(fromDateStr, toDateStr);
    }

    // Always trigger onApply for presets, regardless of showApplyButton
    if (onApply) {
      onApply(fromDateStr, toDateStr);
    }
  };

  const handleFromDateChange = (event) => {
    const newFromDate = event.target.value;
    setLocalFromDate(newFromDate);

    if (onDateChange) {
      onDateChange(newFromDate, localToDate);
    }

    if (!showApplyButton && onApply) {
      onApply(newFromDate, localToDate);
    }
  };

  const handleToDateChange = (event) => {
    const newToDate = event.target.value;
    setLocalToDate(newToDate);

    if (onDateChange) {
      onDateChange(localFromDate, newToDate);
    }

    if (!showApplyButton && onApply) {
      onApply(localFromDate, newToDate);
    }
  };

  const handleApply = () => {
    if (onApply) {
      onApply(localFromDate, localToDate);
    }
  };

  const handleReset = () => {
    setLocalFromDate('');
    setLocalToDate('');

    if (onDateChange) {
      onDateChange('', '');
    }

    if (onReset) {
      onReset();
    }
  };

  const isValidDateRange = localFromDate && localToDate && localFromDate <= localToDate;

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <DateRange />
        Date Range Filter
      </Typography>

      <Stack spacing={2}>
        {/* Custom Date Range */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Custom Date Range
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              label="From Date"
              type="date"
              value={localFromDate}
              onChange={handleFromDateChange}
              disabled={disabled}
              InputLabelProps={{
                shrink: true,
              }}
              size="small"
              sx={{ minWidth: 150 }}
            />
            <TextField
              label="To Date"
              type="date"
              value={localToDate}
              onChange={handleToDateChange}
              disabled={disabled}
              InputLabelProps={{
                shrink: true,
              }}
              size="small"
              sx={{ minWidth: 150 }}
              inputProps={{
                min: localFromDate || undefined,
              }}
            />
            {showApplyButton && (
              <Button
                variant="contained"
                onClick={handleApply}
                disabled={disabled || !isValidDateRange}
                size="small"
              >
                Apply
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={handleReset}
              disabled={disabled}
              size="small"
              startIcon={<Refresh />}
            >
              Reset
            </Button>
          </Stack>
        </Box>

        {/* Quick Presets */}
        {showPresets && (
          <>
            <Divider />
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Quick Presets
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {presets.map((preset) => (
                  <Chip
                    key={preset.value}
                    label={preset.label}
                    icon={preset.icon}
                    onClick={() => handlePresetClick(preset.value)}
                    disabled={disabled}
                    variant="outlined"
                    clickable
                    size="small"
                  />
                ))}
              </Stack>
            </Box>
          </>
        )}

        {/* Current Selection Display */}
        {(localFromDate || localToDate) && (
          <>
            <Divider />
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Current Selection
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {localFromDate && localToDate
                  ? `From ${new Date(localFromDate).toLocaleDateString()} to ${new Date(localToDate).toLocaleDateString()}`
                  : localFromDate
                  ? `From ${new Date(localFromDate).toLocaleDateString()}`
                  : localToDate
                  ? `To ${new Date(localToDate).toLocaleDateString()}`
                  : 'No dates selected'}
              </Typography>
              {localFromDate && localToDate && (
                <Typography variant="caption" color="text.secondary">
                  {Math.ceil((new Date(localToDate) - new Date(localFromDate)) / (1000 * 60 * 60 * 24)) + 1} days selected
                </Typography>
              )}
            </Box>
          </>
        )}
      </Stack>
    </Paper>
  );
};

export default DateRangePicker;
