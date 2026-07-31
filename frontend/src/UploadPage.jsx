import { useState } from 'react'

// apiBaseUrl is passed in as a prop from App.jsx -- this is how
// a child component receives data from its parent (recall Task 11.1's
// "props" vocabulary).
function UploadPage({ apiBaseUrl, token }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  function handleFileChange(e) {
    setSelectedFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  async function handleUpload() {
    if (!selectedFile) return

    setIsUploading(true)
    setResult(null)
    setError(null)

    // FormData is the browser's built-in way to build a
    // multipart/form-data request body -- matches what our
    // FastAPI UploadFile endpoint expects (Task 7.2).
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${apiBaseUrl}/documents/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
        // Note: no 'Content-Type' header here -- the browser sets it
        // automatically for FormData, including the required boundary.
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        setError(errorData.detail || `Upload failed (${response.status})`)
        return
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Could not reach the server. Is the backend running?')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <main className="upload-container">
      <h2>Upload a document</h2>

      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!selectedFile || isUploading}>
        {isUploading ? 'Uploading...' : 'Upload'}
      </button>

      {error && <div className="upload-error">{error}</div>}

      {result && (
        <div className="upload-result">
          <p><strong>Filename:</strong> {result.filename}</p>
          <p><strong>Status:</strong> {result.status}</p>
          <p><strong>Chunks created:</strong> {result.chunks_created}</p>
          <p><strong>Chunks stored in Qdrant:</strong> {result.chunks_stored_in_qdrant}</p>
          <p><strong>Preview:</strong> {result.preview}</p>
        </div>
      )}
    </main>
  )
}

export default UploadPage
