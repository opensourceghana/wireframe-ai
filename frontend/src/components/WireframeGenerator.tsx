import { useState } from 'react'
import { Loader2, Download, Wand2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateWireframe } from '../services/api'

interface WireframeData {
  image_base64: string
  svg_code: string
  generation_time: number
}

export default function WireframeGenerator() {
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('low-fi')
  const [isLoading, setIsLoading] = useState(false)
  const [wireframe, setWireframe] = useState<WireframeData | null>(null)

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt')
      return
    }

    setIsLoading(true)
    try {
      const result = await generateWireframe({
        prompt: prompt.trim(),
        style,
        width: 512,
        height: 512,
        num_inference_steps: 20,
        guidance_scale: 7.5
      })
      
      setWireframe(result)
      toast.success(`Wireframe generated in ${result.generation_time.toFixed(2)}s`)
    } catch (error) {
      console.error('Generation error:', error)
      toast.error('Failed to generate wireframe')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadSVG = () => {
    if (!wireframe) return
    
    const blob = new Blob([wireframe.svg_code], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'wireframe.svg'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('SVG downloaded!')
  }

  const handleDownloadPNG = () => {
    if (!wireframe) return
    
    const a = document.createElement('a')
    a.href = `data:image/png;base64,${wireframe.image_base64}`
    a.download = 'wireframe.png'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    toast.success('PNG downloaded!')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Generate Wireframe
        </h2>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your wireframe
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Login page with email field, password field, remember me checkbox, and login button"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
          </div>

          <div>
            <label htmlFor="style" className="block text-sm font-medium text-gray-700 mb-2">
              Wireframe Style
            </label>
            <select
              id="style"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="low-fi">Low Fidelity</option>
              <option value="high-fi">High Fidelity</option>
              <option value="mobile">Mobile</option>
              <option value="web">Web</option>
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isLoading || !prompt.trim()}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Wand2 className="w-4 h-4 mr-2" />
            )}
            {isLoading ? 'Generating...' : 'Generate Wireframe'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {wireframe && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              Generated Wireframe
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={handleDownloadPNG}
                className="inline-flex items-center px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                <Download className="w-4 h-4 mr-1" />
                PNG
              </button>
              <button
                onClick={handleDownloadSVG}
                className="inline-flex items-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <Download className="w-4 h-4 mr-1" />
                SVG
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* PNG Preview */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">PNG Preview</h4>
              <div className="border rounded-lg p-4 bg-gray-50">
                <img
                  src={`data:image/png;base64,${wireframe.image_base64}`}
                  alt="Generated wireframe"
                  className="w-full h-auto rounded"
                />
              </div>
            </div>

            {/* SVG Preview */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">SVG Preview</h4>
              <div className="border rounded-lg p-4 bg-gray-50">
                <div
                  dangerouslySetInnerHTML={{ __html: wireframe.svg_code }}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            Generated in {wireframe.generation_time.toFixed(2)} seconds
          </div>
        </div>
      )}
    </div>
  )
}
