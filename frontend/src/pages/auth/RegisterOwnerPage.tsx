import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { authV2Api } from '@/api/authV2'

const schema = z.object({
  first_name: z.string().min(2, 'First name is required'),
  last_name: z.string().min(2, 'Last name is required'),
  company_name: z.string().min(2, 'Company name is required'),
  company_code: z.string()
    .min(3, 'At least 3 characters')
    .max(30)
    .regex(/^[A-Z0-9-]+$/, 'Only uppercase letters, numbers, and hyphens'),
  email: z.string().email('Enter a valid email'),
  phone: z.string().min(10, 'Enter a valid phone number'),
  password: z.string()
    .min(8, 'Minimum 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirm_password: z.string(),
}).refine(d => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

const steps = ['Firm Details', 'Contact & Login']

type RegisterFormData = z.infer<typeof schema>

export default function RegisterOwnerPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [showPw, setShowPw] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [done, setDone] = useState(false)

  const { register, handleSubmit, trigger, watch, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(schema),
    mode: 'onBlur',
  })

  const companyName = watch('company_name', '')
  const companyCode = watch('company_code', '')

  const nextStep = async () => {
    const valid = await trigger(['first_name', 'last_name', 'company_name', 'company_code'])
    if (valid) setStep(1)
  }

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    try {
      await authV2Api.registerOwner({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        password: data.password,
        company_name: data.company_name,
        company_code: data.company_code,
      })
      setDone(true)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      toast.error(detail || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="text-green-600" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Registration Successful!</h2>
          <p className="text-slate-500 mb-6">
            Welcome to CA Assists! Your account has been created. Please log in to get started.
          </p>
          <button onClick={() => navigate('/login')} className="btn-primary btn-lg w-full">
            Go to Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex">
      {/* Left */}
      <div className="hidden lg:flex lg:w-5/12 bg-brand-800 flex-col justify-between p-12">
        <div>
          <div className="flex items-center gap-3 mb-10">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
              <span className="text-brand-800 font-bold text-lg">CA</span>
            </div>
            <span className="text-white text-xl font-bold">CA Assists</span>
          </div>
          <h1 className="text-white text-3xl font-bold leading-snug mb-3">
            Start your CA practice today
          </h1>
          <p className="text-brand-200 text-base">
            Complete suite for GST filing, ITR preparation, and client management.
          </p>
        </div>
        <div className="bg-brand-900 rounded-2xl p-6 space-y-3">
          {['GST & ITR Filing Automation', 'Task & Deadline Tracking', 'Client Document Vault',
            'Team Collaboration', 'Multi-branch Support', 'Bank-grade Security'].map(f => (
            <div key={f} className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-400 flex-shrink-0" />
              <span className="text-brand-100 text-sm">{f}</span>
            </div>
          ))}
        </div>
        <p className="text-brand-400 text-xs">
          Already have an account?{' '}
          <Link to="/login" className="text-white underline">Sign in</Link>
        </p>
      </div>

      {/* Right */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-slate-50">
        <div className="w-full max-w-lg">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-6 lg:hidden">
            <div className="w-8 h-8 bg-brand-800 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CA</span>
            </div>
            <span className="text-brand-800 font-bold text-lg">CA Assists</span>
          </div>

          {/* Step indicator */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-1">
              {steps.map((s, i) => (
                <div key={s} className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-colors
                    ${i <= step ? 'bg-brand-800 text-white' : 'bg-slate-200 text-slate-500'}`}>
                    {i < step ? '✓' : i + 1}
                  </div>
                  <span className={`text-sm font-medium ${i === step ? 'text-slate-900' : 'text-slate-400'}`}>{s}</span>
                  {i < steps.length - 1 && <div className={`h-px w-8 ${i < step ? 'bg-brand-800' : 'bg-slate-200'}`} />}
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Step 0: Firm Details */}
            {step === 0 && (
              <>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Your Firm Details</h2>
                  <p className="text-slate-500 text-sm mt-1">Tell us about your CA practice</p>
                </div>

                <div>
                  <label className="label">First Name *</label>
                  <input {...register('first_name')} placeholder="John" className={`input ${errors.first_name ? 'input-error' : ''}`} />
                  {errors.first_name && <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>}
                </div>

                <div>
                  <label className="label">Last Name *</label>
                  <input {...register('last_name')} placeholder="Doe" className={`input ${errors.last_name ? 'input-error' : ''}`} />
                  {errors.last_name && <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>}
                </div>

                <div>
                  <label className="label">Firm Name *</label>
                  <input {...register('company_name')} placeholder="e.g. Sharma & Associates" className={`input ${errors.company_name ? 'input-error' : ''}`} />
                  {errors.company_name && <p className="mt-1 text-xs text-red-600">{errors.company_name.message}</p>}
                </div>

                <div>
                  <label className="label">Firm Code *
                    <span className="ml-1 text-slate-400 font-normal">(unique identifier)</span>
                  </label>
                  <input
                    {...register('company_code')}
                    placeholder="ABC001"
                    className={`input ${errors.company_code ? 'input-error' : ''}`}
                  />
                  {errors.company_code
                    ? <p className="mt-1 text-xs text-red-600">{errors.company_code.message}</p>
                    : companyCode && <p className="mt-1 text-xs text-green-600">✓ {companyCode}</p>
                  }
                </div>

                <button type="button" onClick={nextStep} className="btn-primary w-full btn-lg">
                  Next: Contact & Login
                </button>
              </>
            )}

            {/* Step 1: Contact & Login */}
            {step === 1 && (
              <>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Contact & Login Details</h2>
                  <p className="text-slate-500 text-sm mt-1">Set up your login credentials</p>
                </div>

                <div>
                  <label className="label">Email Address *</label>
                  <input {...register('email')} type="email" placeholder="ca@yourfirm.com" className={`input ${errors.email ? 'input-error' : ''}`} />
                  {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
                </div>

                <div>
                  <label className="label">Mobile Number *</label>
                  <input {...register('phone')} type="tel" placeholder="9876543210" className={`input ${errors.phone ? 'input-error' : ''}`} />
                  {errors.phone && <p className="mt-1 text-xs text-red-600">{errors.phone.message}</p>}
                </div>

                <div>
                  <label className="label">Password *</label>
                  <div className="relative">
                    <input
                      {...register('password')}
                      type={showPw ? 'text' : 'password'}
                      placeholder="Min 8 chars with uppercase & number"
                      className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
                    />
                    <button type="button" onClick={() => setShowPw(!showPw)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                      {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
                </div>

                <div>
                  <label className="label">Confirm Password *</label>
                  <input {...register('confirm_password')} type="password" placeholder="••••••••"
                    className={`input ${errors.confirm_password ? 'input-error' : ''}`} />
                  {errors.confirm_password && <p className="mt-1 text-xs text-red-600">{errors.confirm_password.message}</p>}
                </div>

                <div className="flex gap-3">
                  <button type="button" onClick={() => setStep(0)} className="btn-secondary flex-1">
                    Back
                  </button>
                  <button type="submit" disabled={isLoading} className="btn-primary flex-1 btn-lg">
                    {isLoading ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : 'Create Account'}
                  </button>
                </div>

                <p className="text-center text-xs text-slate-400">
                  By registering, you agree to our{' '}
                  <a href="#" className="underline">Terms</a> and{' '}
                  <a href="#" className="underline">Privacy Policy</a>
                </p>
              </>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
