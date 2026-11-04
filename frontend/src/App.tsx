import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Cadastro from './pages/Cadastro'
import Upload from './pages/Upload'
import Resultado from './pages/Resultado'
import Historico from './pages/Historico'
import Perfil from './pages/Perfil'
import './App.css'

function App() {
  return (
    <Routes>
      {/* Páginas públicas */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/cadastro" element={<Cadastro />} />

      {/* Área interna da plataforma */}
      <Route element={<Layout />}>
        <Route path="/upload" element={<Upload />} />
        <Route path="/resultado/:id" element={<Resultado />} />
        <Route path="/historico" element={<Historico />} />
        <Route path="/perfil" element={<Perfil />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App