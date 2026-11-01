/**
 * Indian Sign Language (ISL) Translator - Professional Web Client
 * Real-Time Video-to-Text and Voice Translation (English & Hindi)
 * Includes User Authentication (Login/Register), MongoDB Stories Storage,
 * and seamless Guest Mode.
 */

// Comprehensive Real-Time Bilingual Vocabulary (165 ISLRTC Gestures)
const ISL_REALTIME_VOCAB = {
  // 1. Module 1.2: Greetings and Salutations
  "Namaste": { en: "Namaste / Hello", hi: "नमस्ते" },
  "Hello": { en: "Hello", hi: "हैलो" },
  "Good Morning": { en: "Good morning", hi: "सुप्रभात" },
  "Good Afternoon": { en: "Good afternoon", hi: "शुभ दोपहर" },
  "Good Evening": { en: "Good evening", hi: "शुभ संध्या" },
  "Good Night": { en: "Good night", hi: "शुभ रात्रि" },
  "Welcome": { en: "Welcome", hi: "आपका स्वागत है" },
  "How are you": { en: "How are you?", hi: "आप कैसे हैं?" },
  "Fine": { en: "I am fine", hi: "मैं ठीक हूँ" },
  "Nice to meet you": { en: "Nice to meet you", hi: "आपसे मिलकर खुशी हुई" },
  "Goodbye": { en: "Goodbye", hi: "अलविदा" },
  "Sorry": { en: "Sorry, excuse me", hi: "माफ़ कीजिए" },
  "Thank You": { en: "Thank you", hi: "धन्यवाद" },
  "Please": { en: "Please", hi: "कृपया" },

  // 2. Module 1.3: Polite & Useful Phrases
  "Excuse me": { en: "Excuse me", hi: "माफ़ कीजिए" },
  "Congratulations": { en: "Congratulations!", hi: "बधाई हो!" },
  "See you later": { en: "See you later", hi: "फिर मिलेंगे" },
  "Take care": { en: "Take care", hi: "ख्याल रखना" },
  "All the best": { en: "All the best", hi: "शुभकामनाएँ" },
  "Safe": { en: "Safe", hi: "सुरक्षित" },

  // 3. Pronouns & Questions
  "Me": { en: "Me / I", hi: "मैं / मुझे" },
  "You": { en: "You", hi: "आप / तुम" },
  "We": { en: "We", hi: "हम सब" },
  "They": { en: "They", hi: "वे लोग" },
  "What": { en: "What?", hi: "क्या?" },
  "Where": { en: "Where?", hi: "कहाँ?" },
  "Who": { en: "Who?", hi: "कौन?" },
  "When": { en: "When?", hi: "कब?" },
  "Why": { en: "Why?", hi: "क्यों?" },
  "How": { en: "How?", hi: "कैसे?" },
  "Which": { en: "Which?", hi: "कौन सा?" },
  "Whose": { en: "Whose?", hi: "किसका?" },
  "How many": { en: "How many?", hi: "कितने?" },

  // 4. Emergency, Health & Safety
  "Help": { en: "Please help me", hi: "मेरी मदद कीजिए" },
  "Doctor": { en: "Doctor", hi: "डॉक्टर" },
  "Hospital": { en: "Hospital", hi: "अस्पताल" },
  "Medicine": { en: "Medicine", hi: "दवाई" },
  "Pain": { en: "Pain / Hurt", hi: "दर्द" },
  "Sick": { en: "Sick / Fever", hi: "बीमार / बुखार" },
  "Police": { en: "Police", hi: "पुलिस" },
  "Emergency": { en: "Emergency", hi: "आपातकाल" },
  "Danger": { en: "Danger", hi: "खतरा" },

  // 5. Family & Daily Relations
  "Father": { en: "Father", hi: "पिताजी" },
  "Mother": { en: "Mother", hi: "माताजी" },
  "Brother": { en: "Brother", hi: "भाई" },
  "Sister": { en: "Sister", hi: "बहन" },
  "Friend": { en: "Friend", hi: "दोस्त" },
  "Teacher": { en: "Teacher", hi: "शिक्षक" },
  "Family": { en: "Family", hi: "परिवार" },
  "Child": { en: "Child", hi: "बच्चा" },
  "Son": { en: "Son", hi: "बेटा" },
  "Daughter": { en: "Daughter", hi: "बेटी" },
  "Grandfather": { en: "Grandfather", hi: "दादाजी" },
  "Grandmother": { en: "Grandmother", hi: "दादीजी" },
  "Husband": { en: "Husband", hi: "पति" },
  "Wife": { en: "Wife", hi: "पत्नी" },

  // 6. Food, Dining & Needs
  "Water": { en: "Water", hi: "पानी" },
  "Food": { en: "Food / Eat", hi: "खाना" },
  "Drink": { en: "Drink", hi: "पीना" },
  "Tea": { en: "Tea", hi: "चाय" },
  "Milk": { en: "Milk", hi: "दूध" },
  "Coffee": { en: "Coffee", hi: "कॉफी" },
  "Bread": { en: "Bread / Roti", hi: "रोटी" },
  "Rice": { en: "Rice", hi: "चावल" },
  "Vegetable": { en: "Vegetable", hi: "सब्जी" },
  "Fruit": { en: "Fruit", hi: "फल" },
  "Hungry": { en: "I am hungry", hi: "मुझे भूख लगी है" },
  "Thirsty": { en: "I am thirsty", hi: "मुझे प्यास लगी है" },

  // 7. Feelings & Emotions
  "Happy": { en: "Happy", hi: "खुश" },
  "Sad": { en: "Sad", hi: "उदास" },
  "Angry": { en: "Angry", hi: "गुस्सा" },
  "Scared": { en: "Scared / Afraid", hi: "डरा हुआ" },
  "Surprise": { en: "Surprised", hi: "आश्चर्यचकित" },
  "Like": { en: "I like it", hi: "पसंद है" },
  "Dislike": { en: "I dislike it", hi: "नापसंद" },
  "Good": { en: "Good", hi: "अच्छा" },
  "Bad": { en: "Bad", hi: "बुरा" },
  "Tired": { en: "Tired", hi: "थका हुआ" },
  "Excited": { en: "Excited", hi: "उत्साहित" },
  "Bored": { en: "Bored", hi: "ऊब गया" },
  "Proud": { en: "Proud", hi: "गर्व" },
  "Confused": { en: "Confused", hi: "भ्रमित" },
  "I Love You": { en: "I Love You", hi: "मैं आपसे प्यार करता हूँ" },

  // 8. Everyday Verbs & Actions
  "Go": { en: "Go", hi: "जाओ" },
  "Come": { en: "Come", hi: "आओ" },
  "Sit": { en: "Sit down", hi: "बैठो" },
  "Stand": { en: "Stand up", hi: "खड़े रहो" },
  "Wait": { en: "Please wait", hi: "प्रतीक्षा करें" },
  "Work": { en: "Work / Job", hi: "काम" },
  "Study": { en: "Study / Learn", hi: "पढ़ाई" },
  "Understand": { en: "I understand", hi: "समझ गया" },
  "Sleep": { en: "Sleep", hi: "सोना" },
  "Read": { en: "Read", hi: "पढ़ना" },
  "Write": { en: "Write", hi: "लिखना" },
  "Speak": { en: "Speak", hi: "बोलना" },
  "Listen": { en: "Listen", hi: "सुनना" },
  "See": { en: "See / Look", hi: "देखना" },
  "Buy": { en: "Buy", hi: "खरीदना" },
  "Sell": { en: "Sell", hi: "बेचना" },
  "Give": { en: "Give", hi: "देना" },
  "Take": { en: "Take", hi: "लेना" },

  // 9. Places, Time & Daily Objects
  "Home": { en: "Home / House", hi: "घर" },
  "School": { en: "School", hi: "स्कूल" },
  "Office": { en: "Office", hi: "दफ्तर" },
  "Shop": { en: "Shop / Market", hi: "दुकान" },
  "Bus": { en: "Bus", hi: "बस" },
  "Train": { en: "Train", hi: "ट्रेन" },
  "Car": { en: "Car", hi: "कार" },
  "Book": { en: "Book", hi: "किताब" },
  "Pen": { en: "Pen", hi: "कलम" },
  "Phone": { en: "Phone", hi: "फ़ोन" },
  "Money": { en: "Money / Cash", hi: "पैसे" },
  "Time": { en: "Time", hi: "समय" },
  "Today": { en: "Today", hi: "आज" },
  "Tomorrow": { en: "Tomorrow", hi: "कल (आने वाला)" },
  "Yesterday": { en: "Yesterday", hi: "कल (बीता हुआ)" },
  "Morning": { en: "Morning", hi: "सुबह" },
  "Evening": { en: "Evening", hi: "शाम" },
  "Night": { en: "Night", hi: "रात" },
  "Monday": { en: "Monday", hi: "सोमवार" },
  "Tuesday": { en: "Tuesday", hi: "मंगलवार" },
  "Wednesday": { en: "Wednesday", hi: "बुधवार" },
  "Thursday": { en: "Thursday", hi: "गुरुवार" },
  "Friday": { en: "Friday", hi: "शुक्रवार" },
  "Saturday": { en: "Saturday", hi: "शनिवार" },
  "Sunday": { en: "Sunday", hi: "रविवार" },

  // 10. Control Tokens
  "Yes": { en: "Yes", hi: "हाँ" },
  "No": { en: "No", hi: "नहीं" },
  "Stop": { en: "Stop", hi: "रुकिए" },
  "Space": { en: "Space", hi: "स्थान" },
  "Backspace": { en: "Backspace", hi: "हटाएँ" }
};

