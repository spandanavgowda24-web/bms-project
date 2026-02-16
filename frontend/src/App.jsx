import { useState, useRef } from "react";

const BASE_URL = "http://127.0.0.1:5000";

function App() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);
  const waveRef = useRef(null);

  const addMessage = (msg, type) => {
    setMessages((prev) => [...prev, { msg, type }]);
  };

  const sendText = async (customText) => {
    const finalText = customText || text;
    if (!finalText) return;

    addMessage(finalText, "user");
    setText("");

    const res = await fetch(`${BASE_URL}/generate-response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "U001",
        session_id: "S001",
        speech_text: finalText,
      }),
    });

    const data = await res.json();
    addMessage(data.data.response_text, "system");

    const audio = new Audio(`${BASE_URL}/${data.data.audio_response}`);
    audio.play();
  };

  const toggleMic = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Browser not supported");
      return;
    }

    if (!recognitionRef.current) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.lang = "en-US";
      recognitionRef.current.continuous = false;

      recognitionRef.current.onresult = (event) => {
        const speech = event.results[0][0].transcript;
        sendText(speech);
      };

      recognitionRef.current.onend = () => {
        setListening(false);
        if (waveRef.current) waveRef.current.style.width = "0%";
      };
    }

    if (!listening) {
      recognitionRef.current.start();
      setListening(true);
      if (waveRef.current) waveRef.current.style.width = "100%";
    } else {
      recognitionRef.current.stop();
      setListening(false);
      if (waveRef.current) waveRef.current.style.width = "0%";
    }
  };

  const uploadSpeech = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "U001");
    formData.append("session_id", "S001");

    const res = await fetch(`${BASE_URL}/speech-to-text`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    sendText(data.data.speech_text);
  };

  return (
    <div className="app">
      <header>
        <h2>🤖 Intelligent Speech Interaction</h2>
      </header>

      <div className="chat-box">
        {messages.map((m, index) => (
          <div key={index} className={`message ${m.type}`}>
            {m.msg}
          </div>
        ))}
      </div>

      <div className="wave" ref={waveRef}></div>

      <div className="controls">
        <button className="mic-btn" onClick={toggleMic}>
          🎤
        </button>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your message..."
        />

        <button onClick={() => sendText()}>Send</button>
      </div>

      <input type="file" onChange={uploadSpeech} />
    </div>
  );
}

export default App;
