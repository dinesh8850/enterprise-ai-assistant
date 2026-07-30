import { useState } from 'react'
import './App.css'

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
      const data = await response.json()

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data.answer, routedTo: data.routed_to },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Something went wrong reaching the server.' },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <h1>Enterprise AI Assistant</h1>

      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
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
    </div>
  )
}

export default App
