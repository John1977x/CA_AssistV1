import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { authV2Api } from '@/api/authV2'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  remember_me: z.boolean().default(false),
})

type LoginFormData = z.infer<typeof schema>

export default function LoginPageV2() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStoreV2()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(schema),
    defaultValues: { remember_me: false },
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      const response = await authV2Api.login({
        email: data.email,
        password: data.password,
      })

      setAuth(response.user, response.company, response.access_token, response.refresh_token)

      // Route based on role - no toast notification
      setTimeout(() => {
        switch (response.company.role) {
          case 'OWNER':
            navigate('/owner/dashboard')
            break
          case 'MANAGER':
            navigate('/manager/dashboard')
            break
          case 'EMPLOYEE':
            navigate('/employee/dashboard')
            break
          case 'CLIENT':
            navigate('/client/dashboard')
            break
          default:
            navigate('/owner/dashboard')
        }
      }, 100)
    } catch (err: any) {
      // Silent error handling - no toast notification
      console.error('Login failed:', err)
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
              <Link to="/register-owner" className="text-brand-700 font-medium hover:underline">
                Create one
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
