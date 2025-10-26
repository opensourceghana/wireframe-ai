import { Zap } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                AI Wireframing Tool
              </h1>
              <p className="text-sm text-gray-500">
                Generate wireframes with AI
              </p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            v1.0.0
          </div>
        </div>
      </div>
    </header>
  )
}
