const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function detectPii(file) {
	const form = new FormData()
	form.append('file', file)
	const res = await fetch(`${BASE_URL}/detect`, {
		method: 'POST',
		body: form,
	})
	if (!res.ok) throw new Error(`detect failed: ${res.status}`)
	return res.json()
}

export async function maskPii(file, { style = 'box', asJson = true } = {}) {
	const form = new FormData()
	form.append('file', file)
	const params = new URLSearchParams({ style, as_json: asJson ? 'true' : 'false' })
	const res = await fetch(`${BASE_URL}/mask?${params.toString()}`, {
		method: 'POST',
		body: form,
	})
	if (!res.ok) throw new Error(`mask failed: ${res.status}`)
	return asJson ? res.json() : res.blob()
} 