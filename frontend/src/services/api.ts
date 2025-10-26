import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for AI generation
})

export interface WireframeRequest {
  prompt: string
  style: string
  width: number
  height: number
  num_inference_steps: number
  guidance_scale: number
}

export interface WireframeResponse {
  image_base64: string
  svg_code: string
  generation_time: number
}

export interface WireframeStyle {
  id: string
  name: string
  description: string
}

export const generateWireframe = async (request: WireframeRequest): Promise<WireframeResponse> => {
  try {
    const response = await api.post<WireframeResponse>('/generate-wireframe', request)
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw new Error('Failed to generate wireframe')
  }
}

export const getWireframeStyles = async (): Promise<{ styles: WireframeStyle[] }> => {
  try {
    const response = await api.get<{ styles: WireframeStyle[] }>('/wireframe-styles')
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw new Error('Failed to fetch wireframe styles')
  }
}

export const checkHealth = async (): Promise<{ status: string; device: string; torch_available: string }> => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw new Error('Failed to check API health')
  }
}
