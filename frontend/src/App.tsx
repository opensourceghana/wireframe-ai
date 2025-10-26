import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import WireframeGenerator from './components/WireframeGenerator'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <WireframeGenerator />
      </main>
      <Toaster position="top-right" />
    </div>
  )
}

export default App
