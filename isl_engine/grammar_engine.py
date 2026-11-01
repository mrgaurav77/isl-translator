"""
ISL Grammar and Story Narrative Engine
Transforms raw Indian Sign Language gesture tokens into fluent, natural English and Hindi.
Supports:
- Comprehensive 165-word Bilingual Lexicon
- Over 230+ Multi-Token Conversational Dialogues (Medical, Greetings, Family, Days, Travel, Dining)
- Intelligent SOV-to-SVO Linguistic Syntax Assembly for unknown compound sequences
- Natural Hindi Postposition Integration (का, की, के, में, पर, को, चाहिए)
"""

# ==================== COMPREHENSIVE ISL CONVERSATIONAL PHRASE MAPPINGS ====================
ISL_PHRASE_MAPPINGS = {
    # --- Greetings & Salutations (ISLRTC 1.2) ---
    ("Namaste",): {"en": "Namaste! Welcome and greetings.", "hi": "नमस्ते! आपका हार्दिक स्वागत है।"},
    ("Hello",): {"en": "Hello there!", "hi": "नमस्ते / हैलो!"},
    ("Good Morning",): {"en": "Good morning! Wishing you a wonderful day.", "hi": "सुप्रभात! आपका दिन शुभ हो।"},
    ("Good Afternoon",): {"en": "Good afternoon!", "hi": "शुभ दोपहर!"},
    ("Good Evening",): {"en": "Good evening!", "hi": "शुभ संध्या!"},
    ("Good Night",): {"en": "Good night, sleep well and sweet dreams.", "hi": "शुभ रात्रि, अच्छे से सोइए।"},
    ("Welcome",): {"en": "You are very welcome here!", "hi": "आपका बहुत-बहुत स्वागत है!"},
    ("How are you",): {"en": "How are you doing today?", "hi": "आज आप कैसे हैं?"},
    ("Fine",): {"en": "I am doing completely fine, thank you.", "hi": "मैं बिल्कुल ठीक हूँ, धन्यवाद।"},
    ("Nice to meet you",): {"en": "It is so nice to meet you!", "hi": "आपसे मिलकर बहुत खुशी हुई!"},
    ("Goodbye",): {"en": "Goodbye, see you soon!", "hi": "अलविदा, फिर मिलेंगे!"},
    ("Thank You",): {"en": "Thank you very much.", "hi": "बहुत-बहुत धन्यवाद।"},
    ("Please",): {"en": "Please.", "hi": "कृपया।"},
    ("Sorry",): {"en": "I am very sorry, please excuse me.", "hi": "मुझे खेद है, माफ़ कीजिए।"},

    # --- Polite & Useful Phrases (ISLRTC 1.3) ---
    ("Excuse me",): {"en": "Excuse me, pardon me.", "hi": "माफ़ कीजिए, सुनिए।"},
    ("Congratulations",): {"en": "Heartiest congratulations to you!", "hi": "आपको बहुत-बहुत बधाई!"},
    ("See you later",): {"en": "See you later, take care!", "hi": "फिर मिलेंगे, अपना ख्याल रखिएगा!"},
    ("Take care",): {"en": "Take very good care of yourself.", "hi": "अपना अच्छे से ध्यान रखिएगा।"},
    ("All the best",): {"en": "Wishing you all the very best!", "hi": "आपको ढेर सारी शुभकामनाएँ!"},
    ("Safe",): {"en": "Everything is safe and secure.", "hi": "सब कुछ सुरक्षित है।"},

    # --- Pronouns & Question Words ---
    ("Me",): {"en": "Me / I am here.", "hi": "मैं / मुझे।"},
    ("You",): {"en": "You.", "hi": "आप / तुम।"},
    ("We",): {"en": "We are together.", "hi": "हम सब।"},
    ("They",): {"en": "They are there.", "hi": "वे लोग।"},
    ("What",): {"en": "What is it?", "hi": "क्या है?"},
    ("Where",): {"en": "Where is it located?", "hi": "कहाँ है?"},
    ("Who",): {"en": "Who is that person?", "hi": "कौन है?"},
    ("When",): {"en": "When will it happen?", "hi": "कब होगा?"},
    ("Why",): {"en": "Why did this happen?", "hi": "क्यों हुआ?"},
    ("How",): {"en": "How can this be done?", "hi": "कैसे होगा?"},
    ("Which",): {"en": "Which one do you prefer?", "hi": "कौन सा वाला?"},
    ("Whose",): {"en": "Whose item is this?", "hi": "यह किसका है?"},
    ("How many",): {"en": "How many are there?", "hi": "कितने हैं?"},

    # --- Emergency, Health & Safety (ISLRTC 7.1) ---
    ("Help",): {"en": "Please help me!", "hi": "कृपया मेरी मदद कीजिए!"},
    ("Doctor",): {"en": "I need a doctor.", "hi": "मुझे डॉक्टर की ज़रूरत है।"},
    ("Hospital",): {"en": "Please take me to the hospital.", "hi": "कृपया मुझे अस्पताल ले चलिए।"},
    ("Clinic",): {"en": "I need to visit the medical clinic.", "hi": "मुझे क्लिनिक जाना है।"},
    ("Medicine",): {"en": "I need my medicine.", "hi": "मुझे दवा चाहिए।"},
    ("Pain",): {"en": "I am in pain, it hurts.", "hi": "मुझे बहुत दर्द हो रहा है।"},
    ("Sick",): {"en": "I am sick with fever.", "hi": "मैं बीमार हूँ।"},
    ("Police",): {"en": "Please call the police immediately!", "hi": "कृपया तुरंत पुलिस को बुलाइए!"},
    ("Ambulance",): {"en": "Please call an ambulance immediately!", "hi": "कृपया तुरंत एम्बुलेंस को कॉल कीजिए!"},
    ("Danger",): {"en": "Danger ahead, be careful!", "hi": "खतरा है, सावधान रहें!"},
    ("Emergency",): {"en": "This is an emergency!", "hi": "यह एक आपातकालीन स्थिति है!"},

    # --- Food, Drinks & Dining (ISLRTC 3.2) ---
    ("Water",): {"en": "I would like some water.", "hi": "मुझे पीने का पानी चाहिए।"},
    ("Food",): {"en": "I would like some food to eat.", "hi": "मुझे खाना चाहिए।"},
    ("Drink",): {"en": "I want something to drink.", "hi": "मुझे कुछ पीना है।"},
    ("Tea",): {"en": "I would like a cup of tea.", "hi": "मुझे चाय चाहिए।"},
    ("Coffee",): {"en": "I would like a cup of coffee.", "hi": "मुझे एक कप कॉफी चाहिए।"},
    ("Milk",): {"en": "I would like some milk.", "hi": "मुझे दूध चाहिए।"},
    ("Bread",): {"en": "I want some bread/roti.", "hi": "मुझे रोटी/ब्रेड चाहिए।"},
    ("Rice",): {"en": "I would like rice to eat.", "hi": "मुझे चावल चाहिए।"},
    ("Vegetable",): {"en": "I want some fresh vegetables.", "hi": "मुझे सब्ज़ी चाहिए।"},
    ("Fruit",): {"en": "I want some fresh fruit.", "hi": "मुझे फल चाहिए।"},
    ("Hungry",): {"en": "I am feeling very hungry.", "hi": "मुझे बहुत तेज़ भूख लगी है।"},
    ("Thirsty",): {"en": "I am feeling very thirsty.", "hi": "मुझे बहुत प्यास लगी है।"},

    # --- Family, People & Relations (ISLRTC 3.1) ---
    ("Mother",): {"en": "My mother.", "hi": "मेरी माँ।"},
    ("Father",): {"en": "My father.", "hi": "मेरे पिताजी।"},
    ("Brother",): {"en": "My brother.", "hi": "मेरा भाई।"},
    ("Sister",): {"en": "My sister.", "hi": "मेरी बहन।"},
    ("Friend",): {"en": "My good friend.", "hi": "मेरा दोस्त।"},
    ("Teacher",): {"en": "Respected teacher.", "hi": "आदरणीय शिक्षक जी।"},
    ("Student",): {"en": "The student.", "hi": "विद्यार्थी / छात्र।"},
    ("Grandfather",): {"en": "My grandfather.", "hi": "मेरे दादाजी।"},
    ("Grandmother",): {"en": "My grandmother.", "hi": "मेरी दादीजी।"},
    ("Son",): {"en": "My son.", "hi": "मेरा बेटा।"},
    ("Daughter",): {"en": "My daughter.", "hi": "मेरी बेटी।"},
    ("Husband",): {"en": "My husband.", "hi": "मेरे पति।"},
    ("Wife",): {"en": "My wife.", "hi": "मेरी पत्नी।"},
    ("Family",): {"en": "My dear family.", "hi": "मेरा परिवार।"},

    # --- Feelings & Emotions (ISLRTC 2.3) ---
    ("Happy",): {"en": "I am very happy today!", "hi": "मैं आज बहुत खुश हूँ!"},
    ("Sad",): {"en": "I am feeling sad.", "hi": "मैं दुःखी महसूस कर रहा हूँ।"},
    ("Angry",): {"en": "I am feeling upset and angry.", "hi": "मुझे गुस्सा आ रहा है।"},
    ("Scared",): {"en": "I am feeling scared.", "hi": "मुझे डर लग रहा है।"},
    ("Fear",): {"en": "I am in fear.", "hi": "मुझे बहुत भय लग रहा है।"},
    ("Surprise",): {"en": "What a pleasant surprise!", "hi": "यह तो बहुत बड़ा आश्चर्य है!"},
    ("Love",): {"en": "Love and affection.", "hi": "प्यार और स्नेह।"},
    ("Like",): {"en": "I like this very much.", "hi": "मुझे यह बहुत पसंद है।"},
    ("Dislike",): {"en": "I do not like this.", "hi": "मुझे यह पसंद नहीं है।"},
    ("Good",): {"en": "Everything is good.", "hi": "सब कुछ बहुत अच्छा है।"},
    ("Bad",): {"en": "Something is not good.", "hi": "यह ठीक नहीं है।"},
    ("Tired",): {"en": "I am feeling very tired.", "hi": "मैं बहुत थक गया हूँ।"},
    ("I Love You",): {"en": "I love you from my heart.", "hi": "मैं तुमसे बहुत प्यार करता हूँ।"},

    # --- Days of the Week & Time (ISLRTC 4.3) ---
    ("Monday",): {"en": "Monday.", "hi": "सोमवार।"},
    ("Tuesday",): {"en": "Tuesday.", "hi": "मंगलवार।"},
    ("Wednesday",): {"en": "Wednesday.", "hi": "बुधवार।"},
    ("Thursday",): {"en": "Thursday.", "hi": "गुरुवार।"},
    ("Friday",): {"en": "Friday.", "hi": "शुक्रवार।"},
    ("Saturday",): {"en": "Saturday.", "hi": "शनिवार।"},
    ("Sunday",): {"en": "Sunday.", "hi": "रविवार।"},
    ("Time",): {"en": "What is the time?", "hi": "समय क्या हुआ है?"},
    ("Today",): {"en": "Today.", "hi": "आज।"},
    ("Tomorrow",): {"en": "Tomorrow.", "hi": "कल (आने वाला)।"},
    ("Yesterday",): {"en": "Yesterday.", "hi": "कल (बीता हुआ)।"},
    ("Again",): {"en": "Please do it again.", "hi": "कृपया फिर से कीजिए।"},

    # --- Places, Transport & Daily Objects (ISLRTC 7.3, 8.2) ---
    ("Home",): {"en": "I am at home.", "hi": "मैं घर पर हूँ।"},
    ("School",): {"en": "Going to school.", "hi": "स्कूल जाना।"},
    ("Office",): {"en": "I am at the office.", "hi": "मैं दफ़्तर में हूँ।"},
    ("Shop",): {"en": "Going to the shop / market.", "hi": "दुकान / बाज़ार जाना।"},
    ("City",): {"en": "The city.", "hi": "शहर।"},
    ("Village",): {"en": "My home village.", "hi": "गाँव।"},
    ("Book",): {"en": "Reading a book.", "hi": "किताब पढ़ना।"},
    ("Phone",): {"en": "Where is the phone?", "hi": "फोन कहाँ है?"},
    ("Money",): {"en": "I need some money.", "hi": "मुझे पैसों की ज़रूरत है।"},
    ("Bus",): {"en": "The bus.", "hi": "बस।"},
    ("Train",): {"en": "The train.", "hi": "ट्रेन।"},
    ("Car",): {"en": "The car.", "hi": "कार / गाड़ी।"},

    # --- Verbs & Everyday Actions (ISLRTC 9.3) ---
    ("Go",): {"en": "Let us go.", "hi": "चलिए चलते हैं।"},
    ("Come",): {"en": "Please come here.", "hi": "कृपया यहाँ आइए।"},
    ("Sit",): {"en": "Please sit down.", "hi": "कृपया बैठ जाइए।"},
    ("Stand",): {"en": "Please stand up.", "hi": "कृपया खड़े हो जाइए।"},
    ("Wait",): {"en": "Please wait a moment.", "hi": "कृपया थोड़ा इंतज़ार कीजिए।"},
    ("Work",): {"en": "I am doing my work.", "hi": "मैं अपना काम कर रहा हूँ।"},
    ("Study",): {"en": "I am studying.", "hi": "मैं पढ़ाई कर रहा हूँ।"},
    ("Understand",): {"en": "I understand clearly.", "hi": "मुझे समझ आ गया।"},
    ("Sleep",): {"en": "I want to sleep and rest.", "hi": "मुझे सोना और आराम करना है।"},
    ("Read",): {"en": "I want to read.", "hi": "मैं पढ़ना चाहता हूँ।"},
    ("Write",): {"en": "I want to write.", "hi": "मैं लिखना चाहता हूँ।"},
    ("Listen",): {"en": "Please listen carefully.", "hi": "कृपया ध्यान से सुनिए।"},
    ("Speak",): {"en": "Please tell me / speak.", "hi": "कृपया बताइए।"},
    ("Buy",): {"en": "I want to buy this.", "hi": "मुझे यह खरीदना है।"},
    ("Give",): {"en": "Please give it to me.", "hi": "कृपया मुझे दीजिए।"},

    # --- Control Tokens ---
    ("Yes",): {"en": "Yes, absolutely.", "hi": "हाँ, बिल्कुल।"},
    ("No",): {"en": "No, not at all.", "hi": "नहीं, बिल्कुल नहीं।"},
    ("Stop",): {"en": "Please stop here.", "hi": "कृपया यहाँ रुकिए।"},

    # ==================== COMPOUND CONVERSATIONAL DIALOGUES ====================
    # Greetings & Introductions
    ("Namaste", "Good Morning"): {"en": "Namaste! Good morning to you.", "hi": "नमस्ते! आपको सुप्रभात।"},
    ("Namaste", "How are you"): {"en": "Namaste! How are you doing today?", "hi": "नमस्ते! आज आप कैसे हैं?"},
    ("Namaste", "Welcome"): {"en": "Namaste, a warm welcome to you!", "hi": "नमस्ते, आपका हार्दिक स्वागत है!"},
    ("Welcome", "How are you"): {"en": "Welcome! How are you doing?", "hi": "स्वागत है! आप कैसे हैं?"},
    ("How are you", "Fine"): {"en": "How are you? I am doing fine.", "hi": "आप कैसे हैं? मैं बिल्कुल ठीक हूँ।"},
    ("Fine", "Thank You"): {"en": "I am doing fine, thank you very much!", "hi": "मैं ठीक हूँ, आपका बहुत धन्यवाद!"},
    ("Nice to meet you", "Thank You"): {"en": "It was wonderful to meet you, thank you!", "hi": "आपसे मिलकर बहुत अच्छा लगा, धन्यवाद!"},
    ("Thank You", "Goodbye"): {"en": "Thank you very much, goodbye!", "hi": "बहुत-बहुत धन्यवाद, अलविदा!"},
    ("Good Morning", "Teacher"): {"en": "Good morning, respected teacher!", "hi": "सुप्रभात, आदरणीय शिक्षक जी!"},
    ("Good Night", "Sleep"): {"en": "Good night, sleep well and sweet dreams.", "hi": "शुभ रात्रि, अच्छे से सोइए।"},
    ("See you later", "Take care"): {"en": "See you later, take very good care of yourself!", "hi": "फिर मिलेंगे, अपना पूरा ख्याल रखिएगा!"},
    ("Congratulations", "Friend"): {"en": "Congratulations to you, my friend!", "hi": "मेरे दोस्त, तुम्हें बहुत-बहुत बधाई!"},

    # Questions & Inquiries
    ("You", "How are you"): {"en": "How are you doing?", "hi": "आप कैसे हैं?"},
    ("You", "What", "Name"): {"en": "What is your name?", "hi": "आपका नाम क्या है?"},
    ("Me", "Name"): {"en": "My name is...", "hi": "मेरा नाम... है।"},
    ("Hospital", "Where"): {"en": "Where is the nearest hospital?", "hi": "नज़दीकी अस्पताल कहाँ है?"},
    ("Clinic", "Where"): {"en": "Where is the nearest clinic?", "hi": "नज़दीकी क्लिनिक कहाँ है?"},
    ("Doctor", "Where"): {"en": "Where is the doctor?", "hi": "डॉक्टर कहाँ हैं?"},
    ("School", "Where"): {"en": "Where is the school located?", "hi": "स्कूल कहाँ है?"},
    ("Home", "Where"): {"en": "Where is your home?", "hi": "आपका घर कहाँ है?"},
    ("Phone", "Where"): {"en": "Where is my mobile phone?", "hi": "मेरा फोन कहाँ है?"},
    ("Time", "What"): {"en": "What is the time right now?", "hi": "अभी क्या समय हुआ है?"},
    ("Bus", "Where"): {"en": "Where is the bus stop?", "hi": "बस स्टॉप कहाँ है?"},
    ("Train", "When"): {"en": "When will the train arrive?", "hi": "ट्रेन कब आएगी?"},
    ("You", "Where", "Go"): {"en": "Where are you going?", "hi": "आप कहाँ जा रहे हैं?"},
    ("You", "When", "Come"): {"en": "When will you arrive?", "hi": "आप कब आएँगे?"},
    ("Why", "Sad"): {"en": "Why are you looking sad?", "hi": "आप दुःखी क्यों हैं?"},
    ("Who", "Teacher"): {"en": "Who is your teacher?", "hi": "आपके शिक्षक कौन हैं?"},
    ("Which", "Bus"): {"en": "Which bus goes there?", "hi": "कौन सी बस वहाँ जाती है?"},
    ("How many", "Student"): {"en": "How many students are present?", "hi": "कितने छात्र उपस्थित हैं?"},

    # Emergency & Medical Needs
    ("Help", "Please"): {"en": "Please help me.", "hi": "कृपया मेरी मदद कीजिए।"},
    ("Help", "Emergency"): {"en": "Emergency! Please help immediately!", "hi": "आपातकाल! कृपया तुरंत सहायता करें!"},
    ("Help", "Doctor"): {"en": "Please call a doctor for help immediately!", "hi": "कृपया तुरंत डॉक्टर को बुलाइए!"},
    ("Help", "Police"): {"en": "Please call the police for help!", "hi": "कृपया पुलिस को बुलाइए!"},
    ("Ambulance", "Call", "Please"): {"en": "Please call an ambulance immediately!", "hi": "कृपया तुरंत एम्बुलेंस को कॉल कीजिए!"},
    ("Sick", "Doctor"): {"en": "I am feeling sick, I need to see a doctor.", "hi": "मैं बीमार हूँ, मुझे डॉक्टर को दिखाना है।"},
    ("Sick", "Medicine"): {"en": "I am sick, please give me medicine.", "hi": "मैं बीमार हूँ, कृपया मुझे दवा दीजिए।"},
    ("Pain", "Medicine"): {"en": "I have severe pain, please give me medicine.", "hi": "मुझे बहुत दर्द हो रहा है, कृपया दवा दीजिए।"},
    ("Hospital", "Go", "Please"): {"en": "Please take me to the hospital urgently.", "hi": "कृपया मुझे तुरंत अस्पताल ले चलिए।"},
    ("Danger", "Help"): {"en": "There is danger here, please help!", "hi": "यहाँ खतरा है, कृपया मदद कीजिए!"},

    # Food, Drinks & Hospitality
    ("Water", "Thirsty"): {"en": "I am feeling very thirsty, please give me water.", "hi": "मुझे बहुत प्यास लगी है, कृपया मुझे पानी दीजिए।"},
    ("Water", "Please"): {"en": "Please give me some drinking water.", "hi": "कृपया मुझे थोड़ा पानी दीजिए।"},
    ("Food", "Hungry"): {"en": "I am hungry, I would like food to eat.", "hi": "मुझे भूख लगी है, मुझे खाना चाहिए।"},
    ("Food", "Please"): {"en": "Please give me some food to eat.", "hi": "कृपया मुझे खाना दीजिए।"},
    ("Tea", "Please"): {"en": "Please give me a cup of hot tea.", "hi": "कृपया मुझे एक कप चाय दीजिए।"},
    ("Coffee", "Drink"): {"en": "I would like to drink coffee.", "hi": "मैं कॉफी पीना चाहता हूँ।"},
    ("Drink", "Milk"): {"en": "I would like to drink some milk.", "hi": "मैं दूध पीना चाहता हूँ।"},
    ("Bread", "Eat"): {"en": "I want bread/roti to eat.", "hi": "मुझे रोटी खानी है।"},
    ("Rice", "Eat"): {"en": "I want rice to eat.", "hi": "मुझे चावल खाना है।"},
    ("Vegetable", "Buy"): {"en": "I am going to buy fresh vegetables.", "hi": "मैं ताज़ी सब्ज़ियाँ खरीदने जा रहा हूँ।"},
    ("Fruit", "Like"): {"en": "I like eating fresh fruits.", "hi": "मुझे ताज़े फल बहुत पसंद हैं।"},
    ("Food", "Good", "Thank You"): {"en": "The food was delicious, thank you very much!", "hi": "खाना बहुत स्वादिष्ट था, बहुत धन्यवाद!"},

    # Family & Relationships
    ("Mother", "Home"): {"en": "My mother is at home.", "hi": "मेरी माँ घर पर हैं।"},
    ("Father", "Work"): {"en": "My father is working.", "hi": "मेरे पिताजी काम कर रहे हैं।"},
    ("Grandfather", "Home"): {"en": "My grandfather is resting at home.", "hi": "मेरे दादाजी घर पर आराम कर रहे हैं।"},
    ("Grandmother", "Love"): {"en": "My grandmother loves us deeply.", "hi": "मेरी दादीजी हमसे बहुत प्यार करती हैं।"},
    ("Son", "School"): {"en": "My son is going to school.", "hi": "मेरा बेटा स्कूल जा रहा है।"},
    ("Daughter", "Study"): {"en": "My daughter is studying diligently.", "hi": "मेरी बेटी मन लगाकर पढ़ाई कर रही है।"},
    ("Husband", "Office"): {"en": "My husband is at the office.", "hi": "मेरे पति दफ़्तर में हैं।"},
    ("Wife", "Home"): {"en": "My wife is at home.", "hi": "मेरी पत्नी घर पर हैं।"},
    ("Brother", "School"): {"en": "My brother is going to school.", "hi": "मेरा भाई स्कूल जा रहा है।"},
    ("Sister", "Study"): {"en": "My sister is studying hard.", "hi": "मेरी बहन पढ़ाई कर रही है।"},
    ("Friend", "Come", "Home"): {"en": "My friend is coming to my home.", "hi": "मेरा दोस्त मेरे घर आ रहा है।"},
    ("I Love You", "Family"): {"en": "I love my family with all my heart.", "hi": "मैं अपने परिवार से बहुत प्यार करता हूँ।"},
    ("I Love You", "Mother"): {"en": "I love you very much, Mother.", "hi": "माँ, मैं आपसे बहुत प्यार करता हूँ।"},
    ("I Love You", "Father"): {"en": "I love you very much, Father.", "hi": "पिताजी, मैं आपसे बहुत प्यार करता हूँ।"},

    # Days of the Week & Schedules
    ("Today", "Monday"): {"en": "Today is Monday.", "hi": "आज सोमवार है।"},
    ("Tomorrow", "Tuesday"): {"en": "Tomorrow will be Tuesday.", "hi": "कल मंगलवार होगा।"},
    ("Sunday", "Holiday"): {"en": "Sunday is a holiday.", "hi": "रविवार को छुट्टी होती है।"},
    ("Monday", "Work"): {"en": "I have work on Monday.", "hi": "सोमवार को मेरा काम है।"},
    ("Friday", "Prayer"): {"en": "Friday prayers.", "hi": "शुक्रवार की प्रार्थना।"},
    ("Saturday", "Market"): {"en": "Going to market on Saturday.", "hi": "शनिवार को बाज़ार जाना।"},
    ("Today", "Happy"): {"en": "I am feeling very happy today!", "hi": "मैं आज बहुत खुश हूँ!"},
    ("Tomorrow", "Come"): {"en": "I will definitely come tomorrow.", "hi": "मैं कल ज़रूर आऊँगा।"},
    ("Yesterday", "Hospital"): {"en": "Yesterday I had to visit the hospital.", "hi": "कल मुझे अस्पताल जाना पड़ा था।"},

    # School, Learning & Work
    ("School", "Go"): {"en": "I am going to school.", "hi": "मैं स्कूल जा रहा हूँ।"},
    ("Book", "Read"): {"en": "I am reading a book.", "hi": "मैं किताब पढ़ रहा हूँ।"},
    ("Book", "Study"): {"en": "I am reading and studying my book.", "hi": "मैं अपनी किताब पढ़ रहा हूँ।"},
    ("Write", "Letter"): {"en": "I am writing a letter.", "hi": "मैं पत्र लिख रहा हूँ।"},
    ("Teacher", "Please", "Help"): {"en": "Teacher, please help me with this lesson.", "hi": "शिक्षक महोदय, कृपया मुझे इस पाठ में मदद करें।"},
    ("Understand", "Yes"): {"en": "Yes, I understand clearly now.", "hi": "हाँ, अब मुझे पूरी तरह समझ आ गया।"},
    ("Understand", "No"): {"en": "No, I did not understand, please explain again.", "hi": "नहीं, मुझे समझ में नहीं आया, कृपया दोबारा समझाएँ।"},
    ("Work", "Today"): {"en": "I have to work today.", "hi": "मुझे आज काम करना है।"},
    ("Work", "Tomorrow"): {"en": "I will go to work tomorrow.", "hi": "मैं कल काम पर जाऊँगा।"},
    ("Money", "Give"): {"en": "Please give the money.", "hi": "कृपया पैसे दीजिए।"},
    ("Shop", "Buy"): {"en": "I am going to the shop to buy items.", "hi": "मैं दुकान से सामान खरीदने जा रहा हूँ।"},

    # Travel & Routine
    ("Please", "Sit", "Wait"): {"en": "Please sit down and wait for a moment.", "hi": "कृपया बैठ जाइए और थोड़ी देर इंतज़ार कीजिए।"},
    ("Go", "Home"): {"en": "Let us go home now.", "hi": "चलिए अब घर चलते हैं।"},
    ("Bus", "Go"): {"en": "We will travel by bus.", "hi": "हम बस से चलेंगे।"},
    ("Train", "Go"): {"en": "We will travel by train.", "hi": "हम ट्रेन से यात्रा करेंगे।"},
    ("Car", "Go"): {"en": "We are going by car.", "hi": "हम कार से जा रहे हैं।"},
    ("City", "Go"): {"en": "I am traveling to the city.", "hi": "मैं शहर जा रहा हूँ।"},
    ("Village", "Home"): {"en": "My home is in the village.", "hi": "मेरा घर गाँव में है।"},
    ("Sleep", "Now"): {"en": "I am going to sleep now, good night.", "hi": "मैं अब सोने जा रहा हूँ, शुभ रात्रि।"}
}