// Add standard Alphabet A-Z & Numbers 0-10
for (let i = 65; i <= 90; i++) {
  const char = String.fromCharCode(i);
  ISL_REALTIME_VOCAB[char] = { en: `Letter ${char}`, hi: `अक्षर ${char}` };
}
for (let n = 0; n <= 10; n++) {
  ISL_REALTIME_VOCAB[String(n)] = { en: `Number ${n}`, hi: `संख्या ${n}` };
}


class ISLApp {
  constructor() {
    this.pollInterval = null;
    this.autoSpeak = true;
    this.speechSynthesis = window.speechSynthesis;
    this.speechRate = 1.0;

    // Dual-Language Voice Configuration
    this.selectedVoiceLang = 'hindi'; // Default to Hindi
    this.speechMode = 'instant';      // 'instant' | 'sentence' | 'story'
    this.activeStoryLang = 'english'; // 'english' | 'hindi'

    this.lastSpokenGesture = "";
    this.lastSpokenGestureTime = 0;
    this.lastSpokenSentence = "";

    // Browser camera fallback state
    this.useBrowserCamera = false;
    this.browserStream = null;
    this.processFrameInterval = null;

    // User authentication state
    this.currentUser = null;
    this.authMode = 'login'; // 'login' | 'register'

    this.initElements();
    this.initVoices();
    this.initEventListeners();
    this.checkAuthStatus();
    this.startStatusPolling();
  }

