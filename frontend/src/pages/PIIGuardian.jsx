//pages/PIIGuardian.jsx
import React, { useState, useCallback } from 'react'
import { Upload, Download, Shield, Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { detectPii, maskPii } from '../services/api'
import Header from '../components/Header'

export default function PIIGuardian() {
	const [selectedFile, setSelectedFile] = useState(null)
	const [originalImage, setOriginalImage] = useState(null)
	const [maskedImage, setMaskedImage] = useState(null)
	const [isProcessing, setIsProcessing] = useState(false)
	const [detectedPII, setDetectedPII] = useState([])
	const [showOriginal, setShowOriginal] = useState(true)
	const [dragOver, setDragOver] = useState(false)

	const handleFileSelect = useCallback((file) => {
		if (file && file.type.startsWith('image/')) {
			setSelectedFile(file)
			const reader = new FileReader()
			reader.onload = (e) => {
				setOriginalImage(e.target.result)
				setMaskedImage(null)
				setDetectedPII([])
			}
			reader.readAsDataURL(file)
		}
	}, [])

	const handleDrop = useCallback((e) => {
		e.preventDefault()
		setDragOver(false)
		const files = Array.from(e.dataTransfer.files)
		if (files.length > 0) {
			handleFileSelect(files[0])
		}
	}, [handleFileSelect])

	const handleDragOver = useCallback((e) => {
		e.preventDefault()
		setDragOver(true)
	}, [])

	const handleDragLeave = useCallback((e) => {
		e.preventDefault()
		setDragOver(false)
	}, [])

	const processImage = async () => {
		if (!selectedFile) return
		setIsProcessing(true)
		try {
			const [piiResp, maskResp] = await Promise.all([
				detectPii(selectedFile),
				maskPii(selectedFile)
			])
			const mapped = (piiResp?.detected_pii || []).map((e) => ({
				type: e.entity_type,
				text: e.text,
				confidence: e.confidence,
				bbox: e.coordinates || [0, 0, 0, 0],
			}))
			setDetectedPII(mapped)
			if (maskResp?.image_base64) {
				setMaskedImage(`data:image/png;base64,${maskResp.image_base64}`)
			} else {
				setMaskedImage(null)
			}
		} catch (error) {
			console.error('Error processing image:', error)
			setMaskedImage(null)
			setDetectedPII([])
		} finally {
			setIsProcessing(false)
		}
	}

	const downloadMaskedImage = () => {
		if (maskedImage) {
			const link = document.createElement('a')
			link.href = maskedImage
			link.download = 'masked_image.png'
			document.body.appendChild(link)
			link.click()
			document.body.removeChild(link)
		}
	}

	const getPIITypeColor = (type) => {
		const colors = {
			'PERSON': 'bg-blue-100 text-blue-800',
			// Backend custom entities
			'AADHAAR_NUMBER': 'bg-red-100 text-red-800',
			'PAN_NUMBER': 'bg-rose-100 text-rose-800',
			'PHONE_NUMBER': 'bg-green-100 text-green-800',
			'EMAIL': 'bg-purple-100 text-purple-800',
			'DATE_OF_BIRTH': 'bg-amber-100 text-amber-800',
			'PIN_CODE': 'bg-yellow-100 text-yellow-800',
			'DRIVING_LICENSE': 'bg-indigo-100 text-indigo-800',
			'VOTER_ID': 'bg-teal-100 text-teal-800',
			// Common Presidio entities / aliases
			'EMAIL_ADDRESS': 'bg-purple-100 text-purple-800',
			'ADDRESS': 'bg-yellow-100 text-yellow-800',
			'AADHAAR': 'bg-red-100 text-red-800',
			'INDIAN_PHONE': 'bg-green-100 text-green-800',
			'PAN': 'bg-rose-100 text-rose-800',
			'US_SSN': 'bg-red-100 text-red-800',
		}
		return colors[type] || 'bg-gray-100 text-gray-800'
	}

	return (
		<div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
			<div className="max-w-6xl mx-auto">
				<Header />

				<div className="grid lg:grid-cols-2 gap-8">
					<div className="space-y-6">
						<div className="bg-white rounded-xl shadow-lg p-6 min-h-[32rem] flex flex-col">
							<h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
								<Upload className="h-6 w-6 mr-2 text-blue-600" />
								Upload Document
							</h2>
							<div
								className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
									dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
								}`}
								onDrop={handleDrop}
								onDragOver={handleDragOver}
								onDragLeave={handleDragLeave}
							>
								<div className="space-y-4">
									<div className="flex justify-center">
										<Upload className="h-16 w-16 text-gray-400" />
									</div>
									<div>
										<p className="text-lg font-medium text-gray-700">Drop your image here or click to browse</p>
										<p className="text-sm text-gray-500">Supports JPG, PNG, JPEG files up to 10MB</p>
									</div>
									<input type="file" accept="image/*" onChange={(e) => handleFileSelect(e.target.files[0])} className="hidden" id="file-upload" />
									<label htmlFor="file-upload" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">Choose File</label>
								</div>
							</div>
							{selectedFile && (
								<div className="mt-4 p-4 bg-gray-50 rounded-lg">
									<p className="text-sm font-medium text-gray-700">Selected File:</p>
									<p className="text-sm text-gray-600">{selectedFile.name}</p>
									<p className="text-xs text-gray-500">Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
								</div>
							)}
							<button onClick={processImage} disabled={!selectedFile || isProcessing} className="w-full mt-6 flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all">
								{isProcessing ? (<><Loader2 className="animate-spin h-5 w-5 mr-2" />Processing...</>) : (<><Shield className="h-5 w-5 mr-2" />Detect & Mask PII</>)}
							</button>
						</div>

						{detectedPII.length > 0 && (
							<div className="bg-white rounded-xl shadow-lg p-6">
								<h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
									<AlertCircle className="h-5 w-5 mr-2 text-orange-600" />Detected PII ({detectedPII.length} items)
								</h3>
								<div className="space-y-3">
									{detectedPII.map((pii, index) => (
										<div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
											<div className="flex items-center space-x-3">
												<span className={`px-2 py-1 text-xs font-medium rounded ${getPIITypeColor(pii.type)}`}>{pii.type}</span>
												<span className="font-mono text-sm text-gray-600 line-through">{pii.text}</span>
											</div>
											<div className="flex items-center space-x-2">
												<span className="text-xs text-gray-500">{Math.round(pii.confidence * 100)}% confidence</span>
												<CheckCircle className="h-4 w-4 text-green-600" />
											</div>
										</div>
									))}
								</div>
							</div>
						)}
					</div>

					<div className="space-y-6">
						<div className="bg-white rounded-xl shadow-lg p-6 min-h-[32rem] flex flex-col">
							<div className="flex items-center justify-between mb-4">
								<h3 className="text-xl font-semibold text-gray-800">{showOriginal ? 'Original Image' : 'Masked Image'}</h3>
								<div className="flex items-center space-x-2">
									{maskedImage && (
										<>
											<button onClick={() => setShowOriginal(!showOriginal)} className="flex items-center px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
												{showOriginal ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
												{showOriginal ? 'Show Masked' : 'Show Original'}
											</button>
											<button onClick={downloadMaskedImage} className="flex items-center px-3 py-2 text-sm bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors">
												<Download className="h-4 w-4 mr-1" />Download
											</button>
										</>
									)}
								</div>
							</div>
							<div className="border-2 border-gray-200 rounded-lg overflow-hidden bg-gray-50 grow flex items-center justify-center">
								{originalImage ? (
									<img src={showOriginal ? originalImage : (maskedImage || originalImage)} alt={showOriginal ? 'Original document' : 'Masked document'} className="max-w-full max-h-96 object-contain" />
								) : (
									<div className="text-center text-gray-500">
										<div className="h-24 w-24 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
											<Shield className="h-12 w-12 text-gray-400" />
										</div>
										<p>Upload an image to get started</p>
									</div>
								)}
							</div>
							{maskedImage && (
								<div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
									<div className="flex items-center">
										<CheckCircle className="h-5 w-5 text-green-600 mr-2" />
										<span className="text-sm font-medium text-green-800">PII successfully detected and masked</span>
									</div>
									<p className="text-xs text-green-600 mt-1">The sensitive information has been securely redacted from the image</p>
								</div>
							)}
						</div>

						{/* Security features card removed here; a full-width section is rendered below */}
					</div>
				</div>
				{/* Full-width Security Features section */}
				<div className="mt-8">
					<div className="bg-white rounded-2xl shadow-lg p-8">
						<h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">Security Features</h3>
						<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
							<div className="rounded-xl border border-green-100 bg-green-50 p-4 flex items-start space-x-3">
								<CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
								<div>
									<p className="font-medium text-gray-800">Multi-model OCR</p>
									<p className="text-xs text-gray-600">Best-in-class accuracy</p>
								</div>
							</div>
							<div className="rounded-xl border border-blue-100 bg-blue-50 p-4 flex items-start space-x-3">
								<CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
								<div>
									<p className="font-medium text-gray-800">AI-driven NER</p>
									<p className="text-xs text-gray-600">Presidio + spaCy</p>
								</div>
							</div>
							<div className="rounded-xl border border-purple-100 bg-purple-50 p-4 flex items-start space-x-3">
								<CheckCircle className="h-5 w-5 text-purple-600 mt-0.5" />
								<div>
									<p className="font-medium text-gray-800">80+ Languages</p>
									<p className="text-xs text-gray-600">Global language support</p>
								</div>
							</div>
							<div className="rounded-xl border border-amber-100 bg-amber-50 p-4 flex items-start space-x-3">
								<CheckCircle className="h-5 w-5 text-amber-600 mt-0.5" />
								<div>
									<p className="font-medium text-gray-800">Privacy-first</p>
									<p className="text-xs text-gray-600">Enterprise-grade security</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	)
} 