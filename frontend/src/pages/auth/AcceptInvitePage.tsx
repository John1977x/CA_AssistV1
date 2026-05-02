import { useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { usersApi } from '@/api/users'

const schema = z.object({
  password: z.string()
    .min(8, 'Minimum 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirm_password: z.string(),
}).refine(d => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export default function AcceptInvitePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [showPw, setShowPw] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [done, setDone] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: { password: string; confirm_password: string }) => {
    if (!token) return
    setIsLoading(true)
    try {
      await usersApi.acceptInvite(token, data.password)
      setDone(true)
      toast.success('Account activated!')
    } catch {
      // handled by interceptor
    } finally {
      setIsLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div className="card p-8 max-w-md w-full text-center">
          <p className="text-red-600 font-medium mb-4">Invalid invitation link.</p>
          <p className="text-slate-500 text-sm">Please contact your firm administrator for a new invite.</p>
        </div>
      </div>
    )
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div className="card p-10 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <CheckCircle className="text-green-600" size={30} />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Account Activated!</h2>
          <p className="text-slate-500 text-sm mb-6">
            Your CA Assists account is ready. Log in to get started.
          </p>
          <button onClick={() => navigate('/login')} className="btn-primary btn-lg w-full">
            Login Now
          </button>
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

        <div className="card p-8">
          <h2 className="text-xl font-bold text-slate-900 mb-1">Accept Your Invitation</h2>
          <p className="text-slate-500 text-sm mb-6">
            Set a password to activate your account.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">New Password</label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPw ? 'text' : 'password'}
                  placeholder="Min 8 chars, uppercase & number"
                  className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message as string}</p>
              )}
            </div>

            <div>
              <label className="label">Confirm Password</label>
              <input
                {...register('confirm_password')}
                type="password"
                placeholder="••••••••"
                className={`input ${errors.confirm_password ? 'input-error' : ''}`}
              />
              {errors.confirm_password && (
                <p className="mt-1 text-xs text-red-600">{errors.confirm_password.message as string}</p>
              )}
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full btn-lg">
              {isLoading
                ? <><Loader2 size={16} className="animate-spin" /> Activating...</>
                : 'Activate Account'
              }
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
