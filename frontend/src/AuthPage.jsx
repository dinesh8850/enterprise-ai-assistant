import { useState } from 'react'

// onLogin is a callback passed from the parent (App.jsx) -- when
// login/register succeeds, we call it with the token so App.jsx
// can store it and switch to the main app view.
function AuthPage({ apiBaseUrl, onLogin }) {
  const [mode, setMode] = useState('login')   // 'login' or 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()   // stops the browser's default full-page form reload
    setError(null)
    setIsSubmitting(true)

    try {
      const response = await fetch(`${apiBaseUrl}/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        setError(data.detail || `${mode === 'login' ? 'Login' : 'Registration'} failed`)
        return
      }

      const data = await response.json()
      onLogin(data.access_token)
    } catch (err) {
      setError('Could not reach the server.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-container">
      <h2>{mode === 'login' ? 'Log in' : 'Create an account'}</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Register'}
        </button>
      </form>

      {error && <div className="upload-error">{error}</div>}

      <p className="auth-switch">
        {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
        <button className="link-button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Register' : 'Log in'}
        </button>
      </p>
    </main>
  )
}

export default AuthPage
