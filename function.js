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

// Centralized question loading function
// Loads compiled question files from source/compile workflow
async function loadQuestionBank(options = {}) {
    const defaultOptions = {
        files: ['questions/q-compiled-a.json', 'questions/q-compiled-b.json', 'questions/q-compiled-c.json'],
        // Note: fallbackFiles removed as monolithic files are now empty (source/compile workflow only)
        useCompiled: true, // Always use compiled files (monolithic files deprecated)
        levels: null, // null = all levels, or array like ['A1', 'A2', 'B1']
        enableLogging: false,
        logLevel: 3 // 1=error, 2=warn, 3=info
    };
    
    const config = { ...defaultOptions, ...options };
    
    function log(level, ...args) {
        if (config.enableLogging && level <= config.logLevel) {
            const prefix = level === 1 ? '❌' : level === 2 ? '⚠️' : '📚';
            console.log(prefix, 'QuestionLoader:', ...args);
        }
    }
    
    try {
        const filesToLoad = config.files; // Always use compiled files
        log(3, 'Loading question files:', filesToLoad, '(compiled)');
        
        // Fetch all files in parallel with error handling
        const responses = await Promise.all(
            filesToLoad.map(async (filename) => {
                try {
                    const response = await fetch(filename);
                    return { filename, response, error: null };
                } catch (error) {
                    return { filename, response: null, error };
                }
            })
        );
        
        // Process responses and extract question data
        const questionData = await Promise.all(
            responses.map(async ({ filename, response, error }) => {
                if (error) {
                    log(2, `Network error for ${filename}:`, error.message);
                    return { filename, questions: [], error: error.message };
                }
                
                if (!response.ok) {
                    log(2, `HTTP ${response.status} for ${filename}: ${response.statusText}`);
                    return { filename, questions: [], error: `HTTP ${response.status}` };
                }
                
                try {
                    const data = await response.json();
                    
                    // Handle both old format {questions: [...]} and new compiled format with metadata
                    let questions = [];
                    if (data.questions && Array.isArray(data.questions)) {
                        questions = data.questions;
                    } else if (Array.isArray(data)) {
                        // Handle direct array format
                        questions = data;
                    } else {
                        log(2, `Unexpected data format in ${filename}:`, Object.keys(data));
                        questions = [];
                    }
                    
                    log(3, `✅ ${filename}: ${questions.length} questions loaded`);
                    return { filename, questions, error: null };
                } catch (parseError) {
                    log(1, `JSON parse error for ${filename}:`, parseError.message);
                    return { filename, questions: [], error: 'Parse error' };
                }
            })
        );
        
        // Flatten and filter questions
        let allQuestions = questionData.flatMap(data => data.questions);
        
        // Apply level filtering if specified
        if (config.levels && Array.isArray(config.levels)) {
            const beforeCount = allQuestions.length;
            allQuestions = allQuestions.filter(q => 
                config.levels.includes(q.difficulty)
            );
            log(3, `Filtered ${beforeCount} → ${allQuestions.length} questions for levels:`, config.levels);
        }
        
        log(3, `Total questions loaded: ${allQuestions.length}`);
        
        return {
            success: true,
            questions: allQuestions,
            fileStats: questionData ? questionData.map(({ filename, questions, error }) => ({
                filename,
                count: questions ? questions.length : 0,
                error
            })) : [],
            totalCount: allQuestions.length,
            compiledMode: config.useCompiled,
            loadedFrom: filesToLoad
        };
        
    } catch (error) {
        log(1, 'Critical loading error:', error);
        return {
            success: false,
            questions: [],
            fileStats: [],
            totalCount: 0,
            error: error.message
        };
    }
} 