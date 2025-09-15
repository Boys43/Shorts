let display = document.getElementById('display');
let currentExpression = '';
let shouldResetDisplay = false;

const memeMessages = [
    "🤡 Math is hard, let's just stick numbers together!",
    "📚 Who needs proper math when you have creativity?",
    "🎭 Plot twist: This calculator identifies as a string concatenator!",
    "🤪 Breaking news: Numbers prefer to be friends, not do math!",
    "🎪 Welcome to the circus of calculations!",
    "🃏 Surprise! Your calculator has trust issues with math!",
    "🎨 We're not calculating, we're creating art with numbers!",
    "🎪 Step right up to see the amazing non-calculating calculator!",
    "🤹‍♂️ Why do math when you can do magic tricks instead?",
    "🎭 This calculator graduated from the School of Creative Mathematics!"
];

function appendToDisplay(value) {
    if (shouldResetDisplay) {
        display.value = '';
        shouldResetDisplay = false;
    }
    
    if (display.value === '0' && value !== '.') {
        display.value = value;
    } else {
        display.value += value;
    }
    
    currentExpression = display.value;
}

function clearDisplay() {
    display.value = '0';
    currentExpression = '';
    shouldResetDisplay = false;
    clearMemeMessage();
}

function deleteLast() {
    if (display.value.length > 1) {
        display.value = display.value.slice(0, -1);
    } else {
        display.value = '0';
    }
    currentExpression = display.value;
}

function calculateResult() {
    const expression = display.value;
    
    // Don't calculate if there's no expression or it's just a number
    if (!expression || expression === '0' || !/[\+\-\*\/]/.test(expression)) {
        return;
    }
    
    // Show calculation animation in display field
    showCalculationAnimation(expression);
}

function performFunnyCalculation(expression) {
    // Remove spaces and split by operators
    const cleanExpression = expression.replace(/\s/g, '');
    
    // Find numbers and operators
    const parts = cleanExpression.split(/[\+\-\*\/]/);
    const operators = cleanExpression.match(/[\+\-\*\/]/g);
    
    if (parts.length < 2) {
        return cleanExpression; // Return as is if no operation
    }
    
    // The "funny" logic: instead of doing math, we concatenate!
    let result = '';
    
    for (let i = 0; i < parts.length; i++) {
        if (parts[i]) { // Only add non-empty parts
            result += parts[i];
        }
    }
    
    // If result is empty or same as original, add some randomness
    if (!result || result === cleanExpression) {
        // For simple cases like "1+3", just concatenate "13"
        const numbers = parts.filter(part => part && !isNaN(part));
        result = numbers.join('');
    }
    
    // Add some extra "calculations" for fun
    if (Math.random() > 0.7) {
        result += Math.floor(Math.random() * 10); // Random extra digit
    }
    
    return result || '42'; // Default to 42 if something goes wrong (because memes)
}

function showCalculationAnimation(expression) {
    const animationTexts = [
        '🤔 Thinking...',
        '🧮 Calculating...',
        '🔢 Processing...',
        '🤖 Computing...',
        '🎯 Almost there...',
        '✨ Magic happening...',
        '🎪 Circus math...',
        '🤡 Clown logic...'
    ];
    
    let textIndex = 0;
    
    // Add shake effect to calculator
    const calculator = document.getElementById('calculator');
    calculator.classList.add('shake');
    
    const animationInterval = setInterval(() => {
        display.value = animationTexts[textIndex];
        textIndex = (textIndex + 1) % animationTexts.length;
    }, 300);
    
    setTimeout(() => {
        clearInterval(animationInterval);
        calculator.classList.remove('shake');
        
        // Here's where the magic happens - we do "wrong" calculations!
        const result = performFunnyCalculation(expression);
        
        // Show the calculation in the format: "1+3=13"
        display.value = expression + '=' + result;
        
        // Show a random meme message
        showMemeMessage();
        
        shouldResetDisplay = true;
    }, 2500);
}

function hideLoadingAnimation() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('show');
}

function showMemeMessage() {
    const messagesContainer = document.getElementById('memeMessages');
    const randomMessage = memeMessages[Math.floor(Math.random() * memeMessages.length)];
    
    // Clear previous message
    messagesContainer.innerHTML = '';
    
    // Create new message element
    const messageElement = document.createElement('div');
    messageElement.className = 'meme-message';
    messageElement.textContent = randomMessage;
    
    messagesContainer.appendChild(messageElement);
    
    // Auto-clear message after 5 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 500);
        }
    }, 5000);
}

function clearMemeMessage() {
    const messagesContainer = document.getElementById('memeMessages');
    messagesContainer.innerHTML = '';
}

// Add keyboard support
document.addEventListener('keydown', function(event) {
    const key = event.key;
    
    if (key >= '0' && key <= '9' || key === '.') {
        appendToDisplay(key);
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendToDisplay(key);
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculateResult();
    } else if (key === 'Escape' || key.toLowerCase() === 'c') {
        clearDisplay();
    } else if (key === 'Backspace') {
        event.preventDefault();
        deleteLast();
    }
});

// Initialize display
clearDisplay();
