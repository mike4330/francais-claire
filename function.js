// Utility function to shuffle an array in place (Fisher-Yates algorithm)
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

// Utility to get a cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Utility to set a cookie with optional expiration
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

// Generate a random UUID v4
function generateUUIDv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Weighted random selection utility function
function weightedRandomSelect(options, weights) {
    // Create cumulative weight array
    const cumulativeWeights = [];
    let sum = 0;
    for (let i = 0; i < weights.length; i++) {
        sum += weights[i];
        cumulativeWeights[i] = sum;
    }
    
    // Generate random number and find corresponding option
    const random = Math.random() * sum;
    for (let i = 0; i < cumulativeWeights.length; i++) {
        if (random <= cumulativeWeights[i]) {
            return options[i];
        }
    }
    
    // Fallback to first option
    return options[0];
}

// Generate cache key for audio files
function generateCacheKey(text, voiceId) {
    // Use same MD5 approach as server (here, base64 and string manipulation)
    return btoa(text + '_' + voiceId).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
} 