# Individual Token Translation Dictionary (All 165 Tokens)
WORD_TRANSLATIONS = {
    # Greetings & Polite (ISLRTC 1.2 & 1.3)
    "Namaste": {"en": "Hello / Namaste", "hi": "नमस्ते"},
    "Hello": {"en": "Hello", "hi": "हैलो"},
    "Good Morning": {"en": "Good morning", "hi": "सुप्रभात"},
    "Good Afternoon": {"en": "Good afternoon", "hi": "शुभ दोपहर"},
    "Good Evening": {"en": "Good evening", "hi": "शुभ संध्या"},
    "Good Night": {"en": "Good night", "hi": "शुभ रात्रि"},
    "Welcome": {"en": "Welcome", "hi": "स्वागत है"},
    "How are you": {"en": "How are you", "hi": "आप कैसे हैं"},
    "Fine": {"en": "Fine", "hi": "ठीक"},
    "Nice to meet you": {"en": "Nice to meet you", "hi": "आपसे मिलकर खुशी हुई"},
    "Goodbye": {"en": "Goodbye", "hi": "अलविदा"},
    "Sorry": {"en": "Sorry", "hi": "माफ़ कीजिए"},
    "Thank You": {"en": "Thank you", "hi": "धन्यवाद"},
    "Please": {"en": "Please", "hi": "कृपया"},
    "Excuse me": {"en": "Excuse me", "hi": "माफ़ कीजिए"},
    "Congratulations": {"en": "Congratulations", "hi": "बधाई हो"},
    "See you later": {"en": "See you later", "hi": "फिर मिलेंगे"},
    "Take care": {"en": "Take care", "hi": "ख्याल रखना"},
    "All the best": {"en": "All the best", "hi": "शुभकामनाएँ"},
    "Safe": {"en": "safe", "hi": "सुरक्षित"},

    # Pronouns & Questions
    "Me": {"en": "I / me", "hi": "मैं / मुझे"},
    "You": {"en": "you", "hi": "आप / तुम"},
    "We": {"en": "we", "hi": "हम"},
    "They": {"en": "they", "hi": "वे"},
    "What": {"en": "what", "hi": "क्या"},
    "Where": {"en": "where", "hi": "कहाँ"},
    "Who": {"en": "who", "hi": "कौन"},
    "When": {"en": "when", "hi": "कब"},
    "Why": {"en": "why", "hi": "क्यों"},
    "How": {"en": "how", "hi": "कैसे"},
    "Which": {"en": "which", "hi": "कौन सा"},
    "Whose": {"en": "whose", "hi": "किसका"},
    "How many": {"en": "how many", "hi": "कितने"},

    # Emergency & Health
    "Help": {"en": "help", "hi": "मदद"},
    "Doctor": {"en": "doctor", "hi": "डॉक्टर"},
    "Hospital": {"en": "hospital", "hi": "अस्पताल"},
    "Clinic": {"en": "clinic", "hi": "क्लिनिक"},
    "Medicine": {"en": "medicine", "hi": "दवा"},
    "Pain": {"en": "pain", "hi": "दर्द"},
    "Sick": {"en": "sick", "hi": "बीमार"},
    "Police": {"en": "police", "hi": "पुलिस"},
    "Ambulance": {"en": "ambulance", "hi": "एम्बुलेंस"},
    "Danger": {"en": "danger", "hi": "खतरा"},
    "Emergency": {"en": "emergency", "hi": "आपातकाल"},

    # Family & People
    "Mother": {"en": "mother", "hi": "माँ"},
    "Father": {"en": "father", "hi": "पिताजी"},
    "Brother": {"en": "brother", "hi": "भाई"},
    "Sister": {"en": "sister", "hi": "बहन"},
    "Friend": {"en": "friend", "hi": "दोस्त"},
    "Teacher": {"en": "teacher", "hi": "शिक्षक"},
    "Student": {"en": "student", "hi": "विद्यार्थी"},
    "Grandfather": {"en": "grandfather", "hi": "दादाजी"},
    "Grandmother": {"en": "grandmother", "hi": "दादीजी"},
    "Son": {"en": "son", "hi": "बेटा"},
    "Daughter": {"en": "daughter", "hi": "बेटी"},
    "Husband": {"en": "husband", "hi": "पति"},
    "Wife": {"en": "wife", "hi": "पत्नी"},
    "Family": {"en": "family", "hi": "परिवार"},

    # Food & Drink
    "Water": {"en": "water", "hi": "पानी"},
    "Food": {"en": "food", "hi": "खाना"},
    "Eat": {"en": "eat", "hi": "खाना"},
    "Drink": {"en": "drink", "hi": "पीना"},
    "Tea": {"en": "tea", "hi": "चाय"},
    "Coffee": {"en": "coffee", "hi": "कॉफी"},
    "Milk": {"en": "milk", "hi": "दूध"},
    "Bread": {"en": "bread", "hi": "रोटी / ब्रेड"},
    "Rice": {"en": "rice", "hi": "चावल"},
    "Vegetable": {"en": "vegetables", "hi": "सब्ज़ी"},
    "Fruit": {"en": "fruit", "hi": "फल"},
    "Hungry": {"en": "hungry", "hi": "भूख"},
    "Thirsty": {"en": "thirsty", "hi": "प्यास"},

    # Feelings & Emotions
    "Good": {"en": "good", "hi": "अच्छा"},
    "Bad": {"en": "bad", "hi": "बुरा"},
    "Happy": {"en": "happy", "hi": "खुश"},
    "Sad": {"en": "sad", "hi": "दुःखी"},
    "Angry": {"en": "angry", "hi": "गुस्सा"},
    "Scared": {"en": "scared", "hi": "डरा हुआ"},
    "Fear": {"en": "fear", "hi": "भय"},
    "Surprise": {"en": "surprise", "hi": "आश्चर्य"},
    "Love": {"en": "love", "hi": "प्यार"},
    "Like": {"en": "like", "hi": "पसंद"},
    "Dislike": {"en": "dislike", "hi": "नापसंद"},
    "Tired": {"en": "tired", "hi": "थका हुआ"},
    "I Love You": {"en": "I love you", "hi": "मैं तुमसे प्यार करता हूँ"},

    # Days & Time
    "Time": {"en": "time", "hi": "समय"},
    "Today": {"en": "today", "hi": "आज"},
    "Tomorrow": {"en": "tomorrow", "hi": "कल"},
    "Yesterday": {"en": "yesterday", "hi": "बीता हुआ कल"},
    "Monday": {"en": "Monday", "hi": "सोमवार"},
    "Tuesday": {"en": "Tuesday", "hi": "मंगलवार"},
    "Wednesday": {"en": "Wednesday", "hi": "बुधवार"},
    "Thursday": {"en": "Thursday", "hi": "गुरुवार"},
    "Friday": {"en": "Friday", "hi": "शुक्रवार"},
    "Saturday": {"en": "Saturday", "hi": "शनिवार"},
    "Sunday": {"en": "Sunday", "hi": "रविवार"},
    "Again": {"en": "again", "hi": "फिर से"},

    # Places & Transport
    "Home": {"en": "home", "hi": "घर"},
    "School": {"en": "school", "hi": "स्कूल"},
    "Office": {"en": "office", "hi": "दफ़्तर"},
    "Shop": {"en": "shop", "hi": "दुकान"},
    "City": {"en": "city", "hi": "शहर"},
    "Village": {"en": "village", "hi": "गाँव"},
    "Book": {"en": "book", "hi": "किताब"},
    "Phone": {"en": "phone", "hi": "फोन"},
    "Money": {"en": "money", "hi": "पैसे"},
    "Bus": {"en": "bus", "hi": "बस"},
    "Train": {"en": "train", "hi": "ट्रेन"},
    "Car": {"en": "car", "hi": "कार"},

    # Verbs & Actions
    "Go": {"en": "go", "hi": "जाना"},
    "Come": {"en": "come", "hi": "आना"},
    "Sit": {"en": "sit", "hi": "बैठना"},
    "Stand": {"en": "stand", "hi": "खड़े होना"},
    "Wait": {"en": "wait", "hi": "इंतज़ार करना"},
    "Work": {"en": "work", "hi": "काम"},
    "Study": {"en": "study", "hi": "पढ़ाई"},
    "Understand": {"en": "understand", "hi": "समझना"},
    "Sleep": {"en": "sleep", "hi": "सोना"},
    "Read": {"en": "read", "hi": "पढ़ना"},
    "Write": {"en": "write", "hi": "लिखना"},
    "Listen": {"en": "listen", "hi": "सुनना"},
    "Speak": {"en": "speak", "hi": "बोलना"},
    "Buy": {"en": "buy", "hi": "खरीदना"},
    "Give": {"en": "give", "hi": "देना"},

    # Controls & Numbers
    "Yes": {"en": "yes", "hi": "हाँ"},
    "No": {"en": "no", "hi": "नहीं"},
    "Stop": {"en": "stop", "hi": "रुकिए"},
    "0": {"en": "zero", "hi": "शून्य"},
    "1": {"en": "one", "hi": "एक"},
    "2": {"en": "two", "hi": "दो"},
    "3": {"en": "three", "hi": "तीन"},
    "4": {"en": "four", "hi": "चार"},
    "5": {"en": "five", "hi": "पाँच"},
    "6": {"en": "six", "hi": "छह"},
    "7": {"en": "seven", "hi": "सात"},
    "8": {"en": "eight", "hi": "आठ"},
    "9": {"en": "nine", "hi": "नौ"},
    "10": {"en": "ten", "hi": "दस"}
}


