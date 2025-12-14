const { ipcRenderer } = require('electron');
const React = window.React;
const ReactDOM = window.ReactDOM;
const { useState, useEffect, useRef } = React;

// Particle class for circle animation
class Particle {
    constructor(index, total, radius) {
        this.angle = (index / total) * Math.PI * 2;
        this.baseRadius = radius;
        this.radius = radius;
        this.x = 0;
        this.y = 0;
        this.size = 3 + Math.random() * 2;
        this.speed = 0.001 + Math.random() * 0.002;
        this.offset = Math.random() * Math.PI * 2;
        this.pulseSpeed = 0.02 + Math.random() * 0.03;
        this.pulseOffset = Math.random() * Math.PI * 2;
    }

    update(time, isListening) {
        // Rotate around circle
        this.angle += this.speed;

        // Pulse effect
        const pulse = Math.sin(time * this.pulseSpeed + this.pulseOffset) * 10;
        this.radius = this.baseRadius + pulse;

        // Extra movement when listening
        if (isListening) {
            this.radius += Math.sin(time * 0.05 + this.offset) * 20;
        }

        // Calculate position
        this.x = Math.cos(this.angle) * this.radius;
        this.y = Math.sin(this.angle) * this.radius;
    }
}

// Voice Interface Component with Particle Circle
function VoiceInterface({ onCommand }) {
    const canvasRef = useRef(null);
    const [isListening, setIsListening] = useState(false);
    const [particles, setParticles] = useState([]);
    const animationRef = useRef(null);
    const [lastCommand, setLastCommand] = useState('');

    useEffect(() => {
        // Initialize particles
        const particleCount = 60;
        const radius = 100;
        const newParticles = [];

        for (let i = 0; i < particleCount; i++) {
            newParticles.push(new Particle(i, particleCount, radius));
        }

        setParticles(newParticles);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        let time = 0;

        const animate = () => {
            // Clear canvas
            ctx.fillStyle = 'rgba(10, 14, 39, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update and draw particles
            particles.forEach((particle, i) => {
                particle.update(time, isListening);

                // Draw particle
                const x = centerX + particle.x;
                const y = centerY + particle.y;

                // Gradient for particle
                const gradient = ctx.createRadialGradient(x, y, 0, x, y, particle.size);
                gradient.addColorStop(0, isListening ? '#00fff2' : '#00d4ff');
                gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y, particle.size, 0, Math.PI * 2);
                ctx.fill();

                // Draw connections to nearby particles
                particles.forEach((other, j) => {
                    if (j <= i) return;

                    const otherX = centerX + other.x;
                    const otherY = centerY + other.y;
                    const distance = Math.sqrt(
                        Math.pow(x - otherX, 2) + Math.pow(y - otherY, 2)
                    );

                    if (distance < 80) {
                        const opacity = (1 - distance / 80) * 0.3;
                        ctx.strokeStyle = `rgba(0, 212, 255, ${opacity})`;
                        ctx.lineWidth = 0.5;
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(otherX, otherY);
                        ctx.stroke();
                    }
                });
            });

            // Draw center glow
            const glowSize = isListening ? 40 : 20;
            const glowGradient = ctx.createRadialGradient(
                centerX, centerY, 0,
                centerX, centerY, glowSize
            );
            glowGradient.addColorStop(0, isListening ? 'rgba(0, 255, 242, 0.5)' : 'rgba(0, 212, 255, 0.3)');
            glowGradient.addColorStop(1, 'rgba(0, 212, 255, 0)');

            ctx.fillStyle = glowGradient;
            ctx.beginPath();
            ctx.arc(centerX, centerY, glowSize, 0, Math.PI * 2);
            ctx.fill();

            time += 0.1;
            animationRef.current = requestAnimationFrame(animate);
        };

        if (particles.length > 0) {
            animate();
        }

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [particles, isListening]);

    const handleVoiceCommand = async () => {
        setIsListening(true);
        setTimeout(() => {
            setIsListening(false);
        }, 3000);
    };

    return (
        <div className="voice-interface">
            <div className="particle-container" onClick={handleVoiceCommand}>
                <canvas
                    ref={canvasRef}
                    width={400}
                    height={400}
                    className="particle-canvas"
                />
            </div>

            <div className="voice-status">
                {isListening ? (
                    <p className="status-text listening">Listening...</p>
                ) : (
                    <p className="status-text">Say "Hey ELI" to activate</p>
                )}
            </div>

            {lastCommand && (
                <div className="last-command">
                    <span className="command-label">Last Command:</span>
                    <span className="command-text">{lastCommand}</span>
                </div>
            )}
        </div>
    );
}

