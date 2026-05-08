import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface Holiday {
  date: string // YYYY-MM-DD
  name: string
  type: 'national' | 'state' | 'religious' | 'optional'
}

interface HolidayCalendarProps {
  holidays?: Holiday[]
  onDateSelect?: (date: string) => void
}

// Default Indian holidays for 2026
const DEFAULT_HOLIDAYS: Holiday[] = [
  { date: '2026-01-26', name: 'Republic Day', type: 'national' },
  { date: '2026-03-08', name: 'Maha Shivaratri', type: 'religious' },
  { date: '2026-03-25', name: 'Holi', type: 'religious' },
  { date: '2026-03-29', name: 'Good Friday', type: 'religious' },
  { date: '2026-04-02', name: 'Eid ul-Fitr', type: 'religious' },
  { date: '2026-04-10', name: 'Eid ul-Adha', type: 'religious' },
  { date: '2026-04-14', name: 'Ambedkar Jayanti', type: 'national' },
  { date: '2026-05-01', name: 'May Day', type: 'national' },
  { date: '2026-08-15', name: 'Independence Day', type: 'national' },
  { date: '2026-08-29', name: 'Janmashtami', type: 'religious' },
  { date: '2026-09-16', name: 'Milad un-Nabi', type: 'religious' },
  { date: '2026-10-02', name: 'Gandhi Jayanti', type: 'national' },
  { date: '2026-10-03', name: 'Dussehra', type: 'religious' },
  { date: '2026-10-24', name: 'Diwali', type: 'religious' },
  { date: '2026-10-25', name: 'Govardhan Puja', type: 'religious' },
  { date: '2026-11-01', name: 'Bhai Dooj', type: 'religious' },
  { date: '2026-12-25', name: 'Christmas', type: 'religious' },
]

