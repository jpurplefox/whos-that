import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          fontFamily: "'Courier New', monospace",
          color: '#10b981',
          background: '#0a0a0a',
          textAlign: 'center',
          padding: '2rem',
        }}>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>SYSTEM ERROR</h1>
          <p style={{ opacity: 0.7, marginBottom: '2rem' }}>Something went wrong. Please reload.</p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: 'transparent',
              border: '2px solid #10b981',
              color: '#10b981',
              padding: '0.75rem 2rem',
              fontFamily: "'Courier New', monospace",
              fontSize: '1rem',
              cursor: 'pointer',
              borderRadius: '6px',
            }}
          >
            RELOAD
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
