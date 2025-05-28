/**
 * MetricCard Component
 * Reusable card component for displaying key metrics
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  alpha,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  InfoOutlined,
} from '@mui/icons-material';

const MetricCard = ({
  title,
  value,
  unit = '',
  trend = null,
  trendValue = null,
  color = 'primary',
  icon = null,
  subtitle = null,
  tooltip = null,
  onClick = null,
  loading = false,
  error = null,
  target = null,
  progress = null,
  variant = 'default',
  size = 'medium',
}) => {
  const theme = useTheme();

  const getTrendIcon = () => {
    if (!trend) return null;

    switch (trend) {
      case 'up':
        return <TrendingUp sx={{ fontSize: 16 }} />;
      case 'down':
        return <TrendingDown sx={{ fontSize: 16 }} />;
      case 'stable':
        return <TrendingFlat sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'success';
      case 'down':
        return 'error';
      case 'stable':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatValue = (val) => {
    if (loading) return '...';
    if (error) return 'Error';
    if (val === null || val === undefined) return 'N/A';

    // Format large numbers
    if (typeof val === 'number') {
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`;
      } else if (val >= 1000) {
        return `${(val / 1000).toFixed(1)}K`;
      } else if (val % 1 !== 0) {
        return val.toFixed(1);
      }
    }

    return val.toString();
  };

  return (
    <Card
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s ease-in-out',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
        } : {},
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon && (
              <Box
                sx={{
                  p: 1,
                  borderRadius: 2,
                  backgroundColor: `${color}.light`,
                  color: `${color}.contrastText`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {icon}
              </Box>
            )}
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{
                fontSize: '0.875rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}
            >
              {title}
            </Typography>
          </Box>

          {tooltip && (
            <Tooltip title={tooltip} arrow>
              <IconButton size="small" sx={{ color: 'text.secondary' }}>
                <InfoOutlined fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Main Value */}
        <Box mb={1}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              color: error ? 'error.main' : `${color}.main`,
              lineHeight: 1,
            }}
          >
            {formatValue(value)}
            {unit && (
              <Typography
                component="span"
                variant="h5"
                sx={{
                  ml: 0.5,
                  color: 'text.secondary',
                  fontWeight: 400,
                }}
              >
                {unit}
              </Typography>
            )}
          </Typography>
        </Box>

        {/* Subtitle */}
        {subtitle && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 1 }}
          >
            {subtitle}
          </Typography>
        )}

        {/* Progress Bar */}
        {progress !== undefined && progress !== null && (
          <Box sx={{ mb: 1 }}>
            <LinearProgress
              variant="determinate"
              value={Math.min(progress, 100)}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: alpha(theme.palette[color].main, 0.1),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  bgcolor: theme.palette[color].main,
                },
              }}
            />
            {target && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                Target: {target}{unit} ({progress.toFixed(1)}% achieved)
              </Typography>
            )}
          </Box>
        )}

        {/* Trend */}
        {trend && trendValue !== null && trendValue !== undefined && (
          <Box display="flex" alignItems="center" gap={0.5}>
            <Chip
              icon={getTrendIcon()}
              label={`${trendValue > 0 ? '+' : ''}${trendValue}%`}
              size="small"
              color={getTrendColor()}
              variant="outlined"
              sx={{
                fontSize: '0.75rem',
                height: 24,
                '& .MuiChip-icon': {
                  fontSize: 14,
                },
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ ml: 0.5 }}
            >
              vs last period
            </Typography>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Typography
            variant="caption"
            color="error.main"
            sx={{ mt: 1, display: 'block' }}
          >
            {error}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;