  initElements() {
    // Header Auth Elements
    this.authHeaderGuest = document.getElementById('authHeaderGuest');
    this.authHeaderUser = document.getElementById('authHeaderUser');
    this.headerUsername = document.getElementById('headerUsername');
    this.userStoriesCount = document.getElementById('userStoriesCount');
    this.btnOpenAuthModal = document.getElementById('btnOpenAuthModal');
    this.btnLogout = document.getElementById('btnLogout');
    this.btnOpenSavedStories = document.getElementById('btnOpenSavedStories');

    // Live Video Elements
    this.videoStreamImg = document.getElementById('videoStreamImg');
    this.browserVideo = document.getElementById('browserVideo');
    this.browserCanvas = document.getElementById('browserCanvas');
    this.cameraSourceSelect = document.getElementById('cameraSourceSelect');

    // Real-Time Detection Badges
    this.heroSignChar = document.getElementById('heroSignChar');
    this.heroSignHindi = document.getElementById('heroSignHindi');
    this.heroSignDesc = document.getElementById('heroSignDesc');
    this.confidenceBar = document.getElementById('confidenceBar');
    this.confidenceVal = document.getElementById('confidenceVal');
    this.stabilityBadge = document.getElementById('stabilityBadge');
    this.topCandidatesList = document.getElementById('topCandidatesList');

    // Live Sentence Building Elements
    this.currentWordBadge = document.getElementById('currentWordBadge');
    this.liveSentenceRaw = document.getElementById('liveSentenceRaw');
    this.liveSentencePolished = document.getElementById('liveSentencePolished');
    this.liveSentenceHindi = document.getElementById('liveSentenceHindi');

    // Full Story Elements
    this.storyEnglishText = document.getElementById('storyEnglishText');
    this.storyHindiText = document.getElementById('storyHindiText');
    this.storySentencesTimeline = document.getElementById('storySentencesTimeline');
    this.storyWordCount = document.getElementById('storyWordCount');
    this.storySentenceCount = document.getElementById('storySentenceCount');

    // Action Buttons
    this.btnNarrateStory = document.getElementById('btnNarrateStory');
    this.btnSaveStory = document.getElementById('btnSaveStory');
    this.btnSpeakCurrentSentence = document.getElementById('btnSpeakCurrentSentence');
    this.btnEndSentence = document.getElementById('btnEndSentence');
    this.btnAddSpace = document.getElementById('btnAddSpace');
    this.btnBackspace = document.getElementById('btnBackspace');
    this.btnClearStory = document.getElementById('btnClearStory');
    this.btnCopyStory = document.getElementById('btnCopyStory');
    this.btnExportStory = document.getElementById('btnExportStory');
    this.btnLoadDemoStory = document.getElementById('btnLoadDemoStory');

    // Video File Translator Elements
    this.videoFileInput = document.getElementById('videoFileInput');
    this.btnUploadVideo = document.getElementById('btnUploadVideo');
    this.videoUploadStatus = document.getElementById('videoUploadStatus');

    // Settings
    this.speechModeSelect = document.getElementById('speechModeSelect');
    this.autoSpeakToggle = document.getElementById('autoSpeakToggle');
    this.storyLangTabs = document.querySelectorAll('.story-lang-tab');
    this.rateSlider = document.getElementById('rateSlider');
    this.rateVal = document.getElementById('rateVal');

    // Auth Modal Elements
    this.authModal = document.getElementById('authModal');
    this.btnCloseAuthModal = document.getElementById('btnCloseAuthModal');
    this.btnContinueGuest = document.getElementById('btnContinueGuest');
    this.tabAuthLogin = document.getElementById('tabAuthLogin');
    this.tabAuthRegister = document.getElementById('tabAuthRegister');
    this.authModalTitle = document.getElementById('authModalTitle');
    this.authEmailGroup = document.getElementById('authEmailGroup');
    this.authUsername = document.getElementById('authUsername');
    this.authEmail = document.getElementById('authEmail');
    this.authPassword = document.getElementById('authPassword');
    this.btnSubmitAuth = document.getElementById('btnSubmitAuth');
    this.authErrorNotice = document.getElementById('authErrorNotice');
    this.authForm = document.getElementById('authForm');

    // Save Story Modal Elements
    this.saveStoryModal = document.getElementById('saveStoryModal');
    this.btnCloseSaveModal = document.getElementById('btnCloseSaveModal');
    this.btnCancelSave = document.getElementById('btnCancelSave');
    this.btnConfirmSaveStory = document.getElementById('btnConfirmSaveStory');
    this.saveStoryTitle = document.getElementById('saveStoryTitle');
    this.saveStoryPreview = document.getElementById('saveStoryPreview');

    // Saved Stories Modal Elements
    this.storiesModal = document.getElementById('storiesModal');
    this.btnCloseStoriesModal = document.getElementById('btnCloseStoriesModal');
    this.btnCloseStoriesModalBottom = document.getElementById('btnCloseStoriesModalBottom');
    this.savedStoriesList = document.getElementById('savedStoriesList');
    this.savedStoriesCounterBadge = document.getElementById('savedStoriesCounterBadge');

    // Toast
    this.toast = document.getElementById('toastNotice');
    this.toastMsg = document.getElementById('toastNoticeMsg');
  }

  initVoices() {
    if (!this.speechSynthesis) return;
    if (this.speechSynthesis.onvoiceschanged !== undefined) {
      this.speechSynthesis.onvoiceschanged = () => {};
    }
  }

  initEventListeners() {
    // Story View Language Tabs (English vs Hindi view)
    this.storyLangTabs.forEach(btn => {
      btn.addEventListener('click', () => {
        this.storyLangTabs.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.activeStoryLang = btn.dataset.lang;

        if (this.activeStoryLang === 'hindi') {
          this.storyEnglishText?.classList.add('hidden');
          this.storyHindiText?.classList.remove('hidden');
        } else {
          this.storyHindiText?.classList.add('hidden');
          this.storyEnglishText?.classList.remove('hidden');
        }
      });
    });

    // Story Narration (Read Aloud)
    this.btnNarrateStory?.addEventListener('click', () => {
      const text = (this.activeStoryLang === 'hindi')
        ? (this.storyHindiText?.textContent || "")
        : (this.storyEnglishText?.textContent || "");

      if (text.trim() && !text.includes("Your continuous story will weave together here") && !text.includes("पूरी कहानी का हिंदी")) {
        this.speakText(text.trim(), this.activeStoryLang);
      } else {
        const live = (this.selectedVoiceLang === 'hindi')
          ? (this.liveSentenceHindi?.textContent || "")
          : (this.liveSentencePolished?.textContent || "");
        if (live.trim()) {
          this.speakText(live.trim(), this.selectedVoiceLang);
        } else {
          this.showToast("Story is empty. Sign sentences or load sample story.", "info");
        }
      }
    });

    // Save Story Button
    this.btnSaveStory?.addEventListener('click', () => {
      this.openSaveStoryModal();
    });

    // Speak Current Sentence
    this.btnSpeakCurrentSentence?.addEventListener('click', () => {
      const live = (this.selectedVoiceLang === 'hindi')
        ? (this.liveSentenceHindi?.textContent || "")
        : (this.liveSentencePolished?.textContent || "");
      if (live.trim() && !live.includes("Waiting for") && !live.includes("प्रतीक्षा")) {
        this.speakText(live.trim(), this.selectedVoiceLang);
      } else {
        this.showToast("No active sentence to speak.", "info");
      }
    });

    // End Sentence & Add to Story
    this.btnEndSentence?.addEventListener('click', async () => {
      const res = await fetch('/api/story/end_sentence', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.finalized_sentence) {
          this.showToast("Sentence added to story!", "success");
        }
        this.fetchStatusOnce();
      }
    });

