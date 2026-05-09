import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from '@/components/layout/AppLayout'
import { ProtectedRoute, PublicRoute } from '@/components/auth/ProtectedRoute'

// Auth Pages
import LandingPage from '@/pages/auth/LandingPage'
import LoginPage from '@/pages/auth/LoginPage'
import LoginPageV2 from '@/pages/auth/LoginPageV2'
import UnifiedLoginPage from '@/pages/auth/UnifiedLoginPage'
import RegisterOwnerPage from '@/pages/auth/RegisterOwnerPage'
import ClientLoginPage from '@/pages/auth/ClientLoginPage'
import EmployeeLoginPage from '@/pages/auth/EmployeeLoginPage'
import ManagerLoginPage from '@/pages/auth/ManagerLoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import { ForgotPasswordPage, ResetPasswordPage } from '@/pages/auth/PasswordPages'
import AcceptInvitePage from '@/pages/auth/AcceptInvitePage'

// Dashboards
import DashboardPage from '@/pages/DashboardPage'
import DashboardUnified from '@/pages/DashboardUnified'
import OwnerDashboard from '@/pages/owner/OwnerDashboard'
import ManagerDashboard from '@/pages/manager/ManagerDashboard'
import EmployeeDashboardV2 from '@/pages/employee/EmployeeDashboardV2'
import ClientDashboardV2 from '@/pages/client/ClientDashboardV2'
import ClientDashboard from '@/pages/client/ClientDashboard'
import ClientTasksPage from '@/pages/client/ClientTasksPage'
import EmployeeDashboard from '@/pages/employee/EmployeeDashboard'
import EmployeeTasksPage from '@/pages/employee/EmployeeTasksPage'

// Management Pages
import UsersPage from '@/pages/UsersPage'
import BranchesPage from '@/pages/BranchesPage'
import CustomersPage from '@/pages/customers/CustomersPage'
import OwnerClientsPage from '@/pages/owner/OwnerClientsPage'
import OwnerEmployeesPage from '@/pages/owner/OwnerEmployeesPage'
import OwnerCompanyPage from '@/pages/owner/OwnerCompanyPage'
import OwnerBranchPage from '@/pages/owner/OwnerBranchPage'
import DocumentRequestsPage from '@/pages/owner/DocumentRequestsPage'
import ManagerClientsPage from '@/pages/manager/ManagerClientsPage'
import EmployeeClientsPage from '@/pages/employee/EmployeeClientsPage'
import EnquiriesPage from '@/pages/enquiries/EnquiriesPage'
import TasksPage from '@/pages/tasks/TasksPage'
import BillingPage from '@/pages/billing/BillingPage'
import SubscriptionPage from '@/pages/subscription/SubscriptionPage'
import PlansPage from '@/pages/subscription/PlansPage'
import { SubscriptionSuccessPage, SubscriptionCancelPage } from '@/pages/subscription/StripeCallbacks'
import {
  GSTPage, ITRPage, PortfolioPage,
  RolesPage, SettingsPage, ProfilePage, SecurityPage, NotFoundPage,
} from '@/pages/PlaceholderPages'

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<PublicRoute><Navigate to="/login" replace /></PublicRoute>} />
      <Route path="/login" element={<PublicRoute><UnifiedLoginPage /></PublicRoute>} />
      <Route path="/register-owner" element={<PublicRoute><RegisterOwnerPage /></PublicRoute>} />
      <Route path="/manager/login" element={<PublicRoute><ManagerLoginPage /></PublicRoute>} />
      <Route path="/client/login" element={<PublicRoute><ClientLoginPage /></PublicRoute>} />
      <Route path="/employee/login" element={<PublicRoute><EmployeeLoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />
      <Route path="/reset-password" element={<PublicRoute><ResetPasswordPage /></PublicRoute>} />
      <Route path="/accept-invite" element={<AcceptInvitePage />} />

      {/* Protected Routes with AppLayout as parent */}
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        {/* Stripe Callbacks */}
        <Route path="/subscription/success" element={<SubscriptionSuccessPage />} />
        <Route path="/subscription/cancel" element={<SubscriptionCancelPage />} />

        {/* Dashboards */}
        <Route path="/owner/dashboard" element={<OwnerDashboard />} />
        <Route path="/manager/dashboard" element={<ManagerDashboard />} />
        <Route path="/employee/dashboard" element={<EmployeeDashboardV2 />} />
        <Route path="/client/dashboard" element={<ClientDashboardV2 />} />
        <Route path="/client/tasks" element={<ClientTasksPage />} />
        <Route path="/employee/tasks" element={<EmployeeTasksPage />} />
        
        {/* Main Pages */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/dashboard-unified" element={<DashboardUnified />} />
        
        {/* Management Pages */}
        <Route path="/users" element={<UsersPage />} />
        <Route path="/branches" element={<BranchesPage />} />
        <Route path="/clients" element={<CustomersPage />} />
        
        {/* Role-Specific Client Pages */}
        <Route path="/owner/clients" element={<OwnerClientsPage />} />
        <Route path="/manager/clients" element={<ManagerClientsPage />} />
        <Route path="/employee/clients" element={<EmployeeClientsPage />} />
        
        {/* Role-Specific Employee Pages */}
        <Route path="/owner/employees" element={<OwnerEmployeesPage />} />
        
        {/* Owner Company and Branch Pages */}
        <Route path="/owner/company" element={<OwnerCompanyPage />} />
        <Route path="/owner/branch" element={<OwnerBranchPage />} />
        <Route path="/owner/document-requests" element={<DocumentRequestsPage />} />
        
        <Route path="/enquiries" element={<EnquiriesPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/billing" element={<BillingPage />} />
        <Route path="/subscription" element={<SubscriptionPage />} />
        <Route path="/subscription/plans" element={<PlansPage />} />
        <Route path="/gst" element={<GSTPage />} />
        <Route path="/itr" element={<ITRPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/roles" element={<RolesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/security" element={<SecurityPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
