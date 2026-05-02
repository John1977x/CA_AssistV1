import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, ArrowLeft, CheckCircle, Eye, EyeOff } from 'lucide-react'
import { authApi } from '@/api/auth'

// ── Forgot Password ───────────────────────────────────────────────────────────
const forgotSchema = z.object({ email: z.string().email('Enter a valid email') })

export function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(forgotSchema),
  })

  const onSubmit = async ({ email }: { email: string }) => {
    setIsLoading(true)
    try {
      await authApi.forgotPassword(email)
      setSent(true)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-9 h-9 bg-brand-800 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">CA</span>
          </div>
          <span className="text-brand-800 font-bold text-lg">CA Assists</span>
        </div>

        {sent ? (
          <div className="card p-8 text-center">
            <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-green-600" size={28} />
            </div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">Check your email</h2>
            <p className="text-slate-500 text-sm mb-6">
              If this email is registered, you'll receive a password reset link shortly.
              Check your spam folder if you don't see it.
            </p>
            <Link to="/login" className="btn-secondary w-full flex items-center justify-center gap-2">
              <ArrowLeft size={16} /> Back to Login
            </Link>
          </div>
        ) : (
          <div className="card p-8">
            <h2 className="text-xl font-bold text-slate-900 mb-1">Forgot your password?</h2>
            <p className="text-slate-500 text-sm mb-6">
              Enter your email address and we'll send you a reset link.
            </p>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="label">Email Address</label>
                <input {...register('email')} type="email" placeholder="you@yourfirm.com"
                  className={`input ${errors.email ? 'input-error' : ''}`} />
                {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message as string}</p>}
              </div>
              <button type="submit" disabled={isLoading} className="btn-primary w-full">
                {isLoading ? <><Loader2 size={16} className="animate-spin" /> Sending...</> : 'Send Reset Link'}
              </button>
            </form>
            <div className="mt-4 text-center">
              <Link to="/login" className="text-sm text-brand-700 hover:underline flex items-center justify-center gap-1">
                <ArrowLeft size={14} /> Back to Login
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Reset Password ────────────────────────────────────────────────────────────
const resetSchema = z.object({
  new_password: z.string().min(8, 'Minimum 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain a number'),
  confirm_password: z.string(),
}).refine(d => d.new_password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [showPw, setShowPw] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [done, setDone] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(resetSchema),
  })

  const onSubmit = async (data: { new_password: string; confirm_password: string }) => {
    setIsLoading(true)
    try {
      await authApi.resetPassword({ token, ...data })
      setDone(true)
    } finally {
      setIsLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div className="card p-8 max-w-md w-full text-center">
          <p className="text-red-600 font-medium mb-4">Invalid reset link.</p>
          <Link to="/forgot-password" className="btn-primary">Request a new one</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-9 h-9 bg-brand-800 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">CA</span>
          </div>
          <span className="text-brand-800 font-bold text-lg">CA Assists</span>
        </div>

        {done ? (
          <div className="card p-8 text-center">
            <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-green-600" size={28} />
            </div>
            <h2 className="text-xl font-bold mb-2">Password Reset!</h2>
            <p className="text-slate-500 text-sm mb-6">Your password has been reset successfully.</p>
            <button onClick={() => navigate('/login')} className="btn-primary w-full">Login Now</button>
          </div>
        ) : (
          <div className="card p-8">
            <h2 className="text-xl font-bold text-slate-900 mb-1">Set new password</h2>
            <p className="text-slate-500 text-sm mb-6">Choose a strong password for your account.</p>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="label">New Password</label>
                <div className="relative">
                  <input {...register('new_password')} type={showPw ? 'text' : 'password'}
                    placeholder="Min 8 chars, uppercase & number"
                    className={`input pr-10 ${errors.new_password ? 'input-error' : ''}`} />
                  <button type="button" onClick={() => setShowPw(!showPw)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.new_password && <p className="mt-1 text-xs text-red-600">{errors.new_password.message as string}</p>}
              </div>
              <div>
                <label className="label">Confirm New Password</label>
                <input {...register('confirm_password')} type="password" placeholder="••••••••"
                  className={`input ${errors.confirm_password ? 'input-error' : ''}`} />
                {errors.confirm_password && <p className="mt-1 text-xs text-red-600">{errors.confirm_password.message as string}</p>}
              </div>
              <button type="submit" disabled={isLoading} className="btn-primary w-full">
                {isLoading ? <><Loader2 size={16} className="animate-spin" /> Resetting...</> : 'Reset Password'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}
