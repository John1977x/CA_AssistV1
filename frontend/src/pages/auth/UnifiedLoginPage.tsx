import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, Building2, Users, User, UserCheck } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { authV2Api } from '@/api/authV2'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  remember_me: z.boolean().default(false),
})

type LoginFormData = z.infer<typeof schema>

interface SlideInfo {
  id: number
  title: string
  subtitle: string
  description: string
  icon: React.ReactNode
  bgGradient: string
  color: string
}

const slides: SlideInfo[] = [
  {
    id: 1,
    title: 'Owner',
    subtitle: 'Firm Management',
    description: 'Manage your entire firm, clients, and team members with full control and insights.',
    icon: <Building2 size={48} />,
    bgGradient: 'from-amber-500 to-orange-600',
    color: 'bg-amber-500',
  },
  {
    id: 2,
    title: 'Manager',
    subtitle: 'Team Leadership',
    description: 'Lead your team, manage projects, and track performance metrics in real-time.',
    icon: <Users size={48} />,
    bgGradient: 'from-blue-500 to-indigo-600',
    color: 'bg-blue-500',
  },
  {
    id: 3,
    title: 'Employee',
    subtitle: 'Task Management',
    description: 'Complete your tasks, collaborate with team, and track your productivity.',
    icon: <User size={48} />,
    bgGradient: 'from-green-500 to-emerald-600',
    color: 'bg-green-500',
  },
  {
    id: 4,
    title: 'Client',
    subtitle: 'Project Access',
    description: 'View your projects, track progress, and communicate with your service provider.',
    icon: <UserCheck size={48} />,
    bgGradient: 'from-purple-500 to-pink-600',
    color: 'bg-purple-500',
  },
]

export default function UnifiedLoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStoreV2()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [currentSlide, setCurrentSlide] = useState(0)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(schema),
    defaultValues: { remember_me: false },
  })

  // Auto-rotate slides every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

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
            navigate('/dashboard')
        }
      }, 300)
    } catch (error: any) {
      // Silent error handling - no toast
      console.error('Login failed:', error)
      setIsLoading(false)
    }
  }

  const slide = slides[currentSlide]

  return (
    <div className="min-h-screen flex bg-white">
      {/* Left Slideshow Section */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {slides.map((s, idx) => (
          <div
            key={s.id}
            className={`absolute inset-0 bg-gradient-to-br ${s.bgGradient} transition-opacity duration-1000 ${
              idx === currentSlide ? 'opacity-100' : 'opacity-0'
            }`}
          >
            {/* Animated background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-10 left-10 w-40 h-40 bg-white rounded-full blur-3xl"></div>
              <div className="absolute bottom-10 right-10 w-40 h-40 bg-white rounded-full blur-3xl"></div>
            </div>

            {/* Content */}
            <div className="relative h-full flex flex-col items-center justify-center text-white px-8 text-center">
              <div className="mb-6 transform transition-transform duration-500 hover:scale-110">
                {s.icon}
              </div>
              <h2 className="text-5xl font-bold mb-2">{s.title}</h2>
              <p className="text-xl font-semibold mb-4 opacity-90">{s.subtitle}</p>
              <p className="text-lg opacity-80 max-w-sm">{s.description}</p>
            </div>
          </div>
        ))}

        {/* Slide Indicators */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-2 z-10">
          {slides.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentSlide(idx)}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                idx === currentSlide
                  ? 'bg-white w-8'
                  : 'bg-white/50 hover:bg-white/75'
              }`}
              aria-label={`Go to slide ${idx + 1}`}
            />
          ))}
        </div>
      </div>

      {/* Right Login Form Section */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Logo/Header */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome Back</h1>
            <p className="text-slate-600">Sign in to your account to continue</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                {...register('email')}
                className={`w-full px-4 py-2.5 rounded-lg border transition-colors ${
                  errors.email
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-slate-300 focus:ring-indigo-500'
                } focus:outline-none focus:ring-2 focus:border-transparent`}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  {...register('password')}
                  className={`w-full px-4 py-2.5 rounded-lg border transition-colors ${
                    errors.password
                      ? 'border-red-500 focus:ring-red-500'
                      : 'border-slate-300 focus:ring-indigo-500'
                  } focus:outline-none focus:ring-2 focus:border-transparent`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-slate-700"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                {...register('remember_me')}
                className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-slate-600">
                Remember me
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="mt-6 text-center space-y-2">
            <a href="/forgot-password" className="text-sm text-indigo-600 hover:text-indigo-700 block">
              Forgot your password?
            </a>
            <p className="text-sm text-slate-600">
              Don't have an account?{' '}
              <a href="/register-owner" className="text-indigo-600 hover:text-indigo-700 font-medium">
                Register here
              </a>
            </p>
          </div>

          {/* Mobile Slide Info */}
          <div className="lg:hidden mt-8 p-4 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border border-indigo-200">
            <div className="flex items-center gap-3 mb-2">
              {slide.icon}
              <div>
                <h3 className="font-semibold text-slate-900">{slide.title}</h3>
                <p className="text-sm text-slate-600">{slide.subtitle}</p>
              </div>
            </div>
            <p className="text-sm text-slate-600">{slide.description}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
