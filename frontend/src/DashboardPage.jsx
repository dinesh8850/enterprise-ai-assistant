import { useState, useEffect } from 'react'

// useEffect lets a component run code in response to it appearing on
// screen (or specific values changing) -- here, we fetch documents
// once when the Dashboard first mounts.
function DashboardPage({ apiBaseUrl, token }) {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadDocuments() {
      try {
        const response = await fetch(`${apiBaseUrl}/documents/`, {
          headers: { 'Authorization': `Bearer ${token}` },
        })
        if (!response.ok) {
          setError(`Failed to load documents (${response.status})`)
          return
        }
        const data = await response.json()
        setDocuments(data)
      } catch (err) {
        setError('Could not reach the server.')
      } finally {
        setIsLoading(false)
      }
    }
    loadDocuments()
  }, [apiBaseUrl, token])   // re-run only if apiBaseUrl ever changes

  const processedCount = documents.filter((d) => d.status === 'processed').length
  const failedCount = documents.filter((d) => d.status === 'failed').length

  return (
    <main className="dashboard-container">
      <h2>Dashboard</h2>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-number">{documents.length}</div>
          <div className="stat-label">Total documents</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{processedCount}</div>
          <div className="stat-label">Processed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{failedCount}</div>
          <div className="stat-label">Failed</div>
        </div>
      </div>

      {isLoading && <p>Loading...</p>}
      {error && <div className="upload-error">{error}</div>}

      {!isLoading && !error && (
        <table className="doc-table">
          <thead>
            <tr><th>Filename</th><th>Type</th><th>Status</th><th>Uploaded</th></tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.filename}</td>
                <td>{doc.file_type}</td>
                <td><span className={`badge badge-${doc.status}`}>{doc.status}</span></td>
                <td>{new Date(doc.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}

export default DashboardPage
