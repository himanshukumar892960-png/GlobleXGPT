document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-messages');
    const chatWrapper = document.getElementById('chat-wrapper');
    const welcomeScreen = document.getElementById('welcome-screen');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn'); // Added back
    const sidebar = document.querySelector('.sidebar');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const sidebarOpenBtn = document.getElementById('sidebar-open-btn');
    const attachBtn = document.getElementById('attach-btn');
    const fileAttachInput = document.getElementById('file-attach-input');
    const filePreviewContainer = document.getElementById('file-preview-container');
    let attachedFile = null;

    // Track input method to decide whether to speak response
    let lastInputWasVoice = false;

    const sidebarOverlay = document.getElementById('sidebar-overlay');

    // Sidebar Toggle Logic
    if (sidebarCloseBtn && sidebarOpenBtn) {
        sidebarCloseBtn.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
            sidebarOpenBtn.classList.add('visible');
            if (window.innerWidth <= 768) {
                sidebarOverlay.classList.remove('active');
            }
        });

        sidebarOpenBtn.addEventListener('click', () => {
            sidebar.classList.remove('collapsed');
            sidebarOpenBtn.classList.remove('visible');
            if (window.innerWidth <= 768) {
                sidebarOverlay.classList.add('active');
            }
        });

        // Close sidebar when clicking overlay on mobile
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => {
                sidebar.classList.add('collapsed');
                sidebarOpenBtn.classList.add('visible');
                sidebarOverlay.classList.remove('active');
            });
        }
    }





    // --- Voice Logic (Externalized) ---
    const voiceAssistant = new VoiceAssistant({
        onStart: () => {
            micBtn.classList.add('recording');
            userInput.placeholder = "Listening...";
        },
        onEnd: () => {
            micBtn.classList.remove('recording');
            userInput.placeholder = "Ask anything";
        },
        onInterim: (transcript) => {
            userInput.value = transcript;
        },
        onResult: (transcript) => {
            console.log("🎤 Voice input received:", transcript);
            userInput.value = transcript;
            lastInputWasVoice = true;
            console.log("✅ lastInputWasVoice flag set to TRUE");
            handleSendMessage();
        },
        onError: (error) => {
            userInput.placeholder = "Error: " + error;
            console.error("Voice Error:", error);
            micBtn.classList.remove('recording');
        }
    });



    let currentChatId = null;
    let chatHistory = JSON.parse(localStorage.getItem('chat_history') || '[]');

    function saveChatToLocalStorage() {
        localStorage.setItem('chat_history', JSON.stringify(chatHistory));
        renderChatHistory();
    }

    function renderChatHistory(filter = '') {
        const historyList = document.getElementById('chat-history-list');
        if (!historyList) return;

        historyList.innerHTML = '';
        const filtered = chatHistory.filter(c => c.title.toLowerCase().includes(filter.toLowerCase()));

        filtered.forEach(chat => {
            const item = document.createElement('div');
            item.className = 'history-item';
            if (chat.id === currentChatId) item.classList.add('active');

            item.innerHTML = `
                <div class="history-item-content">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span>${chat.title}</span>
                </div>
                <div class="delete-chat-btn" title="Delete chat">
                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </div>
            `;

            item.querySelector('.history-item-content').addEventListener('click', () => loadChat(chat.id));
            item.querySelector('.delete-chat-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteChat(chat.id);
            });
            historyList.appendChild(item);
        });
    }

    function deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;

        chatHistory = chatHistory.filter(c => c.id !== chatId);
        if (currentChatId === chatId) {
            currentChatId = null;
            chatContainer.innerHTML = '';
            welcomeScreen.style.display = 'flex';
        }
        saveChatToLocalStorage();
    }

    function loadChat(chatId) {
        currentChatId = chatId;
        const chat = chatHistory.find(c => c.id === chatId);
        if (!chat) return;

        chatContainer.innerHTML = '';
        welcomeScreen.style.display = 'none';

        chat.messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(msg.isAi ? 'ai-message' : 'user-message');
            messageDiv.innerHTML = msg.text;
            chatContainer.appendChild(messageDiv);
        });

        chatWrapper.scrollTop = chatWrapper.scrollHeight;
        renderChatHistory();

        // On mobile, close sidebar after loading a chat
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            sidebarOpenBtn.classList.add('visible');
            sidebarOverlay.classList.remove('active');
        }
    }

    function updateChatHistoryEntry(text, isAi) {
        if (!currentChatId && !isAi) {
            currentChatId = Date.now().toString();
            chatHistory.unshift({
                id: currentChatId,
                title: text.length > 30 ? text.substring(0, 30) + '...' : text,
                messages: []
            });
        }

        const chat = chatHistory.find(c => c.id === currentChatId);
        if (chat) {
            chat.messages.push({ text, isAi });
            saveChatToLocalStorage();
        }
    }

    // Initialize history
    renderChatHistory();

    const historySearch = document.getElementById('history-search');
    if (historySearch) {
        historySearch.addEventListener('input', (e) => {
            renderChatHistory(e.target.value);
        });
    }

    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            currentChatId = null;
            chatContainer.innerHTML = '';
            welcomeScreen.style.display = 'flex';
            renderChatHistory();
        });
    }

    function addMessage(text, isAi = true, emotion = null) {
        // Hide welcome screen on first message
        if (welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
        }

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isAi ? 'ai-message' : 'user-message');

        if (isAi) {
            messageDiv.innerHTML = `
                <div class="message-content">${text}</div>
                <div class="message-actions">
                    <button class="msg-action-btn speak-btn" title="Listen to response">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        </svg>
                    </button>
                    <button class="msg-action-btn copy-btn" title="Copy to clipboard">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                    </button>
                </div>
            `;

            // Add listeners for the buttons
            const speakBtn = messageDiv.querySelector('.speak-btn');
            if (speakBtn) {
                speakBtn.addEventListener('click', () => voiceAssistant.speak(text));
            }
            const copyBtn = messageDiv.querySelector('.copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    const tempText = text.replace(/<[^>]*>/g, ''); // Strip HTML if any
                    navigator.clipboard.writeText(tempText);
                    copyBtn.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" stroke="#30d158" stroke-width="2" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                    }, 2000);
                });
            }
        } else {
            messageDiv.innerHTML = text;
        }

        chatContainer.appendChild(messageDiv);

        // Scroll to bottom
        chatWrapper.scrollTop = chatWrapper.scrollHeight;

        // Save to history
        updateChatHistoryEntry(text, isAi);

        // Speak the AI response if it was triggered by voice
        if (isAi && lastInputWasVoice) {
            console.log("🔊 Auto-speaking AI response...");
            voiceAssistant.speak(text);
            lastInputWasVoice = false; // Reset flag after speaking
        }
    }

    async function handleSendMessage() {
        const prompt = userInput.value.trim();
        if (!prompt && !attachedFile) return;

        userInput.value = '';
        const displayPrompt = attachedFile ? (prompt || "Attached File") : prompt;
        addMessage(displayPrompt, false);

        // Hide preview
        filePreviewContainer.classList.add('hidden');
        filePreviewContainer.innerHTML = '';

        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai-message', 'thinking');
        thinkingDiv.innerText = 'GlobleXGPT is thinking...';
        chatContainer.appendChild(thinkingDiv);
        chatWrapper.scrollTop = chatWrapper.scrollHeight;

        try {
            const payload = {
                prompt: prompt,
                file: attachedFile ? {
                    name: attachedFile.name,
                    type: attachedFile.type,
                    data: attachedFile.data
                } : null
            };

            attachedFile = null; // Clear after prep

            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            chatContainer.removeChild(thinkingDiv);
            addMessage(data.response, true, data.emotion);

        } catch (error) {
            console.error('Error:', error);
            if (chatContainer.contains(thinkingDiv)) chatContainer.removeChild(thinkingDiv);
            addMessage("I'm sorry, I encountered an internal error. Please check if the server is running.");
        }
    }

    sendBtn.addEventListener('click', () => {
        lastInputWasVoice = false;
        handleSendMessage();
    });

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            voiceAssistant.toggle();
        });
    }

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            lastInputWasVoice = false;
            handleSendMessage();
        }
    });

    if (attachBtn && fileAttachInput) {
        attachBtn.addEventListener('click', () => fileAttachInput.click());

        const handleFileChange = (file) => {
            if (!file) return;

            const isImage = file.type.startsWith('image/');
            const reader = new FileReader();

            reader.onload = (event) => {
                attachedFile = {
                    name: file.name,
                    type: file.type,
                    data: event.target.result, // Base64 for images, raw text for text files
                    isText: !isImage
                };

                // Show preview
                filePreviewContainer.classList.remove('hidden');
                filePreviewContainer.innerHTML = `
                    <div class="file-preview-item">
                        ${isImage ? `<img src="${event.target.result}">` : '<div class="file-icon">📄</div>'}
                        <div class="file-preview-name">${file.name}</div>
                        <button class="file-remove-btn">×</button>
                    </div>
                `;

                filePreviewContainer.querySelector('.file-remove-btn').addEventListener('click', () => {
                    attachedFile = null;
                    filePreviewContainer.classList.add('hidden');
                    filePreviewContainer.innerHTML = '';
                    fileAttachInput.value = '';
                });

                // Clear input after processing
                userInput.placeholder = "Say something about this...";
                userInput.focus();
            };

            if (isImage) {
                reader.readAsDataURL(file);
            } else {
                reader.readAsText(file);
            }
        };

        fileAttachInput.addEventListener('change', (e) => {
            handleFileChange(e.target.files[0]);
        });

        // drag and drop support
        const inputCapsule = document.querySelector('.input-bar-capsule');
        if (inputCapsule) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, () => {
                    inputCapsule.classList.add('drag-active');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, () => {
                    inputCapsule.classList.remove('drag-active');
                }, false);
            });

            inputCapsule.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files && files[0]) {
                    handleFileChange(files[0]);
                }
            });
        }
    }



    // Auto-collapse sidebar on mobile
    if (window.innerWidth <= 768 && sidebarCloseBtn) {
        sidebarCloseBtn.click();
    }

    // --- Authentication Logic ---
    const authModal = document.getElementById('auth-modal');
    const closeAuthBtn = document.getElementById('close-auth-btn');
    // const userProfileBtn = document.querySelector('.user-profile'); // Replaced by authTriggerBtns
    const authForm = document.getElementById('auth-form');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const authSubmitBtn = document.getElementById('auth-submit-btn');
    const toggleAuthModeBtn = document.getElementById('toggle-auth-mode');
    const authSwitchText = document.getElementById('auth-switch-text');
    const authMessage = document.getElementById('auth-message');
    const nameGroup = document.getElementById('name-group');
    const avatarGroup = document.getElementById('avatar-group');
    const profilePicInput = document.getElementById('profile-pic');
    const avatarBase64Input = document.getElementById('avatar-base64');
    const avatarPreview = document.getElementById('avatar-preview');

    let isLoginMode = true;

    function openAuthModal() {
        authModal.classList.remove('hidden');
        authMessage.innerText = '';
        authMessage.className = 'auth-message';
    }

    function closeAuthModal() {
        authModal.classList.add('hidden');
    }

    const authTriggerBtns = document.querySelectorAll('.user-profile, #sidebar-login-btn');

    const userMenu = document.getElementById('user-menu');
    const logoutBtn = document.getElementById('logout-btn');

    function updateUserInterface(user) {
        // 1. Update Sidebar Button
        const sidebarLoginBtn = document.getElementById('sidebar-login-btn');
        if (sidebarLoginBtn) {
            const span = sidebarLoginBtn.querySelector('span');
            const svg = sidebarLoginBtn.querySelector('svg');

            if (user) {
                // Logged In State for Sidebar
                if (span) span.innerText = user.full_name || "User";

                let img = sidebarLoginBtn.querySelector('img');
                if (user.avatar_url && user.avatar_url.length > 50) {
                    if (!img) {
                        img = document.createElement('img');
                        img.style.width = '24px';
                        img.style.height = '24px';
                        img.style.borderRadius = '50%';
                        img.style.objectFit = 'cover';
                        img.style.marginRight = '0';
                        if (svg) svg.replaceWith(img);
                        else sidebarLoginBtn.prepend(img);
                    }
                    img.src = user.avatar_url;
                }
            } else {
                // Reset Sidebar
                if (span) span.innerText = 'Log In';
                const existingImg = sidebarLoginBtn.querySelector('img');
                if (existingImg) existingImg.remove();

                if (!sidebarLoginBtn.querySelector('svg')) {
                    const newSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    newSvg.setAttribute("viewBox", "0 0 24 24");
                    newSvg.setAttribute("stroke", "currentColor");
                    newSvg.setAttribute("stroke-width", "2");
                    newSvg.setAttribute("fill", "none");
                    newSvg.innerHTML = '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />';
                    sidebarLoginBtn.prepend(newSvg);
                }
            }
        }

        // 2. Update Header Profile Button
        const headerProfileBtns = document.querySelectorAll('.user-profile');
        headerProfileBtns.forEach(btn => {
            const svg = btn.querySelector('svg');

            if (user) {
                let img = btn.querySelector('img');
                if (user.avatar_url && user.avatar_url.length > 50) {
                    if (!img) {
                        img = document.createElement('img');
                        // Styling for header profile image
                        img.style.width = '20px';
                        img.style.height = '20px'; // Match svg size
                        img.style.borderRadius = '50%';
                        img.style.objectFit = 'cover';

                        if (svg) svg.replaceWith(img);
                        else btn.appendChild(img);
                    } else {
                        if (svg) svg.remove(); // specific cleanup
                    }
                    img.src = user.avatar_url;
                }
            } else {
                // Reset Header Button
                const existingImg = btn.querySelector('img');
                if (existingImg) existingImg.remove();

                if (!btn.querySelector('svg')) {
                    const newSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    newSvg.setAttribute("viewBox", "0 0 24 24");
                    newSvg.setAttribute("width", "20");
                    newSvg.setAttribute("height", "20");
                    newSvg.setAttribute("fill", "white");
                    newSvg.innerHTML = '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />';
                    btn.appendChild(newSvg);
                }
            }
        });

        // 3. Update Welcome Screen
        const welcomeMessage = document.getElementById('welcome-message');
        const welcomeAvatar = document.getElementById('welcome-avatar');

        if (welcomeMessage) {
            if (user) {
                const name = user.full_name || "User";
                welcomeMessage.innerText = `Welcome back, ${name}`;

                if (welcomeAvatar) {
                    if (user.avatar_url && user.avatar_url.length > 50) {
                        welcomeAvatar.style.display = 'block';
                        welcomeAvatar.querySelector('img').src = user.avatar_url;
                    } else {
                        welcomeAvatar.style.display = 'none';
                    }
                }
            } else {
                welcomeMessage.innerText = 'Where should we begin?';
                if (welcomeAvatar) welcomeAvatar.style.display = 'none';
            }
        }
        // 4. Update Settings Button Visibility
        const settingsTrigger = document.getElementById('settings-trigger');
        if (settingsTrigger) {
            settingsTrigger.style.display = user ? 'flex' : 'none';
        }
    }

    // Check login state on load
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        try {
            const user = JSON.parse(storedUser);
            updateUserInterface(user);
        } catch (e) {
            console.error("Error parsing user data", e);
        }
    }

    const settingsTrigger = document.getElementById('settings-trigger');
    if (settingsTrigger) {
        settingsTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            if (userMenu) {
                const isVisible = userMenu.style.display === 'block';
                userMenu.style.display = isVisible ? 'none' : 'block';
            }
        });
    }

    if (authTriggerBtns.length > 0) {
        authTriggerBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const currentUser = localStorage.getItem('user');

                if (currentUser) {
                    // Toggle User Menu
                    if (userMenu) {
                        const isVisible = userMenu.style.display === 'block';
                        userMenu.style.display = isVisible ? 'none' : 'block';
                    }
                } else {
                    openAuthModal();
                }
            });
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            updateUserInterface(null);
            if (userMenu) userMenu.style.display = 'none';
        });
    }

    // Change Name Logic
    const changeNameBtn = document.getElementById('change-name-btn');
    if (changeNameBtn) {
        changeNameBtn.addEventListener('click', () => {
            if (userMenu) userMenu.style.display = 'none';

            const storedUser = localStorage.getItem('user');
            if (!storedUser) return;

            const user = JSON.parse(storedUser);
            const currentName = user.full_name || "User";
            const newName = prompt("Enter your new name:", currentName);

            if (newName && newName.trim() !== "" && newName !== currentName) {
                const updatedName = newName.trim();

                // Update Local UI Immediately
                user.full_name = updatedName;
                localStorage.setItem('user', JSON.stringify(user));
                updateUserInterface(user);

                // Send to Backend
                fetch('/update_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: user.id,
                        full_name: updatedName
                    })
                })
                    .then(res => res.json())
                    .then(data => {
                        console.log("Name updated on server:", data);
                    })
                    .catch(err => console.error("Error updating name:", err));
            }
        });
    }

    // Change Avatar Logic
    const changeAvatarBtn = document.getElementById('change-avatar-btn');
    const updateAvatarInput = document.getElementById('update-avatar-input');

    if (changeAvatarBtn && updateAvatarInput) {
        changeAvatarBtn.addEventListener('click', () => {
            updateAvatarInput.click();
            // Close menu
            if (userMenu) userMenu.style.display = 'none';
        });

        updateAvatarInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (event) {
                const img = new Image();
                img.onload = function () {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    // Resize to thumbnail
                    const MAX_SIZE = 150; // Increased resolution slightly
                    let sourceX, sourceY, sourceWidth, sourceHeight;

                    // Calculate crop
                    if (img.width > img.height) {
                        sourceHeight = img.height;
                        sourceWidth = img.height;
                        sourceX = (img.width - img.height) / 2;
                        sourceY = 0;
                    } else {
                        sourceWidth = img.width;
                        sourceHeight = img.width;
                        sourceX = 0;
                        sourceY = (img.height - img.width) / 2;
                    }

                    canvas.width = MAX_SIZE;
                    canvas.height = MAX_SIZE;

                    // Draw cut
                    ctx.drawImage(img, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, MAX_SIZE, MAX_SIZE);

                    const dataUrl = canvas.toDataURL('image/jpeg', 0.7);

                    // Update Local UI
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        const user = JSON.parse(storedUser);
                        user.avatar_url = dataUrl;
                        localStorage.setItem('user', JSON.stringify(user));
                        updateUserInterface(user);

                        // Send to Backend
                        fetch('/update_profile', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_id: user.id,
                                avatar_url: dataUrl
                            })
                        }).catch(err => console.error("Error updating profile:", err));
                    }
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle-btn');

    function applyTheme(isLight) {
        if (isLight) {
            document.body.classList.add('light-mode');
            if (themeToggleBtn) {
                themeToggleBtn.querySelector('span').innerText = 'Dark Mode';
                // Optionally update icon here if you want to swap sun/moon
            }
        } else {
            document.body.classList.remove('light-mode');
            if (themeToggleBtn) {
                themeToggleBtn.querySelector('span').innerText = 'Light Mode';
            }
        }
    }

    // Check saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        applyTheme(true);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isLight = document.body.classList.toggle('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            applyTheme(isLight);
            // Close menu
            if (userMenu) userMenu.style.display = 'none';
        });
    }

    // Close menu when clicking outside
    window.addEventListener('click', (e) => {
        // If click is NOT inside sidebar footer or button
        if (!e.target.closest('.sidebar-footer') && userMenu && userMenu.style.display === 'block') {
            userMenu.style.display = 'none';
        }
    });

    if (closeAuthBtn) {
        closeAuthBtn.addEventListener('click', closeAuthModal);
    }

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            closeAuthModal();
        }
    });

    if (toggleAuthModeBtn) {
        toggleAuthModeBtn.addEventListener('click', () => {
            isLoginMode = !isLoginMode;
            if (isLoginMode) {
                authTitle.innerText = 'Welcome Back';
                authSubtitle.innerText = 'Sign in to continue to GlobleXGPT';
                authSubmitBtn.innerText = 'Sign In';
                toggleAuthModeBtn.innerText = 'Sign up';
                if (authSwitchText.firstChild) authSwitchText.firstChild.textContent = "Don't have an account? ";
                nameGroup.style.display = 'none';
                avatarGroup.style.display = 'none';
                document.getElementById('full-name').removeAttribute('required');
            } else {
                authTitle.innerText = 'Create Account';
                authSubtitle.innerText = 'Join GlobleXGPT today';
                authSubmitBtn.innerText = 'Sign Up';
                toggleAuthModeBtn.innerText = 'Sign in';
                if (authSwitchText.firstChild) authSwitchText.firstChild.textContent = "Already have an account? ";
                nameGroup.style.display = 'flex';
                avatarGroup.style.display = 'flex';
                avatarGroup.style.flexDirection = 'column'; // Ensure vertical layout
                document.getElementById('full-name').setAttribute('required', 'true');
            }
        });
    }

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const fullName = document.getElementById('full-name').value;
            const avatarUrl = document.getElementById('avatar-base64').value; // Get base64 string

            authMessage.innerText = 'Processing...';
            authMessage.className = 'auth-message';

            const endpoint = isLoginMode ? '/login' : '/signup';
            const payload = { email, password };
            if (!isLoginMode) {
                payload.full_name = fullName;
                payload.avatar_url = avatarUrl;
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    authMessage.innerText = data.message || 'Success!';
                    authMessage.className = 'auth-message success';

                    if (isLoginMode) {
                        // Store token
                        localStorage.setItem('access_token', data.access_token);
                        if (data.user) {
                            localStorage.setItem('user', JSON.stringify(data.user));
                            updateUserInterface(data.user);
                        }

                        setTimeout(() => {
                            closeAuthModal();
                        }, 1000);
                    } else {
                        // Signup success - usually requires email verification or auto-login
                        // If auto-login isn't implemented server-side, just tell them to check email
                    }
                } else {
                    authMessage.innerText = data.error || 'An error occurred';
                    authMessage.className = 'auth-message error';
                }
            } catch (err) {
                authMessage.innerText = 'Network error. check console.';
                authMessage.className = 'auth-message error';
                console.error(err);
            }
        });
    }
});
