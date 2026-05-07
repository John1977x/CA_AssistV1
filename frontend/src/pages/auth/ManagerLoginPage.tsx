import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, Briefcase } from 'lucide-react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import type { LoginForm } from '@/types/auth'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  remember_me: z.boolean().default(false),
})

type LoginFormData = z.infer<typeof schema>

export default function ManagerLoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(schema),
    defaultValues: { remember_me: false },
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      const result = await authApi.login(data)
      setAuth(result.user, result.access_token, result.refresh_token)
      navigate('/manager/dashboard')
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
      <div className="hidden lg:flex lg:w-1/2 bg-indigo-600 flex-col justify-between p-12">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
              <Briefcase className="text-indigo-600" size={24} />
            </div>
            <span className="text-white text-xl font-bold">CA Assists</span>
          </div>
          <h1 className="text-white text-4xl font-bold leading-tight mb-4">
            Manager Portal
          </h1>
          <p className="text-indigo-100 text-lg leading-relaxed">
            Manage teams, oversee projects, and track firm performance.
          </p>
        </div>

        <div className="space-y-4">
          {[
            { icon: '👥', text: 'Manage team members and assignments' },
            { icon: '📊', text: 'Track project progress and metrics' },
            { icon: '✅', text: 'Approve tasks and deliverables' },
            { icon: '📈', text: 'View performance reports' },
          ].map((f) => (
            <div key={f.text} className="flex items-center gap-3">
              <span className="text-xl">{f.icon}</span>
              <span className="text-indigo-100 text-sm">{f.text}</span>
            </div>
          ))}
        </div>

        <p className="text-indigo-300 text-xs">
          Management dashboard for CA Assists
        </p>
      </div>

      {/* Right — Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-slate-50">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Briefcase className="text-white" size={18} />
            </div>
            <span className="text-indigo-600 font-bold text-lg">CA Assists</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900">Manager Login</h2>
            <p className="text-slate-500 mt-1 text-sm">
              Sign in to access your management dashboard
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
                placeholder="manager@firm.com"
                className={`input ${errors.email ? 'input-error' : ''}`}
              />
              {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="label mb-0">Password</label>
                <Link to="/forgot-password" className="text-xs text-indigo-600 hover:underline">
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
                className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="remember" className="text-sm text-slate-600">
                Keep me signed in
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <><Loader2 size={16} className="animate-spin" /> Signing in...</>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <p className="text-sm text-indigo-800">
              <strong>Demo Credentials:</strong><br />
              Email: manager@firm.com<br />
              Password: CAassist@2026
            </p>
          </div>

          <p className="mt-8 text-center text-xs text-slate-400">
            By signing in, you agree to our{' '}
            <a href="#" className="underline hover:text-slate-600">Terms of Service</a>
          </p>
        </div>
      </div>
    </div>
  )
}
