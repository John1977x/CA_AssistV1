/**
 * Error handling utility for the frontend.
 * Only shows important errors (CRITICAL and WARNING) as popups.
 * SILENT errors are logged but not shown to the user.
 */

import toast from 'react-hot-toast'

export type ErrorSeverity = 'critical' | 'warning' | 'info' | 'silent'

export interface ApiErrorResponse {
  detail: string
  status_code: number
  severity: ErrorSeverity
  error_code: string
}

export interface ApiError {
  response?: {
    status: number
    data?: ApiErrorResponse
  }
  message?: string
}

/**
 * Handle API errors and show appropriate messages to user
 * Only shows CRITICAL and WARNING errors as popups
 */
export function handleApiError(error: any): void {
  const errorData = error?.response?.data as ApiErrorResponse | undefined

  // If no error data, show generic error
  if (!errorData) {
    const message = error?.message || 'An unexpected error occurred'
    console.error('API Error:', message)
    // Only show if it's not a network error or abort
    if (!message.includes('abort') && !message.includes('Network')) {
      toast.error('Something went wrong. Please try again.')
    }
    return
  }

  const { detail, severity, error_code, status_code } = errorData

  // Log all errors for debugging
  console.error(`[${error_code}] ${detail}`, { status_code, severity })

  // Only show CRITICAL and WARNING errors to user
  if (severity === 'critical') {
    toast.error(detail, {
      duration: 5000,
      icon: '❌',
    })
  } else if (severity === 'warning') {
    toast.error(detail, {
      duration: 4000,
      icon: '⚠️',
    })
  } else if (severity === 'info') {
    // Info messages are logged but not shown
    console.info(`[${error_code}] ${detail}`)
  } else if (severity === 'silent') {
    // Silent errors are only logged
    console.debug(`[${error_code}] ${detail}`)
  }
}

/**
 * Handle specific error codes with custom messages
 */
export function getErrorMessage(errorCode: string, defaultMessage: string): string {
  const errorMessages: Record<string, string> = {
    // Auth errors
    'AUTH_FAILED': 'Invalid email or password',
    'AUTH_DENIED': 'You don\'t have permission to perform this action',
    'INVALID_TOKEN': 'Your session has expired. Please login again.',
    'TOKEN_EXPIRED': 'Your session has expired. Please login again.',

    // Validation errors
    'VALIDATION_ERROR': 'Please check your input and try again',
    'INVALID_EMAIL': 'Please enter a valid email address',
    'INVALID_PASSWORD': 'Password does not meet requirements',
    'WEAK_PASSWORD': 'Password is too weak. Use uppercase, lowercase, numbers, and symbols.',

    // Resource errors
    'NOT_FOUND': 'The requested resource was not found',
    'ALREADY_EXISTS': 'This resource already exists',
    'CONFLICT': 'This action conflicts with existing data',

    // Limit errors
    'LIMIT_EXCEEDED': 'You have reached the limit for this action',
    'USER_LIMIT_EXCEEDED': 'You have reached the maximum number of users for your plan',
    'STORAGE_LIMIT_EXCEEDED': 'You have reached your storage limit',

    // Business logic errors
    'BUSINESS_LOGIC_ERROR': 'This action cannot be performed at this time',
    'INVALID_STATE': 'The resource is in an invalid state for this operation',
    'OPERATION_NOT_ALLOWED': 'This operation is not allowed',

    // External service errors
    'EXTERNAL_SERVICE_ERROR': 'An external service is temporarily unavailable',
    'STRIPE_ERROR': 'Payment processing failed. Please try again.',
    'EMAIL_ERROR': 'Failed to send email. Please try again.',

    // Internal errors
    'INTERNAL_ERROR': 'An internal error occurred. Please try again later.',
    'DATABASE_ERROR': 'A database error occurred. Please try again.',
    'UNKNOWN_ERROR': 'An unexpected error occurred',
  }

  return errorMessages[errorCode] || defaultMessage
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
  const status = error?.response?.status
  const errorCode = error?.response?.data?.error_code

  // Retry on 5xx errors (server errors)
  if (status && status >= 500) return true

  // Retry on specific error codes
  const retryableErrors = ['EXTERNAL_SERVICE_ERROR', 'TIMEOUT', 'NETWORK_ERROR']
  if (retryableErrors.includes(errorCode)) return true

  return false
}

/**
 * Check if error is authentication related
 */
export function isAuthError(error: any): boolean {
  const status = error?.response?.status
  const errorCode = error?.response?.data?.error_code

  return status === 401 || ['AUTH_FAILED', 'INVALID_TOKEN', 'TOKEN_EXPIRED'].includes(errorCode)
}

/**
 * Check if error is authorization related
 */
export function isAuthorizationError(error: any): boolean {
  const status = error?.response?.status
  const errorCode = error?.response?.data?.error_code

  return status === 403 || errorCode === 'AUTH_DENIED'
}
