//components/Header.jsx
import { Shield } from 'lucide-react'

export default function Header() {
	return (
		<div className="text-center mb-8">
			<div className="flex items-center justify-center mb-4">
				<Shield className="h-12 w-12 text-blue-600 mr-3" />
				<h1 className="text-4xl font-bold text-gray-900">PII Guardian</h1>
			</div>
			<p className="text-lg text-gray-600 max-w-2xl mx-auto">
				Advanced AI-powered system to detect and mask Personally Identifiable Information in images
			</p>
		</div>
	)
} 