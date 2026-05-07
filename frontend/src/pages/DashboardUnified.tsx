import { useState } from 'react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { Calendar, LayoutGrid } from 'lucide-react'
import HolidayCalendar from '@/components/calendar/HolidayCalendar'

// Import role-specific dashboard components
import OwnerDashboard from './owner/OwnerDashboard'
import ManagerDashboard from './manager/ManagerDashboard'
import EmployeeDashboardV2 from './employee/EmployeeDashboardV2'
import ClientDashboardV2 from './client/ClientDashboardV2'

type ViewType = 'dashboard' | 'calendar'

export default function DashboardUnified() {
  const { user, company } = useAuthStoreV2()
  const [currentView, setCurrentView] = useState<ViewType>('calendar')

  if (!user || !company) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Render role-specific dashboard
  const renderDashboard = () => {
    switch (company.role) {
      case 'OWNER':
        return <OwnerDashboard />
      case 'MANAGER':
        return <ManagerDashboard />
      case 'EMPLOYEE':
        return <EmployeeDashboardV2 />
      case 'CLIENT':
        return <ClientDashboardV2 />
      default:
        return <OwnerDashboard />
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* View Toggle */}
      <div className="sticky top-0 z-40 bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'dashboard'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <LayoutGrid size={18} />
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('calendar')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'calendar'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <Calendar size={18} />
              Calendar
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {currentView === 'dashboard' ? (
          <div className="py-6">
            {renderDashboard()}
          </div>
        ) : (
          <div className="py-6">
            <HolidayCalendar />
          </div>
        )}
      </div>
    </div>
  )
}
