import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import type { LoginForm } from '@/types/auth'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  totp_code: z.string().optional(),
  remember_me: z.boolean().default(false),
})

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const [showPassword, setShowPassword] = useState(false)
  const [needs2FA, setNeeds2FA] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(schema),
    defaultValues: { remember_me: false },
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const result = await authApi.login(data)
      setAuth(result.user, result.access_token, result.refresh_token)
      toast.success(`Welcome back, ${result.user.first_name}!`)
      navigate('/dashboard')
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (detail === '2FA_REQUIRED' || err?.response?.headers?.['x-2fa-required']) {
        setNeeds2FA(true)
        toast('Please enter your authenticator code.', { icon: '🔐' })
      }
      // Other errors handled by axios interceptor
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left — Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-brand-800 flex-col justify-between p-12">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
              <span className="text-brand-800 font-bold text-lg">CA</span>
            </div>
            <span className="text-white text-xl font-bold">CA Assists</span>
          </div>
          <h1 className="text-white text-4xl font-bold leading-tight mb-4">
            Your Complete<br />CA Practice Suite
          </h1>
          <p className="text-brand-200 text-lg leading-relaxed">
            GST filing, ITR preparation, task management, and client communication — all in one place.
          </p>
        </div>

        <div className="space-y-4">
          {[
            { icon: '📊', text: 'Automated GSTR-1 & GSTR-3B filing' },
            { icon: '📋', text: 'Task & deadline tracking with alerts' },
            { icon: '👥', text: 'Client management with document vault' },
            { icon: '🔒', text: 'Bank-grade security for sensitive data' },
          ].map((f) => (
            <div key={f.text} className="flex items-center gap-3">
              <span className="text-xl">{f.icon}</span>
              <span className="text-brand-100 text-sm">{f.text}</span>
            </div>
          ))}
        </div>

        <p className="text-brand-300 text-xs">
          Trusted by 1,000+ CA firms across India
        </p>
      </div>

      {/* Right — Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-slate-50">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-brand-800 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CA</span>
            </div>
            <span className="text-brand-800 font-bold text-lg">CA Assists</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900">Sign in to your account</h2>
            <p className="text-slate-500 mt-1 text-sm">
              Don't have an account?{' '}
              <Link to="/register" className="text-brand-700 font-medium hover:underline">
                Start free trial
              </Link>
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email */}
            <div>
              <label className="label">Email address</label>
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                placeholder="you@yourfirm.com"
                className={`input ${errors.email ? 'input-error' : ''}`}
              />
              {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="label mb-0">Password</label>
                <Link to="/forgot-password" className="text-xs text-brand-700 hover:underline">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
            </div>

            {/* 2FA code — shown only when required */}
            {needs2FA && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">
                    Two-factor authentication required
                  </span>
                </div>
                <label className="label text-blue-800">Authenticator Code</label>
                <input
                  {...register('totp_code')}
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="000000"
                  className="input text-center text-lg tracking-widest font-mono"
                />
              </div>
            )}

            {/* Remember me */}
            <div className="flex items-center gap-2">
              <input
                {...register('remember_me')}
                type="checkbox"
                id="remember"
                className="w-4 h-4 rounded border-slate-300 text-brand-700 focus:ring-brand-500"
              />
              <label htmlFor="remember" className="text-sm text-slate-600">
                Keep me signed in
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full btn-lg"
            >
              {isLoading ? (
                <><Loader2 size={16} className="animate-spin" /> Signing in...</>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400">
            By signing in, you agree to our{' '}
            <a href="#" className="underline hover:text-slate-600">Terms of Service</a> and{' '}
            <a href="#" className="underline hover:text-slate-600">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  )
}