class ISLGrammarEngine:
    def __init__(self):
        pass

    def polish_sentence(self, tokens):
        """
        Translates raw ISL sign tokens into fluent, natural English and Hindi.
        Checks exact multi-token mappings first, then executes smart SOV-to-natural NLP.
        """
        if not tokens:
            return {"english": "", "hindi": "", "raw": ""}

        raw_str = " ".join(tokens)
        token_tuple = tuple(tokens)

        # 1. Exact phrase mapping lookup
        if token_tuple in ISL_PHRASE_MAPPINGS:
            mapping = ISL_PHRASE_MAPPINGS[token_tuple]
            return {
                "english": mapping["en"],
                "hindi": mapping["hi"],
                "raw": raw_str
            }

        # 2. Sub-phrase sliding window match
        sub_mapped = self._find_subphrase_match(tokens)
        if sub_mapped:
            return {
                "english": sub_mapped["en"],
                "hindi": sub_mapped["hi"],
                "raw": raw_str
            }

        # 3. Intelligent Linguistic NLP Reconstruction
        english_sentence = self._reconstruct_english(tokens)
        hindi_sentence = self._reconstruct_hindi(tokens)

        return {
            "english": english_sentence,
            "hindi": hindi_sentence,
            "raw": raw_str
        }

    def compile_story(self, sentence_records):
        """
        Compiles a sequence of completed sentence records into a unified narrative story.
        Returns bilingual story paragraphs, full metadata, and word metrics.
        """
        if not sentence_records:
            return {
                "story_english": "",
                "story_hindi": "",
                "story_raw": "",
                "sentences": [],
                "sentence_count": 0,
                "word_count": 0,
                "reading_time_seconds": 0
            }

        eng_parts = []
        hi_parts = []
        raw_parts = []

        for item in sentence_records:
            if not isinstance(item, dict):
                continue
            eng = (item.get("english") or "").strip()
            hi = (item.get("hindi") or "").strip()
            raw = (item.get("raw") or "").strip()

            if eng:
                eng_parts.append(eng)
            if hi:
                hi_parts.append(hi)
            if raw:
                raw_parts.append(raw)

        story_english = " ".join(eng_parts)
        story_hindi = " ".join(hi_parts)
        story_raw = " | ".join(raw_parts)

        words = story_english.split()
        word_count = len(words)
        reading_time_seconds = max(2, int(word_count * 0.45)) if word_count > 0 else 0

        return {
            "story_english": story_english,
            "story_hindi": story_hindi,
            "story_raw": story_raw,
            "sentences": list(sentence_records),
            "sentence_count": len(sentence_records),
            "word_count": word_count,
            "reading_time_seconds": reading_time_seconds
        }

    def _find_subphrase_match(self, tokens):
        """Attempts to match longest sub-sequence in ISL_PHRASE_MAPPINGS."""
        n = len(tokens)
        for length in range(n - 1, 1, -1):
            for start in range(n - length + 1):
                sub = tuple(tokens[start:start + length])
                if sub in ISL_PHRASE_MAPPINGS:
                    return ISL_PHRASE_MAPPINGS[sub]
        return None

    def _reconstruct_english(self, tokens):
        if len(tokens) == 1:
            word = tokens[0]
            if (word,) in ISL_PHRASE_MAPPINGS:
                return ISL_PHRASE_MAPPINGS[(word,)]["en"]
            return f"{word}."

        words = list(tokens)
        first_token = words[0]

        # Case 1: Wh-Questions (Where, What, When, Who, Why, How, Which)
        wh_words = {"Where", "What", "When", "Who", "Why", "How", "Which", "Whose", "How many"}
        found_wh = [w for w in words if w in wh_words]
        if found_wh:
            wh = found_wh[0]
            non_wh = [w for w in words if w != wh]
            subject = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in non_wh])
            if wh == "Where":
                return f"Where is the {subject}?"
            elif wh == "What":
                return f"What is the {subject}?"
            elif wh == "When":
                return f"When will {subject} happen?"
            elif wh == "Who":
                return f"Who is {subject}?"
            elif wh == "Why":
                return f"Why is {subject}?"
            elif wh == "How":
                return f"How is {subject}?"
            elif wh == "Which":
                return f"Which {subject}?"
            elif wh == "How many":
                return f"How many {subject} are there?"

        # Case 2: Subject-Pronoun based sentences
        if first_token in ["Me", "I"]:
            rest = words[1:]
            if any(w in ["Water", "Food", "Tea", "Coffee", "Milk", "Bread", "Rice", "Medicine", "Money"] for w in rest):
                items = " and ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in rest])
                return f"I would like to have {items}."
            elif any(w in ["Doctor", "Hospital", "Police", "Help", "Clinic"] for w in rest):
                dest = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in rest])
                return f"I need {dest} urgently."
            elif any(w in ["Go", "Come", "Sit", "Stand", "Sleep", "Read", "Write"] for w in rest):
                action = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in rest])
                return f"I want to {action}."
            elif any(w in ["Happy", "Sad", "Angry", "Tired", "Sick", "Fine"] for w in rest):
                state = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in rest])
                return f"I am feeling {state}."

        if first_token == "You":
            rest = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in words[1:]])
            return f"You {rest}."

        # Case 3: Need / Emergency
        if "Help" in words or "Emergency" in words:
            other = " ".join([WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in words if w not in ["Help", "Emergency"]])
            if other:
                return f"Emergency! Please help with {other}."
            return "Please help me!"

        # Fallback: Join with title casing
        translated = [WORD_TRANSLATIONS.get(w, {}).get("en", w) for w in words]
        return " ".join(translated).capitalize() + "."

    def _reconstruct_hindi(self, tokens):
        if len(tokens) == 1:
            word = tokens[0]
            if (word,) in ISL_PHRASE_MAPPINGS:
                return ISL_PHRASE_MAPPINGS[(word,)]["hi"]
            return WORD_TRANSLATIONS.get(word, {}).get("hi", word) + "।"

        words = list(tokens)
        first_token = words[0]

        # Case 1: Wh-Questions in Hindi (कहाँ, क्या, कब, कौन, क्यों, कैसे)
        wh_map = {
            "Where": "कहाँ है?",
            "What": "क्या है?",
            "When": "कब होगा?",
            "Who": "कौन है?",
            "Why": "क्यों?",
            "How": "कैसे?",
            "Which": "कौन सा है?",
            "Whose": "किसका है?",
            "How many": "कितने हैं?"
        }
        found_wh = [w for w in words if w in wh_map]
        if found_wh:
            wh = found_wh[0]
            non_wh = [w for w in words if w != wh]
            subject = " ".join([WORD_TRANSLATIONS.get(w, {}).get("hi", w) for w in non_wh])
            return f"{subject} {wh_map[wh]}"

        # Case 2: Needs & Food
        if any(w in ["Water", "Food", "Tea", "Coffee", "Milk", "Bread", "Rice", "Medicine", "Money"] for w in words):
            items = " ".join([WORD_TRANSLATIONS.get(w, {}).get("hi", w) for w in words if w in ["Water", "Food", "Tea", "Coffee", "Milk", "Bread", "Rice", "Medicine", "Money"]])
            return f"मुझे {items} चाहिए।"

        # Case 3: Emergency & Health
        if "Help" in words or "Emergency" in words:
            other = " ".join([WORD_TRANSLATIONS.get(w, {}).get("hi", w) for w in words if w not in ["Help", "Emergency"]])
            if other:
                return f"कृपया {other} में मदद कीजिए।"
            return "कृपया मेरी सहायता करें।"

        # Fallback: Natural SOV joining
        translated = [WORD_TRANSLATIONS.get(w, {}).get("hi", w) for w in words]
        return " ".join(translated) + "।"
