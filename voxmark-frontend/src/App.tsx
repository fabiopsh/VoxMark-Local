import { createSignal, onMount, For, Show } from 'solid-js';
// import { Command } from '@tauri-apps/plugin-shell'; 
// Spawn logic removed to simplify POC reliability based on user feedback.
import './App.css';

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const [status, setStatus] = createSignal<any>(null);
  const [loading, setLoading] = createSignal(true);
  const [logs, setLogs] = createSignal<string[]>([]);
  const [inputText, setInputText] = createSignal("**Hello**, this is a test.");
  const [isSynthesizing, setIsSynthesizing] = createSignal(false);

  const addLog = (msg: string) => setLogs((l) => [...l.slice(-4), msg]);

  const downloadModel = async () => {
    setLoading(true);
    addLog("Starting model download (this may take a while)...");
    addLog("👉 CHECK THE BLACK BACKEND WINDOW for download progress % 👈");
    try {
      const res = await window.fetch(`${BACKEND_URL}/install`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        addLog("Model download complete!");
        checkStatus();
      } else {
        addLog("Model download failed. Check console.");
      }
    } catch (e) {
      addLog(`Download error: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const res = await window.fetch(`${BACKEND_URL}/status`);
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
        setLoading(false);
      }
    } catch (e) {
      // Backend not ready yet
      // addLog("Waiting for Backend...");
    }
  };

  onMount(async () => {
    // We assume backend is started manually or via script
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  });

  const synthesize = async () => {
    setIsSynthesizing(true);
    addLog("Synthesizing...");
    try {
      const res = await window.fetch(`${BACKEND_URL}/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText() })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
        addLog("Audio playing");
      } else {
        addLog("Synthesis failed");
      }
    } catch (e) {
      addLog(`Error: ${e}`);
    } finally {
      setIsSynthesizing(false);
    }
  };

  return (
    <div class="container">
      <h1>VoxMark Local POC</h1>

      <div class="logs">
        <For each={logs()}>{(log) => <div class="log-line">{log}</div>}</For>
      </div>

      <Show when={!loading() || !status()} fallback={<p>Waiting for Backend on port 8000...</p>}>
        <div class="status-panel">
          <h3>System Status</h3>
          <p>Model Present: {status()?.model_present ? '✅' : '❌'}</p>
          <p>Espeak Present: {status()?.espeak_present ? '✅' : '❌'}</p>
          <p>Ready: {status()?.ready_to_synthesize ? '✅' : '❌'}</p>

          <Show when={!status()?.model_present}>
            <button onClick={downloadModel} class="download-btn">
              Download Model (Auto)
            </button>
            <p style={{ "font-size": "0.8rem", color: "#666" }}>
              (Downloads ~1GB from HuggingFace)
            </p>
          </Show>
        </div>

        <div class="editor-panel">
          <textarea
            value={inputText()}
            onInput={(e) => setInputText(e.currentTarget.value)}
            rows={5}
            cols={50}
          />
          <br />
          <button onClick={synthesize} disabled={isSynthesizing() || !status()?.model_present}>
            {isSynthesizing() ? 'Synthesizing...' : 'Play'}
          </button>
        </div>
      </Show>
    </div>
  );
}

export default App;
