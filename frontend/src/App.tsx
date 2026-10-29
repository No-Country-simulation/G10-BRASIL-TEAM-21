import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './componentes/Layout'
import Login from './paginas/Login'
import Cadastro from './paginas/Cadastro'
import Upload from './paginas/Upload'
import Resultado from './paginas/Resultado'
import Historico from './paginas/Historico'
import Perfil from './paginas/Perfil'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/cadastro" element={<Cadastro />} />

      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/resultado/:id" element={<Resultado />} />
        <Route path="/historico" element={<Historico />} />
        <Route path="/perfil" element={<Perfil />} />
        <Route path="*" element={<Navigate to="/upload" replace />} />
      </Route>
    </Routes>
  )
}

export default App
