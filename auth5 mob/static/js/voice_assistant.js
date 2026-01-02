class VoiceAssistant {
    constructor(callbacks) {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isRecording = false;
        this.shouldRestart = false;
        this.callbacks = callbacks || {};
        this.voices = [];
        this.currentUtterance = null;

        // Bind methods
        this.toggle = this.toggle.bind(this);
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.speak = this.speak.bind(this);
        this.cleanText = this.cleanText.bind(this);

        this.initRecognition();
        this.initSynthesis();
    }

    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("VoiceAssistant: Speech Recognition API not supported.");
            if (this.callbacks.onError) this.callbacks.onError("Speech recognition not supported in this browser.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            console.log("VoiceAssistant: Recognition started");
            this.isRecording = true;
            if (this.callbacks.onStart) this.callbacks.onStart();
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                console.log("VoiceAssistant: Final Transcript received:", finalTranscript);
                if (this.callbacks.onResult) {
                    this.callbacks.onResult(finalTranscript.trim());
                }

                // Stop after final result to process command
                this.stop();
            } else if (interimTranscript) {
                if (this.callbacks.onInterim) {
                    this.callbacks.onInterim(interimTranscript);
                }
            }
        };

        this.recognition.onerror = (event) => {
            if (event.error === 'no-speech' || event.error === 'aborted') {
                return;
            }
            console.error("VoiceAssistant Recognition Error:", event.error);
            this.isRecording = false;
            if (this.callbacks.onError) this.callbacks.onError(event.error);
        };

        this.recognition.onend = () => {
            console.log("VoiceAssistant: Recognition ended");
            this.isRecording = false;
            if (this.shouldRestart) {
                this.start();
            } else {
                if (this.callbacks.onEnd) this.callbacks.onEnd();
            }
        };
    }

    initSynthesis() {
        if (!this.synthesis) {
            console.warn("VoiceAssistant: Text-to-Speech not supported.");
            return;
        }

        const loadVoices = () => {
            this.voices = this.synthesis.getVoices();
            if (this.voices.length > 0) {
                console.log(`VoiceAssistant: Found ${this.voices.length} voices.`);
            }
        };

        loadVoices();
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = loadVoices;
        }
    }

    cleanText(text) {
        if (!text) return "";
        // Remove markdown formatting and improve flow for better speech
        return text
            .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
            .replace(/\*(.*?)\*/g, '$1')     // Italic
            .replace(/`(.*?)`/g, '$1')       // Code
            .replace(/#+\s+(.*?)\n/g, '$1. ') // Headers as sentences
            .replace(/\[(.*?)\]\((.*?)\)/g, '$1') // Links
            .replace(/\n+/g, ' ')            // Newlines to spaces
            .replace(/- /g, '')              // List dashes
            .replace(/:\)/g, 'smiling face')  // Emojis common in AI
            .trim();
    }

    toggle() {
        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }

    start() {
        if (!this.recognition) return;
        if (this.isRecording) return;

        try {
            this.shouldRestart = false;
            this.recognition.start();
        } catch (e) {
            console.error("VoiceAssistant: Failed to start recognition:", e);
        }
    }

    stop() {
        if (!this.recognition) return;
        this.shouldRestart = false;
        try {
            this.recognition.stop();
        } catch (e) {
            // Silently fail if already stopped
        }
    }

    speak(text) {
        if (!this.synthesis) {
            console.error("VoiceAssistant: Synthesis not available");
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        if (!text) {
            console.warn("VoiceAssistant: No text to speak");
            return;
        }

        const cleanedText = this.cleanText(text);
        console.log("VoiceAssistant: Preparing to speak:", cleanedText.substring(0, 50) + "...");

        const utterance = new SpeechSynthesisUtterance(cleanedText);

        // Ensure voices are loaded
        if (this.voices.length === 0) {
            this.voices = this.synthesis.getVoices();
        }

        const preferredVoices = [
            'Google US English',
            'Microsoft Aria Online',
            'Samantha',
            'Microsoft Zira',
            'English United States',
            'en-US'
        ];

        let selectedVoice = null;
        for (const name of preferredVoices) {
            selectedVoice = this.voices.find(v => v.name.includes(name) || v.lang === name);
            if (selectedVoice) break;
        }

        if (!selectedVoice) {
            selectedVoice = this.voices.find(v => v.lang.startsWith('en'));
        }

        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log("VoiceAssistant: Selected voice:", selectedVoice.name);
        } else {
            console.warn("VoiceAssistant: No matching English voice found, using default");
        }

        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.onstart = () => {
            console.log("VoiceAssistant: Speaking started...");
        };

        utterance.onend = () => {
            console.log("VoiceAssistant: Speaking finished.");
            this.currentUtterance = null;
        };

        utterance.onerror = (e) => {
            console.error("VoiceAssistant: Synthesis Error:", e);
        };

        // Important: keep a reference to prevent garbage collection
        this.currentUtterance = utterance;

        // Use a small timeout to ensure cancel() has taken effect in some browsers
        setTimeout(() => {
            this.synthesis.speak(utterance);
        }, 50);
    }
}
