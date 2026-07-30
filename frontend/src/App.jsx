import { useState } from 'react'
import './App.css'
import UploadPage from './UploadPage'

// The backend's base URL. In a real deployment this would come from
// an environment variable -- we'll hardcode it for now since we're
// running everything locally.
const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  // messages: the full conversation history shown on screen.
  // Each message is an object like { role: 'user' | 'assistant', text: '...' }
  const [messages, setMessages] = useState([])

  // input: the text currently typed in the input box.
  const [input, setInput] = useState('')

  // isLoading: true while we're waiting for the backend to respond --
  // lets us show a "thinking..." indicator and disable the send button.
  const [isLoading, setIsLoading] = useState(false)
  const [activePage, setActivePage] = useState('chat')

  async function handleSend() {
    const question = input.trim()
    if (!question) return   // don't send empty messages

    // Immediately show the user's own message, and clear the input box.
    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/query/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      // fetch() only rejects on a genuine network failure (server unreachable).
      // A 400/500 response still "succeeds" as far as fetch is concerned --
      // response.ok tells us whether the HTTP status was actually 2xx.
      if (!response.ok) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', text: `Server error (${response.status}). Please try again.`, isError: true },
        ])
        return
      }

      const data = await response.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data.answer, routedTo: data.routed_to },
      ])
    } catch (error) {
      // This branch only runs for genuine network failures --
      // e.g. the backend isn't running at all.
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Could not reach the server. Is the backend running?', isError: true },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">Enterprise AI Assistant</span>
        <nav className="app-nav">
          <button className={activePage === 'chat' ? 'active' : ''} onClick={() => setActivePage('chat')}>Chat</button>
          <button className={activePage === 'upload' ? 'active' : ''} onClick={() => setActivePage('upload')}>Upload</button>
        </nav>
      </header>

      {activePage === 'upload' ? (
        <UploadPage apiBaseUrl={API_BASE_URL} />
      ) : (
      <main className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}${msg.isError ? ' error-message' : ''}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong> {msg.text}
            {msg.routedTo && <div className="routed-to">via {msg.routedTo}</div>}
          </div>
        ))}
        {isLoading && <div className="message assistant">Thinking...</div>}
      </div>

      <div className="input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading}>
          Send
        </button>
      </div>
      </main>
      )}
    </div>
  )
}

export default App
