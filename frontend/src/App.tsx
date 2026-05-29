import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { TripProvider } from './contexts/TripContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AppLayout } from './components/AppLayout'
import { ThreeDProvider } from './components/ThreeDProvider'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProfilePage } from './pages/ProfilePage'
import { OfferRidePage } from './pages/OfferRidePage'
import { MyOffersPage } from './pages/MyOffersPage'
import { FindRidePage } from './pages/FindRidePage'
import { RequestStatusPage } from './pages/RequestStatusPage'
import { OfferInboxPage } from './pages/OfferInboxPage'
import { DriverInboxPage } from './pages/DriverInboxPage'

function App() {
  return (
    <AuthProvider>
      <TripProvider>
        <ThreeDProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/offer-ride" element={<OfferRidePage />} />
                <Route path="/my-offers" element={<MyOffersPage />} />
                <Route
                  path="/my-offers/:offerId/requests"
                  element={<OfferInboxPage />}
                />
                <Route path="/driver-inbox" element={<DriverInboxPage />} />
                <Route path="/find-ride" element={<FindRidePage />} />
                <Route path="/requests/:id" element={<RequestStatusPage />} />
              </Route>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </ThreeDProvider>
      </TripProvider>
    </AuthProvider>
  );
}

export default App