export default function HolidayCalendar({ holidays = DEFAULT_HOLIDAYS, onDateSelect }: HolidayCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  // Get first day of month and number of days
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  // Create holiday map for quick lookup
  const holidayMap = new Map(holidays.map(h => [h.date, h]))

  // Get holiday for a specific date
  const getHolidayForDate = (y: number, m: number, d: number): Holiday | undefined => {
    const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    return holidayMap.get(dateStr)
  }

  // Generate calendar days
  const calendarDays = []

  // Previous month days
  for (let i = daysInPrevMonth - firstDay + 1; i <= daysInPrevMonth; i++) {
    calendarDays.push({ day: i, isCurrentMonth: false, date: '' })
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    calendarDays.push({ day: i, isCurrentMonth: true, date: dateStr })
  }

  // Next month days
  const remainingDays = 42 - calendarDays.length
  for (let i = 1; i <= remainingDays; i++) {
    calendarDays.push({ day: i, isCurrentMonth: false, date: '' })
  }

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const handleDateClick = (date: string) => {
    setSelectedDate(date)
    onDateSelect?.(date)
  }

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  // Get holidays for current month
  const currentMonthHolidays = holidays.filter(h => {
    const [y, m] = h.date.split('-')
    return parseInt(y) === year && parseInt(m) === month + 1
  })

  // Get all holidays for the year
  const allYearHolidays = holidays.filter(h => {
    const [y] = h.date.split('-')
    return parseInt(y) === year
  })

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'national':
        return 'bg-orange-100 text-orange-800 border-l-4 border-orange-500'
      case 'religious':
        return 'bg-purple-100 text-purple-800 border-l-4 border-purple-500'
      case 'state':
        return 'bg-blue-100 text-blue-800 border-l-4 border-blue-500'
      case 'optional':
        return 'bg-gray-100 text-gray-800 border-l-4 border-gray-500'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Calendar - Main Section */}
        <div className="lg:col-span-2">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">{monthName}</h2>
            <div className="flex gap-2">
              <button
                onClick={handlePrevMonth}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Previous month"
              >
                <ChevronLeft size={20} className="text-slate-600" />
              </button>
              <button
                onClick={handleNextMonth}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Next month"
              >
                <ChevronRight size={20} className="text-slate-600" />
              </button>
            </div>
          </div>

          {/* Weekday Headers */}
          <div className="grid grid-cols-7 gap-1 mb-2 bg-slate-100 rounded-lg p-2">
            {weekDays.map(day => (
              <div key={day} className="text-center font-bold text-slate-700 py-2 text-sm">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid - All Dates Visible */}
          <div className="grid grid-cols-7 gap-1 bg-slate-50 p-2 rounded-lg">
            {calendarDays.map((dayObj, idx) => {
              const holiday = dayObj.isCurrentMonth ? getHolidayForDate(year, month, dayObj.day) : undefined
              const isToday = dayObj.isCurrentMonth && new Date().toDateString() === new Date(year, month, dayObj.day).toDateString()
              const isSelected = dayObj.date === selectedDate
              const dayOfWeek = idx % 7 // 0 = Sunday, 6 = Saturday
              const isWeekend = dayOfWeek === 0 || dayOfWeek === 6 // Sunday or Saturday

              return (
                <button
                  key={idx}
                  onClick={() => dayObj.isCurrentMonth && dayObj.date && handleDateClick(dayObj.date)}
                  disabled={!dayObj.isCurrentMonth}
                  className={`aspect-square p-1 rounded text-xs font-semibold transition-all flex flex-col items-center justify-center ${
                    !dayObj.isCurrentMonth
                      ? 'text-slate-300 bg-transparent cursor-default'
                      : holiday
                      ? 'bg-orange-400 text-white hover:bg-orange-500 cursor-pointer shadow-md border-2 border-orange-500'
                      : isToday
                      ? 'bg-indigo-100 text-indigo-900 border-2 border-indigo-500 font-bold'
                      : isSelected
                      ? 'bg-indigo-500 text-white border-2 border-indigo-600'
                      : isWeekend
                      ? 'bg-yellow-100 text-slate-900 hover:bg-yellow-200 cursor-pointer border border-yellow-300'
                      : 'bg-white text-slate-900 hover:bg-slate-100 cursor-pointer border border-slate-200'
                  }`}
                  title={holiday ? holiday.name : ''}
                >
                  <span className="text-xs">{dayObj.day}</span>
                  {holiday && <span className="text-xs leading-none">🎉</span>}
                </button>
              )
            })}
          </div>

          {/* Legend */}
          <div className="mt-6 pt-6 border-t border-slate-200">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Legend</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-orange-400 rounded text-white text-xs flex items-center justify-center">🎉</div>
                <span className="text-sm text-slate-600">Holiday</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-indigo-100 border-2 border-indigo-500 rounded"></div>
                <span className="text-sm text-slate-600">Today</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-yellow-100 border border-yellow-300 rounded"></div>
                <span className="text-sm text-slate-600">Weekend</span>
              </div>
            </div>
          </div>
        </div>

        {/* Holidays List - Right Section */}
        <div className="lg:col-span-2">
          {/* Current Month Holidays */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
              <span className="text-2xl">📅</span>
              Holidays in {monthName}
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
              {currentMonthHolidays.length > 0 ? (
                currentMonthHolidays.map(holiday => (
                  <div
                    key={holiday.date}
                    className={`p-3 rounded-lg cursor-pointer transition-all hover:shadow-lg ${getTypeColor(holiday.type)}`}
                    onClick={() => handleDateClick(holiday.date)}
                  >
                    <div className="font-bold text-sm">{holiday.name}</div>
                    <div className="text-xs opacity-75 mt-1">
                      {new Date(holiday.date).toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                    <div className="text-xs opacity-60 capitalize mt-1 font-semibold">{holiday.type}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-500 bg-slate-50 rounded-lg">
                  <p className="text-sm">No holidays this month</p>
                </div>
              )}
            </div>
          </div>

          {/* All Year Holidays Summary */}
          <div className="border-t border-slate-200 pt-6">
            <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <span className="text-lg">📊</span>
              Holiday Summary ({year})
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between p-2 bg-orange-50 rounded">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                  <span className="text-slate-700 font-medium">National</span>
                </div>
                <span className="font-bold text-orange-700">{holidays.filter(h => h.type === 'national').length}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-purple-50 rounded">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span className="text-slate-700 font-medium">Religious</span>
                </div>
                <span className="font-bold text-purple-700">{holidays.filter(h => h.type === 'religious').length}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-slate-700 font-medium">State</span>
                </div>
                <span className="font-bold text-blue-700">{holidays.filter(h => h.type === 'state').length}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                  <span className="text-slate-700 font-medium">Optional</span>
                </div>
                <span className="font-bold text-gray-700">{holidays.filter(h => h.type === 'optional').length}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-slate-100 rounded border-2 border-slate-300 mt-2">
                <span className="text-slate-900 font-bold">Total Holidays</span>
                <span className="font-bold text-lg text-slate-900">{allYearHolidays.length}</span>
              </div>
            </div>
          </div>

          {/* All Holidays List */}
          <div className="border-t border-slate-200 pt-6 mt-6">
            <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <span className="text-lg">📋</span>
              All Holidays ({year})
            </h4>
            <div className="space-y-1 max-h-48 overflow-y-auto pr-2">
              {allYearHolidays.map(holiday => (
                <div
                  key={holiday.date}
                  className="p-2 rounded text-xs cursor-pointer transition-all hover:shadow-md"
                  onClick={() => handleDateClick(holiday.date)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900">{holiday.name}</span>
                    <span className="text-slate-500">
                      {new Date(holiday.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 capitalize">{holiday.type}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