    // Space & Backspace
    this.btnAddSpace?.addEventListener('click', async () => {
      await fetch('/api/sentence/space', { method: 'POST' });
      this.fetchStatusOnce();
    });

    this.btnBackspace?.addEventListener('click', async () => {
      await fetch('/api/sentence/backspace', { method: 'POST' });
      this.fetchStatusOnce();
    });

    // Clear Story
    this.btnClearStory?.addEventListener('click', async () => {
      if (confirm("Reset the entire story and start a fresh narrative?")) {
        await fetch('/api/story/clear', { method: 'POST' });
        this.fetchStatusOnce();
        this.showToast("Story cleared.", "info");
      }
    });

    // Copy Story
    this.btnCopyStory?.addEventListener('click', () => {
      const text = this.storyEnglishText?.textContent || "";
      const hiText = this.storyHindiText?.textContent || "";
      if (text.trim() && !text.includes("Your continuous story will weave together here")) {
        const fullContent = `INDIAN SIGN LANGUAGE STORY\n\nEnglish:\n${text}\n\nHindi:\n${hiText}\n`;
        navigator.clipboard.writeText(fullContent);
        this.showToast("Copied story to clipboard!", "success");
      } else {
        this.showToast("Story is empty.", "info");
      }
    });

    // Export Story
    this.btnExportStory?.addEventListener('click', () => {
      this.exportStoryFile();
    });

    // Load Demo Story
    this.btnLoadDemoStory?.addEventListener('click', async () => {
      const res = await fetch('/api/story/load_sample', { method: 'POST' });
      if (res.ok) {
        this.fetchStatusOnce();
        this.showToast("Sample story loaded! Click 'Read Full Story Aloud' to listen.", "success");
      }
    });

    // Upload & Translate Video File
    this.btnUploadVideo?.addEventListener('click', () => {
      this.videoFileInput?.click();
    });

    this.videoFileInput?.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('video', file);

      this.showToast(`Processing '${file.name}'... Please wait.`, "info");
      if (this.videoUploadStatus) {
        this.videoUploadStatus.classList.remove('hidden');
      }

