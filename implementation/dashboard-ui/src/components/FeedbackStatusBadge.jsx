import React from 'react'
import {
  Chip,
  Tooltip,
  Box,
  Typography
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Info as InfoIcon
} from '@mui/icons-material'
import { format } from 'date-fns'

/**
 * FeedbackStatusBadge Component
 *
 * Displays a color-coded badge showing the feedback/validation status of AI analysis.
 * Includes a tooltip with detailed information.
 *
 * Props:
 * - status: string - The feedback status ('accepted', 'rejected', 'refining', 'pending', or null)
 * - size: string - Size of the chip ('small', 'medium') - default: 'small'
 * - showLabel: boolean - Whether to show status text label - default: true
 * - timestamp: string - ISO timestamp of when status was set
 * - validatorName: string - Name of the person who provided feedback
 * - comment: string - Additional comment/reason for the feedback
 * - refinementCount: number - Number of refinements made (for 'refining' status)
 */
function FeedbackStatusBadge({
  status,
  size = 'small',
  showLabel = true,
  timestamp,
  validatorName,
  comment,
  refinementCount = 0
}) {
  // If no status, show 'Pending' or return null
  if (!status) {
    status = 'pending'
  }

  // Normalize status to lowercase
  const normalizedStatus = status.toLowerCase()

  // Status configuration mapping
  const statusConfig = {
    accepted: {
      label: 'Accepted',
      color: 'success',
      icon: CheckCircleIcon,
      bgColor: '#e8f5e9',
      textColor: '#2e7d32',
      description: 'AI analysis has been validated and accepted'
    },
    rejected: {
      label: 'Rejected',
      color: 'error',
      icon: CancelIcon,
      bgColor: '#ffebee',
      textColor: '#c62828',
      description: 'AI analysis was rejected and needs revision'
    },
    refining: {
      label: 'Refining',
      color: 'info',
      icon: EditIcon,
      bgColor: '#e3f2fd',
      textColor: '#1565c0',
      description: 'AI analysis is being refined with additional context'
    },
    refined: {
      label: 'Refined',
      color: 'info',
      icon: EditIcon,
      bgColor: '#e3f2fd',
      textColor: '#1565c0',
      description: 'AI analysis has been refined'
    },
    pending: {
      label: 'Pending Review',
      color: 'default',
      icon: HourglassEmptyIcon,
      bgColor: '#f5f5f5',
      textColor: '#757575',
      description: 'Awaiting human validation'
    }
  }

  // Get configuration for current status
  const config = statusConfig[normalizedStatus] || statusConfig.pending
  const StatusIcon = config.icon

  // Build tooltip content
  const renderTooltipContent = () => {
    return (
      <Box sx={{ p: 1 }}>
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          {config.label}
        </Typography>

        <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
          {config.description}
        </Typography>

        {timestamp && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
              <strong>Date:</strong> {format(new Date(timestamp), 'MMM dd, yyyy HH:mm')}
            </Typography>
          </Box>
        )}

        {validatorName && (
          <Box>
            <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
              <strong>Validator:</strong> {validatorName}
            </Typography>
          </Box>
        )}

        {normalizedStatus === 'refining' && refinementCount > 0 && (
          <Box>
            <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
              <strong>Refinements:</strong> {refinementCount}
            </Typography>
          </Box>
        )}

        {comment && (
          <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
            <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
              <strong>Comment:</strong>
            </Typography>
            <Typography variant="caption" display="block" sx={{ opacity: 0.9, mt: 0.5 }}>
              {comment.length > 100 ? `${comment.substring(0, 100)}...` : comment}
            </Typography>
          </Box>
        )}

        {!timestamp && !validatorName && !comment && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" display="block" sx={{ opacity: 0.7, fontStyle: 'italic' }}>
              No additional details available
            </Typography>
          </Box>
        )}
      </Box>
    )
  }

  // Render the badge with tooltip
  return (
    <Tooltip
      title={renderTooltipContent()}
      arrow
      placement="top"
      componentsProps={{
        tooltip: {
          sx: {
            bgcolor: 'rgba(33, 33, 33, 0.95)',
            '& .MuiTooltip-arrow': {
              color: 'rgba(33, 33, 33, 0.95)',
            },
            maxWidth: 350,
            boxShadow: 3
          }
        }
      }}
    >
      <Chip
        icon={<StatusIcon />}
        label={showLabel ? config.label : ''}
        color={config.color}
        size={size}
        sx={{
          fontWeight: 600,
          cursor: 'pointer',
          '&:hover': {
            opacity: 0.8
          }
        }}
      />
    </Tooltip>
  )
}

// Export variants for common use cases
export const AcceptedBadge = (props) => (
  <FeedbackStatusBadge status="accepted" {...props} />
)

export const RejectedBadge = (props) => (
  <FeedbackStatusBadge status="rejected" {...props} />
)

export const RefiningBadge = (props) => (
  <FeedbackStatusBadge status="refining" {...props} />
)

export const PendingBadge = (props) => (
  <FeedbackStatusBadge status="pending" {...props} />
)

export default FeedbackStatusBadge
