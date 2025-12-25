import React, { useState } from 'react';
import DefaultLayout from '@theme-original/Layout';
import Chatbot from '@site/src/components/Chatbot';

export default function Layout(props) {
  const [showChatbot, setShowChatbot] = useState(false);

  const toggleChatbot = () => {
    setShowChatbot(!showChatbot);
  };

  return (
    <>
      <DefaultLayout {...props} />
      {/* Floating chat button */}
      <button
        onClick={toggleChatbot}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          fontSize: '24px',
          cursor: 'pointer',
          zIndex: 1000,
          boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
        }}
      >
        💬
      </button>
      
      {/* Chatbot Panel - only show when toggled */}
      {showChatbot && (
        <div
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            width: '350px',
            height: '500px',
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            borderRadius: '8px',
            backgroundColor: 'white',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '10px',
              backgroundColor: '#007bff',
              color: 'white',
              borderTopLeftRadius: '8px',
              borderTopRightRadius: '8px',
            }}
          >
            <span>Book Tutor</span>
            <button
              onClick={toggleChatbot}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '18px',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
          </div>
          <div style={{ height: 'calc(100% - 40px)' }}>
            <Chatbot />
          </div>
        </div>
      )}
    </>
  );
}