      try {
        const res = await fetch('/api/video/upload_translate', {
          method: 'POST',
          body: formData
        });

        const data = await res.json();
        if (data.success) {
          this.fetchStatusOnce();
          this.showToast(`Translated video! (${data.sentence_count} sentences extracted)`, "success");
          const spoken = (this.selectedVoiceLang === 'hindi') ? data.story_hindi : data.story_english;
          if (spoken) {
            this.speakText(spoken, this.selectedVoiceLang);
          }
        } else {
          this.showToast(`Translation error: ${data.error || 'Failed to process'}`, "danger");
        }
      } catch (err) {
        this.showToast(`Upload failed: ${err.message}`, "danger");
      } finally {
        if (this.videoUploadStatus) {
          this.videoUploadStatus.classList.add('hidden');
        }
        this.videoFileInput.value = '';
      }
    });

    // Speech Timing Mode Select
    this.speechModeSelect?.addEventListener('change', (e) => {
      this.speechMode = e.target.value;
      fetch('/api/settings/speech_mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: this.speechMode })
      });
      this.showToast(`Voice timing set to: ${this.speechMode}`);
    });

    // Auto-Speak Checkbox Toggle
    this.autoSpeakToggle?.addEventListener('change', (e) => {
      this.autoSpeak = e.target.checked;
      fetch('/api/settings/auto_speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: this.autoSpeak })
      });
      this.showToast(`Auto-speak ${this.autoSpeak ? 'enabled' : 'disabled'}`);
    });

    // Speech Rate Slider
    this.rateSlider?.addEventListener('input', (e) => {
      this.speechRate = parseFloat(e.target.value);
      if (this.rateVal) this.rateVal.textContent = `${this.speechRate.toFixed(1)}x`;
    });

    // Camera Source Dropdown (Server OpenCV vs Browser WebRTC)
    this.cameraSourceSelect?.addEventListener('change', (e) => {
      if (e.target.value === 'browser') {
        this.startBrowserCamera();
      } else {
        this.stopBrowserCamera();
      }
    });

    // Auth Modal Triggers
    this.btnOpenAuthModal?.addEventListener('click', () => this.openAuthModal('login'));
    this.btnCloseAuthModal?.addEventListener('click', () => this.closeAuthModal());
    this.btnContinueGuest?.addEventListener('click', () => this.closeAuthModal());
    this.tabAuthLogin?.addEventListener('click', () => this.switchAuthMode('login'));
    this.tabAuthRegister?.addEventListener('click', () => this.switchAuthMode('register'));
    this.btnSubmitAuth?.addEventListener('click', () => this.handleAuthSubmit());
    this.btnLogout?.addEventListener('click', () => this.handleLogout());

    // Save Story Modal Triggers
    this.btnCloseSaveModal?.addEventListener('click', () => this.closeSaveStoryModal());
    this.btnCancelSave?.addEventListener('click', () => this.closeSaveStoryModal());
    this.btnConfirmSaveStory?.addEventListener('click', () => this.confirmSaveStory());

    // Saved Stories Modal Triggers
    this.btnOpenSavedStories?.addEventListener('click', () => this.openStoriesModal());
    this.btnCloseStoriesModal?.addEventListener('click', () => this.closeStoriesModal());
    this.btnCloseStoriesModalBottom?.addEventListener('click', () => this.closeStoriesModal());
  }

  // ================= USER AUTHENTICATION LOGIC =================

  async checkAuthStatus() {
    try {
      const res = await fetch('/api/auth/me');
      const data = await res.json();
      if (data.logged_in && data.user) {
        this.currentUser = data.user;
        this.renderAuthState(true);
        this.updateStoriesCount();
      } else {
        this.currentUser = null;
        this.renderAuthState(false);
      }
    } catch (e) {
      this.currentUser = null;
      this.renderAuthState(false);
    }
  }

  renderAuthState(isLoggedIn) {
    if (isLoggedIn && this.currentUser) {
      this.authHeaderGuest?.classList.add('hidden');
      this.authHeaderUser?.classList.remove('hidden');
      if (this.headerUsername) {
        this.headerUsername.textContent = this.currentUser.username;
      }
    } else {
      this.authHeaderUser?.classList.add('hidden');
      this.authHeaderGuest?.classList.remove('hidden');
    }
  }

  openAuthModal(mode = 'login') {
    this.switchAuthMode(mode);
    this.hideAuthError();
    this.authModal?.classList.add('show');
    setTimeout(() => this.authUsername?.focus(), 100);
  }

  closeAuthModal() {
    this.authModal?.classList.remove('show');
  }

  switchAuthMode(mode) {
    this.authMode = mode;
    this.hideAuthError();
    if (mode === 'login') {
      if (this.authModalTitle) this.authModalTitle.textContent = "Sign In to Your Account";
      this.tabAuthLogin?.classList.add('border-b-2', 'border-blue-500', 'text-white');
      this.tabAuthLogin?.classList.remove('text-slate-400');
      this.tabAuthRegister?.classList.remove('border-b-2', 'border-blue-500', 'text-white');
      this.tabAuthRegister?.classList.add('text-slate-400');
      this.authEmailGroup?.classList.add('hidden');
      if (this.btnSubmitAuth) this.btnSubmitAuth.textContent = "Sign In";
    } else {
      if (this.authModalTitle) this.authModalTitle.textContent = "Create New Account";
      this.tabAuthRegister?.classList.add('border-b-2', 'border-blue-500', 'text-white');
      this.tabAuthRegister?.classList.remove('text-slate-400');
      this.tabAuthLogin?.classList.remove('border-b-2', 'border-blue-500', 'text-white');
      this.tabAuthLogin?.classList.add('text-slate-400');
      this.authEmailGroup?.classList.remove('hidden');
      if (this.btnSubmitAuth) this.btnSubmitAuth.textContent = "Create Account";
    }
  }

  async handleAuthSubmit() {
    const username = this.authUsername?.value?.trim();
    const password = this.authPassword?.value;
    const email = this.authEmail?.value?.trim();

    if (!username || !password) {
      this.showAuthError("Please provide both username and password.");
      return;
    }

    const endpoint = (this.authMode === 'login') ? '/api/auth/login' : '/api/auth/register';
    const payload = { username, password, email };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        this.currentUser = { user_id: data.user_id, username: data.username, email: data.email };
        this.renderAuthState(true);
        this.closeAuthModal();
        this.showToast(this.authMode === 'login' ? `Welcome, ${data.username}!` : `Account created! Welcome, ${data.username}!`, "success");
        this.updateStoriesCount();
        if (this.authUsername) this.authUsername.value = '';
        if (this.authPassword) this.authPassword.value = '';
        if (this.authEmail) this.authEmail.value = '';
      } else {
        this.showAuthError(data.error || "Authentication failed.");
      }
    } catch (e) {
      this.showAuthError(`Server connection error: ${e.message}`);
    }
  }

  async handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    this.currentUser = null;
    this.renderAuthState(false);
    this.showToast("Logged out. Continuing as guest.", "info");
  }

  showAuthError(msg) {
    if (this.authErrorNotice) {
      this.authErrorNotice.textContent = msg;
      this.authErrorNotice.classList.remove('hidden');
    }
  }

  hideAuthError() {
    if (this.authErrorNotice) {
      this.authErrorNotice.classList.add('hidden');
      this.authErrorNotice.textContent = '';
    }
  }

  // ================= MONGODB STORY MANAGEMENT =================

  openSaveStoryModal() {
    if (!this.currentUser) {
      this.showToast("Please log in or register to save your stories in MongoDB.", "info");
      this.openAuthModal('login');
      return;
    }

    const eng = (this.storyEnglishText?.textContent || "").trim();
    if (!eng || eng.includes("Your continuous story will weave together here")) {
      this.showToast("Story is empty. Sign sentences before saving.", "info");
      return;
    }

    const firstFew = eng.split(/\s+/).slice(0, 5).join(' ');
    if (this.saveStoryTitle) {
      this.saveStoryTitle.value = `${firstFew}...`;
    }
    if (this.saveStoryPreview) {
      this.saveStoryPreview.textContent = eng;
    }

    this.saveStoryModal?.classList.add('show');
    setTimeout(() => this.saveStoryTitle?.focus(), 100);
  }

  closeSaveStoryModal() {
    this.saveStoryModal?.classList.remove('show');
  }

  async confirmSaveStory() {
    const title = this.saveStoryTitle?.value?.trim() || "";
    try {
      const res = await fetch('/api/stories/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      const data = await res.json();
      if (data.success) {
        this.closeSaveStoryModal();
        this.showToast(`Story '${data.title}' saved to MongoDB Compass!`, "success");
        this.updateStoriesCount();
      } else {
        this.showToast(`Could not save story: ${data.error}`, "danger");
      }
    } catch (e) {
      this.showToast(`Save error: ${e.message}`, "danger");
    }
  }

  async updateStoriesCount() {
    if (!this.currentUser) return;
    try {
      const res = await fetch('/api/stories/list');
      if (res.ok) {
        const data = await res.json();
        if (data.success && this.userStoriesCount) {
          this.userStoriesCount.textContent = data.count || 0;
        }
      }
    } catch (e) {}
  }

  async openStoriesModal() {
    if (!this.currentUser) {
      this.openAuthModal('login');
      return;
    }
    this.storiesModal?.classList.add('show');
    await this.fetchUserStories();
  }

  closeStoriesModal() {
    this.storiesModal?.classList.remove('show');
  }

  async fetchUserStories() {
    if (!this.savedStoriesList) return;
    this.savedStoriesList.innerHTML = '<div class="text-center py-8 text-xs text-slate-500">Loading stories from MongoDB...</div>';

    try {
      const res = await fetch('/api/stories/list');
      const data = await res.json();
      if (data.success) {
        if (this.savedStoriesCounterBadge) {
          this.savedStoriesCounterBadge.textContent = `${data.count} stories`;
        }
        if (this.userStoriesCount) {
          this.userStoriesCount.textContent = data.count;
        }
        this.renderSavedStories(data.stories || []);
      } else {
        this.savedStoriesList.innerHTML = `<div class="text-center py-6 text-xs text-red-400">${data.error}</div>`;
      }
    } catch (e) {
      this.savedStoriesList.innerHTML = `<div class="text-center py-6 text-xs text-red-400">Error: ${e.message}</div>`;
    }
  }

  renderSavedStories(stories) {
    if (!this.savedStoriesList) return;

    if (stories.length === 0) {
      this.savedStoriesList.innerHTML = `
        <div class="text-center py-10 px-4 panel-card">
          <i class="fa-solid fa-folder-open text-3xl text-slate-600 mb-2 block"></i>
          <p class="text-sm font-semibold text-slate-300">No saved stories yet</p>
          <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Sign complete sentences to form a story, then click <strong class="text-emerald-400">"Save Story"</strong> to preserve it in your MongoDB database.
          </p>
        </div>
      `;
      return;
    }

    this.savedStoriesList.innerHTML = stories.map(st => `
      <div class="panel-card p-4 space-y-2.5 hover:border-slate-600 transition-colors">
        <div class="flex items-start justify-between gap-2">
          <div>
            <h4 class="text-sm font-bold text-white">${st.title}</h4>
            <div class="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
              <span><i class="fa-regular fa-clock mr-1"></i>${st.date_display}</span>
              <span>•</span>
              <span class="font-mono text-blue-300">${st.sentence_count} sentences</span>
              <span>•</span>
              <span class="font-mono text-slate-300">${st.word_count} words</span>
            </div>
          </div>
          <button class="btn btn-outline py-1 px-2 text-xs text-slate-400 hover:text-red-400"
            onclick="app.deleteSavedStory('${st.id}')" title="Delete from MongoDB">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>

        <div class="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs space-y-1">
          <p class="text-slate-200 leading-relaxed font-normal">${st.story_english}</p>
          <p class="text-blue-300 leading-relaxed font-hindi">${st.story_hindi}</p>
        </div>

        <div class="flex flex-wrap items-center gap-2 pt-1">
          <button class="btn btn-primary text-xs py-1.5 px-3" onclick="app.loadStoryIntoWorkspace('${st.id}')">
            <i class="fa-solid fa-folder-open mr-1"></i> Open in Workspace
          </button>
          <button class="btn btn-secondary text-xs py-1.5 px-3" onclick="app.speakText('${(this.selectedVoiceLang === 'hindi' ? st.story_hindi : st.story_english).replace(/'/g, "\\'")}', '${this.selectedVoiceLang}')">
            <i class="fa-solid fa-volume-high mr-1"></i> Read Aloud
          </button>
          <button class="btn btn-secondary text-xs py-1.5 px-3" onclick="navigator.clipboard.writeText('ENGLISH:\\n${st.story_english.replace(/'/g, "\\'")}\\n\\nHINDI:\\n${st.story_hindi.replace(/'/g, "\\'")}'); app.showToast('Copied story to clipboard!', 'success');">
            <i class="fa-regular fa-copy mr-1"></i> Copy
          </button>
        </div>
      </div>
    `).join('');
  }

  async loadStoryIntoWorkspace(storyId) {
    try {
      const res = await fetch(`/api/stories/load/${storyId}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        this.closeStoriesModal();
        this.fetchStatusOnce();
        this.showToast(`Loaded story into workspace!`, "success");
      } else {
        this.showToast(`Could not load story: ${data.error}`, "danger");
      }
    } catch (e) {
      this.showToast(`Load error: ${e.message}`, "danger");
    }
  }

  async deleteSavedStory(storyId) {
    if (!confirm("Are you sure you want to delete this story from MongoDB?")) return;

    try {
      const res = await fetch(`/api/stories/delete/${storyId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        this.showToast("Story deleted from database.", "info");
        await this.fetchUserStories();
        this.updateStoriesCount();
      } else {
        this.showToast(`Could not delete story: ${data.error}`, "danger");
      }
    } catch (e) {
      this.showToast(`Delete error: ${e.message}`, "danger");
    }
  }

  setVoiceLanguage(lang) {
    this.selectedVoiceLang = lang;
    const btnHi = document.getElementById('btnVoiceLangHindi');
    const btnEn = document.getElementById('btnVoiceLangEnglish');

    if (lang === 'hindi') {
      btnHi?.classList.add('active');
      btnEn?.classList.remove('active');
      this.showToast("Voice Language: Hindi (हिंदी आवाज़ सक्रिय)");
      this.speakText("हिंदी आवाज़", "hindi");
    } else {
      btnEn?.classList.add('active');
      btnHi?.classList.remove('active');
      this.showToast("Voice Language: English");
      this.speakText("English voice", "english");
    }
  }

  startStatusPolling() {
    this.pollInterval = setInterval(async () => {
      if (!this.useBrowserCamera) {
        await this.fetchStatusOnce();
      }
    }, 180);
  }

  async fetchStatusOnce() {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        this.updateUI(data);
      }
    } catch (e) {
      // Ignore polling hiccups
    }
  }

  updateUI(data) {
    if (!data) return;

    // 1. Current Detected Sign & Confidence
    const sign = data.prediction;
    const conf = Math.round(data.confidence || 0);
    const isStable = Boolean(data.is_stable);

    if (sign && conf > 0) {
      const vocab = ISL_REALTIME_VOCAB[sign];
      const enText = vocab ? vocab.en : sign;
      const hiText = vocab ? vocab.hi : sign;

      if (this.heroSignChar) this.heroSignChar.textContent = enText;
      if (this.heroSignHindi) this.heroSignHindi.textContent = hiText;
      if (this.heroSignDesc) this.heroSignDesc.textContent = data.desc || `Gesture detected: ${enText}`;

      if (this.confidenceBar) this.confidenceBar.style.width = `${conf}%`;
      if (this.confidenceVal) this.confidenceVal.textContent = `${conf}%`;

      if (this.stabilityBadge) {
        this.stabilityBadge.textContent = isStable ? 'CONFIRMED' : 'TRACKING';
        this.stabilityBadge.className = isStable
          ? 'px-2 py-0.5 text-xs font-semibold rounded bg-emerald-900/50 text-emerald-400 border border-emerald-600'
          : 'px-2 py-0.5 text-xs font-semibold rounded bg-amber-900/40 text-amber-300 border border-amber-600';
      }

      // Instant Voice Output
      if (this.autoSpeak && isStable && this.speechMode === 'instant') {
        const textToSpeak = (this.selectedVoiceLang === 'hindi') ? hiText : enText;
        const now = Date.now();
        if (textToSpeak !== this.lastSpokenGesture || (now - this.lastSpokenGestureTime > 2200)) {
          this.speakText(textToSpeak, this.selectedVoiceLang);
          this.lastSpokenGesture = textToSpeak;
          this.lastSpokenGestureTime = now;
        }
      }

      // Alternative predictions list
      if (this.topCandidatesList && data.top_k) {
        this.topCandidatesList.innerHTML = data.top_k.map(cand => {
          const cVocab = ISL_REALTIME_VOCAB[cand.label];
          const cLabel = (this.selectedVoiceLang === 'hindi' && cVocab) ? `${cVocab.hi} (${cand.label})` : cand.label;
          return `
            <div class="flex items-center justify-between text-xs py-0.5">
              <span class="text-slate-300 truncate max-w-[200px]">${cLabel}</span>
              <span class="font-mono text-slate-400">${cand.confidence}%</span>
            </div>
          `;
        }).join('');
      }
    } else {
      if (this.heroSignChar) this.heroSignChar.textContent = "—";
      if (this.heroSignHindi) this.heroSignHindi.textContent = "—";
      if (this.heroSignDesc) this.heroSignDesc.textContent = "Perform sign gestures in front of the camera.";
      if (this.confidenceBar) this.confidenceBar.style.width = '0%';
      if (this.confidenceVal) this.confidenceVal.textContent = '0%';
      if (this.stabilityBadge) {
        this.stabilityBadge.textContent = 'STANDBY';
        this.stabilityBadge.className = 'px-2 py-0.5 text-xs font-medium rounded bg-slate-800 text-slate-400 border border-slate-700';
      }
      if (this.topCandidatesList) {
        this.topCandidatesList.innerHTML = '<span class="text-xs text-slate-500">Awaiting hand gestures...</span>';
      }
    }

    // 2. Active Word & Sentence Builder
    if (this.currentWordBadge) {
      this.currentWordBadge.textContent = data.current_word || "—";
    }
    if (this.liveSentenceRaw) {
      this.liveSentenceRaw.textContent = data.live_sentence_raw || "—";
    }

    if (this.liveSentencePolished) {
      const eng = data.live_sentence_english || "";
      this.liveSentencePolished.textContent = eng || (data.live_sentence_raw ? `"${data.live_sentence_raw}"` : "Waiting for signer to begin...");
    }

    if (this.liveSentenceHindi) {
      const hi = data.live_sentence_hindi || "";
      this.liveSentenceHindi.textContent = hi || "सांकेतिक भाषा अनुवाद प्रतीक्षा...";
    }

    // 3. Full Story Translation Box
    const storyEng = data.story_english || "";
    const storyHi = data.story_hindi || "";

    if (this.storyEnglishText) {
      if (storyEng.trim()) {
        this.storyEnglishText.textContent = storyEng;
        this.storyEnglishText.classList.remove('text-slate-500', 'italic');
        this.storyEnglishText.classList.add('text-slate-100');
      } else {
        this.storyEnglishText.textContent = "Your continuous story will weave together here as you sign complete sentences...";
        this.storyEnglishText.classList.add('text-slate-500', 'italic');
        this.storyEnglishText.classList.remove('text-slate-100');
      }
    }

    if (this.storyHindiText) {
      if (storyHi.trim()) {
        this.storyHindiText.textContent = storyHi;
        this.storyHindiText.classList.remove('text-slate-500', 'italic');
        this.storyHindiText.classList.add('text-slate-100');
      } else {
        this.storyHindiText.textContent = "पूरी कहानी का हिंदी अनुवाद यहाँ प्रदर्शित होगा...";
        this.storyHindiText.classList.add('text-slate-500', 'italic');
        this.storyHindiText.classList.remove('text-slate-100');
      }
    }

    // Story Stats
    if (this.storyWordCount) this.storyWordCount.textContent = `${data.word_count || 0} words`;
    if (this.storySentenceCount) this.storySentenceCount.textContent = `${data.sentence_count || 0} sentences`;

    // 4. Sentences Timeline
    if (this.storySentencesTimeline && data.story_sentences) {
      if (data.story_sentences.length === 0) {
        this.storySentencesTimeline.innerHTML = '<span class="text-xs text-slate-500 italic">No completed sentences yet. Pausing for ~2s auto-completes each sentence.</span>';
      } else {
        this.storySentencesTimeline.innerHTML = data.story_sentences.map((item, idx) => `
          <div class="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-start justify-between gap-3">
            <div class="space-y-0.5 flex-1">
              <div class="flex items-center gap-2 text-xs">
                <span class="w-4 h-4 rounded bg-blue-900/60 text-blue-300 font-mono font-bold flex items-center justify-center text-[10px]">
                  ${idx + 1}
                </span>
                <span class="font-mono text-slate-400 text-[11px]">${item.timestamp}</span>
                <span class="text-[10px] uppercase text-slate-500">ISL: ${item.raw}</span>
              </div>
              <p class="text-xs font-medium text-slate-100 pl-6">${item.english}</p>
              <p class="text-xs text-blue-300 pl-6 font-hindi">${item.hindi}</p>
            </div>
            <button class="btn btn-secondary py-1 px-2 text-xs"
              onclick="app.speakText('${(this.selectedVoiceLang === 'hindi' ? item.hindi : item.english).replace(/'/g, "\\'")}', '${this.selectedVoiceLang}')" title="Speak">
              🔊
            </button>
          </div>
        `).join('');
      }
    }

    // 5. Automatic Full-Sentence Speech Trigger
    if (this.autoSpeak && this.speechMode === 'sentence' && data.should_speak && data.speak_text) {
      if (data.speak_text !== this.lastSpokenSentence) {
        this.speakText(data.speak_text, this.selectedVoiceLang);
        this.lastSpokenSentence = data.speak_text;
      }
    }
  }

  // Multi-Language Voice Synthesis Engine (Hindi & English)
  speakText(text, lang = this.selectedVoiceLang) {
    if (!text || !text.trim()) return;

    if (this.speechSynthesis) {
      this.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text.trim());
      utterance.rate = this.speechRate;

      const voices = this.speechSynthesis.getVoices();

      if (lang === 'hindi') {
        utterance.lang = 'hi-IN';
        const hiVoice = voices.find(v =>
          v.lang.toLowerCase().includes('hi') ||
          v.name.toLowerCase().includes('hindi') ||
          v.name.includes('हिन्दी') ||
          v.name.toLowerCase().includes('kalpana') ||
          v.name.toLowerCase().includes('hemant')
        );
        if (hiVoice) utterance.voice = hiVoice;
      } else {
        utterance.lang = 'en-IN';
        const enVoice = voices.find(v =>
          v.lang.toLowerCase().includes('en-in') ||
          v.name.toLowerCase().includes('india') ||
          v.name.toLowerCase().includes('heera') ||
          v.name.toLowerCase().includes('ravi') ||
          v.lang.toLowerCase().startsWith('en')
        );
        if (enVoice) utterance.voice = enVoice;
      }

      utterance.onerror = () => {
        this.speakBackendFallback(text);
      };

      this.speechSynthesis.speak(utterance);
    } else {
      this.speakBackendFallback(text);
    }
  }

  speakBackendFallback(text) {
    fetch('/api/tts/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        rate: Math.round(150 * this.speechRate),
        volume: 1.0
      })
    });
  }

  exportStoryFile() {
    const eng = this.storyEnglishText?.textContent || "";
    const hi = this.storyHindiText?.textContent || "";
    if (!eng.trim() || eng.includes("Your continuous story will weave together here")) {
      this.showToast("No story to export yet.", "info");
      return;
    }

    const content = `======================================================
INDIAN SIGN LANGUAGE (ISL) STORY TRANSLATION
Date: ${new Date().toLocaleString()}
======================================================

ENGLISH NARRATIVE:
${eng}

HINDI TRANSLATION (हिंदी अनुवाद):
${hi}

Generated by Indian Sign Language Translator
`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ISL_Story_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    this.showToast("Story exported as text file!", "success");
  }

  // Browser WebRTC Camera Fallback
  async startBrowserCamera() {
    this.useBrowserCamera = true;
    if (this.videoStreamImg) this.videoStreamImg.classList.add('hidden');
    if (this.browserVideo) this.browserVideo.classList.remove('hidden');

    try {
      this.browserStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' }
      });
      this.browserVideo.srcObject = this.browserStream;
      await this.browserVideo.play();

      const ctx = this.browserCanvas.getContext('2d');
      this.processFrameInterval = setInterval(async () => {
        if (!this.useBrowserCamera) return;
        this.browserCanvas.width = this.browserVideo.videoWidth || 640;
        this.browserCanvas.height = this.browserVideo.videoHeight || 480;
        ctx.drawImage(this.browserVideo, 0, 0);

        const dataUrl = this.browserCanvas.toDataURL('image/jpeg', 0.7);

        try {
          const res = await fetch('/api/process_frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl, mirror: true })
          });
          if (res.ok) {
            const data = await res.json();
            const stab = data.stabilized || {};
            this.updateUI({
              prediction: data.prediction?.prediction,
              confidence: data.prediction?.confidence,
              top_k: data.prediction?.top_k,
              desc: data.prediction?.desc,
              is_stable: stab.is_stable,
              stability_pct: stab.stability_pct,
              current_word: stab.current_word,
              live_sentence_raw: stab.live_sentence_raw,
              live_sentence_english: stab.live_sentence_english,
              live_sentence_hindi: stab.live_sentence_hindi,
              story_english: stab.story_english,
              story_hindi: stab.story_hindi,
              story_sentences: stab.story_sentences,
              sentence_count: stab.sentence_count,
              word_count: stab.word_count,
              should_speak: data.should_speak,
              speak_text: data.speak_text
            });
          }
        } catch (e) {
          // Frame error
        }
      }, 120);

      this.showToast("Browser Camera Active", "success");
    } catch (err) {
      this.showToast(`Camera access denied: ${err.message}`, "danger");
      this.stopBrowserCamera();
    }
  }

  stopBrowserCamera() {
    this.useBrowserCamera = false;
    if (this.processFrameInterval) clearInterval(this.processFrameInterval);
    if (this.browserStream) {
      this.browserStream.getTracks().forEach(t => t.stop());
      this.browserStream = null;
    }
    if (this.browserVideo) this.browserVideo.classList.add('hidden');
    if (this.videoStreamImg) this.videoStreamImg.classList.remove('hidden');
  }

  showToast(message, type = 'success') {
    if (!this.toast || !this.toastMsg) return;
    this.toastMsg.textContent = message;

    if (type === 'danger') {
      this.toast.style.borderColor = 'var(--danger)';
    } else {
      this.toast.style.borderColor = 'var(--primary)';
    }

    this.toast.classList.add('show');
    clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => {
      this.toast.classList.remove('show');
    }, 2800);
  }
}

let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new ISLApp();
});
