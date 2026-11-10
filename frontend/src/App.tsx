import { Navigate, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Cadastro from './pages/Cadastro'
import Painel from './pages/Painel.tsx'
import Upload from './pages/Upload'
import Resultado from './pages/Resultado'
import Historico from './pages/Historico'
import Perfil from './pages/Perfil'
import './App.css'
import RotaProtegida from './components/auth/RotaProtegida'
import Layout from './components/layout/Layout'

function App() {
  return (
    <Routes>
      {/* Páginas públicas */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/cadastro" element={<Cadastro />} />

      {/* Área interna da plataforma */}
      <Route element={<RotaProtegida />}>
        <Route element={<Layout />}>
          <Route path="/painel" element={<Painel />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/resultado/:id" element={<Resultado />} />
          <Route path="/historico" element={<Historico />} />
          <Route path="/perfil" element={<Perfil />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App