// Task Panel Component
function TaskPanel({ tasks }) {
    return (
        <div className="task-panel glass-panel">
            <h2 className="panel-title">
                <span className="title-icon">📋</span>
                Active Tasks
            </h2>

            <div className="task-list">
                {tasks.length === 0 ? (
                    <p className="empty-state">No active tasks</p>
                ) : (
                    tasks.map((task, index) => (
                        <div key={index} className="task-item">
                            <div className="task-checkbox"></div>
                            <div className="task-content">
                                <p className="task-name">{task.name}</p>
                                {task.due_date && (
                                    <p className="task-due">Due: {task.due_date}</p>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

// System Status Component
function SystemStatus({ status }) {
    return (
        <div className="system-status glass-panel">
            <h2 className="panel-title">
                <span className="title-icon">⚡</span>
                System Status
            </h2>

            <div className="status-grid">
                <div className="status-item">
                    <div className={`status-indicator ${status.voice ? 'active' : 'inactive'}`}></div>
                    <span>Voice Engine</span>
                </div>
                <div className="status-item">
                    <div className={`status-indicator ${status.backend ? 'active' : 'inactive'}`}></div>
                    <span>Backend</span>
                </div>
                <div className="status-item">
                    <div className="status-indicator active"></div>
                    <span>UI</span>
                </div>
                <div className="status-item">
                    <div className={`status-indicator ${status.status === 'online' ? 'active' : 'inactive'}`}></div>
                    <span>Status</span>
                </div>
            </div>
        </div>
    );
}

// Command Input Component
function CommandInput({ onSubmit }) {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim()) {
            onSubmit(input);
            setInput('');
        }
    };

    return (
        <div className="command-input-container">
            <form onSubmit={handleSubmit} className="command-form">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type a command or use voice..."
                    className="command-input"
                />
                <button type="submit" className="command-submit">
                    <span>→</span>
                </button>
            </form>
        </div>
    );
}

// Main App Component
function App() {
    const [tasks, setTasks] = useState([]);
    const [status, setStatus] = useState({
        status: 'online',
        voice: true,
        backend: true
    });
    const [commandHistory, setCommandHistory] = useState([]);

    useEffect(() => {
        // Load initial data
        loadTasks();
        loadStatus();

        // Refresh data periodically
        const interval = setInterval(() => {
            loadTasks();
            loadStatus();
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const loadTasks = async () => {
        try {
            const result = await ipcRenderer.invoke('get-tasks');
            if (result.success && result.tasks) {
                setTasks(result.tasks);
            }
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    };

    const loadStatus = async () => {
        try {
            const result = await ipcRenderer.invoke('get-status');
            setStatus(result);
        } catch (error) {
            console.error('Failed to load status:', error);
        }
    };

    const handleCommand = async (command) => {
        try {
            setCommandHistory([...commandHistory, { text: command, timestamp: new Date() }]);

            const result = await ipcRenderer.invoke('send-command', command);

            if (result.success) {
                loadTasks();
            }
        } catch (error) {
            console.error('Command failed:', error);
        }
    };

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <h1 className="app-title">
                        <span className="title-main">ELI</span>
                        <span className="title-sub">Enhanced Learning Intelligence</span>
                    </h1>
                    <div className="header-status">
                        <div className="status-dot"></div>
                        <span>Online</span>
                    </div>
                </div>
            </header>

            <main className="app-main">
                <div className="main-grid">
                    <div className="grid-left">
                        <VoiceInterface onCommand={handleCommand} />
                        <CommandInput onSubmit={handleCommand} />
                    </div>

                    <div className="grid-right">
                        <SystemStatus status={status} />
                        <TaskPanel tasks={tasks} />
                    </div>
                </div>
            </main>

            <div className="background-effects">
                <div className="grid-overlay"></div>
                <div className="glow-effect glow-1"></div>
                <div className="glow-effect glow-2"></div>
            </div>
        </div>
    );
}

// Render app
ReactDOM.render(<App />, document.getElementById('root'));
