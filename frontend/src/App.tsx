import { Routes, Route } from 'react-router-dom'
import CalendarPage from './pages/CalendarPage'
import BookPage from './pages/BookPage'
import SuccessPage from './pages/SuccessPage'
import AdminPage from './pages/AdminPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<CalendarPage />} />
      <Route path="/book" element={<BookPage />} />
      <Route path="/success" element={<SuccessPage />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  )
}

export default App
