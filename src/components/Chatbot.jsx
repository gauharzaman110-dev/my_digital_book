import React, { useState, useRef, useEffect } from 'react';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null); // Track session ID
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Adjust this if your backend is on a different port/host
  const API_ENDPOINT = 'http://localhost:8000/api/v1/chat/';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    // Focus the input field when the component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [messages]);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const newUserMessage = { text: inputText, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputText('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const requestBody = {
        message: newUserMessage.text
      };

      // Include session ID if we have one
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong!');
      }

      const data = await response.json();

      // Update session ID if returned from backend
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      // Simulate typing delay for better UX
      setTimeout(() => {
        let agentResponse;
        if (data.response === "The book is currently unavailable.") {
          agentResponse = { text: "The chatbot is not configured correctly. Please make sure you have added your Gemini API key to the .env file in the backend.", sender: 'agent' };
        } else {
          agentResponse = { text: data.response, sender: 'agent' };
        }
        setMessages((prevMessages) => [...prevMessages, agentResponse]);
        setIsTyping(false);
      }, 500); // Add a small delay to simulate typing
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `Error: ${error.message}`, sender: 'agent' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '700px',
      margin: '20px auto',
      borderRadius: '16px',
      display: 'flex',
      flexDirection: 'column',
      height: '600px',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
      backgroundColor: '#ffffff',
      border: '1px solid #e1e5e9',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '16px 20px',
        borderBottom: '1px solid #e9ecef',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          backgroundColor: '#4CAF50'
        }}></div>
        <h3 style={{
          margin: 0,
          fontSize: '1.2em',
          fontWeight: '600',
          color: '#212529'
        }}>
          Digital Book Assistant
        </h3>
        <span style={{
          marginLeft: 'auto',
          fontSize: '0.85em',
          color: '#6c757d'
        }}>
          {isLoading ? 'Online' : 'Online'}
        </span>
      </div>

      {/* Messages Container */}
      <div style={{
        flexGrow: 1,
        overflowY: 'auto',
        padding: '20px',
        backgroundColor: '#fafafa',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {messages.length === 0 && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            textAlign: 'center',
            color: '#6c757d',
            padding: '20px'
          }}>
            <div style={{
              fontSize: '48px',
              marginBottom: '15px',
              opacity: 0.7
            }}>
              🤖
            </div>
            <h4 style={{
              margin: '0 0 10px 0',
              color: '#495057',
              fontSize: '1.2em'
            }}>
              Welcome to the Digital Book Assistant!
            </h4>
            <p style={{
              margin: '5px 0',
              fontSize: '0.95em',
              maxWidth: '400px'
            }}>
              I'm here to help you explore and understand the content of your Physical AI and Robotics book.
            </p>
            <div style={{
              marginTop: '20px',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              gap: '10px',
              maxWidth: '500px'
            }}>
              {[
                "What is Physical AI?",
                "How many chapters are there?",
                "Explain robot locomotion",
                "Summarize chapter 5"
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => setInputText(suggestion)}
                  style={{
                    backgroundColor: '#e9ecef',
                    border: '1px solid #dee2e6',
                    borderRadius: '16px',
                    padding: '6px 12px',
                    fontSize: '0.8em',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    color: '#495057'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#dee2e6';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#e9ecef';
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
            <p style={{
              marginTop: '20px',
              fontSize: '0.9em',
              color: '#6c757d',
              fontStyle: 'italic'
            }}>
              Or type your own question below:
            </p>
          </div>
        )}

        <div style={{ flexGrow: 1 }}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: '16px',
              }}
            >
              <div
                style={{
                  backgroundColor: msg.sender === 'user' ? '#007bff' : '#ffffff',
                  color: msg.sender === 'user' ? 'white' : '#333',
                  padding: '12px 16px',
                  borderRadius: msg.sender === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                  maxWidth: '85%',
                  wordBreak: 'break-word',
                  fontSize: '0.95em',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
                  border: msg.sender === 'agent' ? '1px solid #e9ecef' : 'none',
                  lineHeight: '1.5'
                }}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
              <div style={{
                backgroundColor: '#ffffff',
                color: '#333',
                padding: '12px 16px',
                borderRadius: '18px 18px 18px 4px',
                maxWidth: '85%',
                wordBreak: 'break-word',
                fontSize: '0.95em',
                boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
                border: '1px solid #e9ecef',
                lineHeight: '1.5'
              }}>
                <div className="chatbot-typing-indicator">
                  <div className="chatbot-typing-dot"></div>
                  <div className="chatbot-typing-dot"></div>
                  <div className="chatbot-typing-dot"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        padding: '16px',
        backgroundColor: '#ffffff',
        borderTop: '1px solid #e9ecef'
      }}>
        <form
          onSubmit={handleSendMessage}
          style={{
            display: 'flex',
            gap: '10px',
            alignItems: 'center'
          }}
        >
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={handleInputChange}
            placeholder="Type your message here..."
            disabled={isLoading}
            style={{
              flexGrow: 1,
              padding: '14px 18px',
              border: '1px solid #ced4da',
              borderRadius: '24px',
              fontSize: '1em',
              outline: 'none',
              transition: 'border-color 0.2s',
              backgroundColor: '#f8f9fa'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#80bdff';
              e.target.style.boxShadow = '0 0 0 0.2rem rgba(0,123,255,.25)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#ced4da';
              e.target.style.boxShadow = 'none';
            }}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            style={{
              backgroundColor: isLoading || !inputText.trim() ? '#6c757d' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '24px',
              padding: '14px 24px',
              cursor: isLoading || !inputText.trim() ? 'not-allowed' : 'pointer',
              fontSize: '1em',
              fontWeight: '500',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            onMouseEnter={(e) => {
              if (!(isLoading || !inputText.trim())) {
                e.target.style.backgroundColor = '#0069d9';
              }
            }}
            onMouseLeave={(e) => {
              if (!(isLoading || !inputText.trim())) {
                e.target.style.backgroundColor = '#007bff';
              }
            }}
          >
            {isLoading ? (
              <>
                <div style={{
                  display: 'inline-block',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: 'white',
                  marginRight: '8px',
                  animation: 'bounce 1.5s infinite',
                  animationTimingFunction: 'cubic-bezier(0.5, 0, 0.5, 1)'
                }}></div>
                Sending...
              </>
            ) : (
              <>
                <span>→</span> Send
              </>
            )}
          </button>
        </form>
      </div>

    </div>
  );
};

export default Chatbot;
