const WebSocket = require('ws');
const redis = require('redis');
const crypto = require('crypto');

// Redis client setup
const redisClient = redis.createClient({
    socket: {
        host: 'localhost',
        port: 6379
    }
});

// WebSocket server setup
const wss = new WebSocket.Server({ 
    port: 8080,
    perMessageDeflate: false 
});

console.log('🔥 Redis Audio Cache Server starting...');

// Redis event handlers
redisClient.on('connect', () => {
    console.log('✅ Connected to Redis');
});

redisClient.on('ready', () => {
    console.log('✅ Redis client ready');
});

redisClient.on('error', (err) => {
    console.error('❌ Redis error:', err);
});

redisClient.on('end', () => {
    console.log('❌ Redis connection ended');
});

// Initialize Redis connection
async function initializeRedis() {
    try {
        await redisClient.connect();
        console.log('✅ Redis connection established');
    } catch (error) {
        console.error('❌ Failed to connect to Redis:', error);
        process.exit(1);
    }
}

// Helper functions
function generateCacheKey(text, voiceId) {
    return crypto.createHash('md5').update(`${text}_${voiceId}`).digest('hex');
}

function log(message, data = '') {
    console.log(`[${new Date().toISOString()}] ${message}`, data);
}

// WebSocket connection handler
wss.on('connection', (ws) => {
    log('🔌 Client connected');
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            const { action, cacheKey, audioData, text, voiceId } = data;
            
            switch (action) {
                case 'check_cache':
                    await handleCacheCheck(ws, cacheKey || generateCacheKey(text, voiceId));
                    break;
                    
                case 'store_cache':
                    await handleCacheStore(ws, cacheKey || generateCacheKey(text, voiceId), audioData);
                    break;
                    
                case 'get_stats':
                    await handleGetStats(ws);
                    break;
                    
                case 'clear_cache':
                    await handleClearCache(ws);
                    break;
                    
                case 'evict_cache':
                    await handleEvictCache(ws, cacheKey || generateCacheKey(text, voiceId));
                    break;
                    
                case 'ping':
                    ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
                    break;
                    

                    
                case 'track_question_result':
                    log('📊 OLD DIFFICULTY TRACKING called - UUID:', data.uuid, 'Difficulty:', data.difficulty, 'Correct:', data.isCorrect);
                    await handleTrackQuestionResult(ws, data.uuid, data.difficulty, data.isCorrect);
                    break;
                    
                case 'track_detailed_question_response':
                    log('🆕 NEW DETAILED TRACKING called with data:', JSON.stringify(data, null, 2));
                    await handleTrackDetailedQuestionResponse(ws, data);
                    break;
                    
                case 'get_question_analytics':
                    await handleGetQuestionAnalytics(ws, data.questionId);
                    break;
                    
                case 'get_user_question_performance':
                    log('📋 USER PERFORMANCE REQUEST for UUID:', data.uuid);
                    await handleGetUserQuestionPerformance(ws, data.uuid);
                    break;
                case 'get_scoring_stats':
                    await handleGetScoringStats(ws, data.uuid);
                    break;
                case 'clear_scoring_stats':
                    await handleClearScoringStats(ws, data.uuid);
                    break;
                    
                default:
                    ws.send(JSON.stringify({ 
                        type: 'error', 
                        message: `Unknown action: ${action}` 
                    }));
            }
        } catch (error) {
            log('❌ Message handling error:', error.message);
            ws.send(JSON.stringify({ 
                type: 'error', 
                message: 'Invalid message format' 
            }));
        }
    });
    
    ws.on('close', () => {
        log('🔌 Client disconnected');
    });
    
    ws.on('error', (error) => {
        log('❌ WebSocket error:', error.message);
    });
});

// Cache operation handlers
async function handleCacheCheck(ws, cacheKey) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        
        const cached = await redisClient.get(`audio:${cacheKey}`);
        
        ws.send(JSON.stringify({
            type: 'cache_check_result',
            cacheKey: cacheKey,
            exists: !!cached,
            audioData: cached || null
        }));
        
        log(`🔍 Cache check: ${cacheKey} - ${cached ? 'HIT' : 'MISS'}`);
    } catch (error) {
        log('❌ Cache check error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Cache check failed'
        }));
    }
}

async function handleCacheStore(ws, cacheKey, audioData) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        
        // Store with expiration (30 days) - using newer Redis API
        await redisClient.setEx(`audio:${cacheKey}`, 2592000, audioData);
        
        ws.send(JSON.stringify({
            type: 'cache_store_result',
            cacheKey: cacheKey,
            success: true
        }));
        
        log(`💾 Cached audio: ${cacheKey}`);
    } catch (error) {
        log('❌ Cache store error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Cache store failed'
        }));
    }
}

async function handleGetStats(ws) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        
        const keys = await redisClient.keys('audio:*');
        let totalSize = 0;
        
        for (const key of keys) {
            const data = await redisClient.get(key);
            if (data) {
                totalSize += data.length;
            }
        }
        
        // Convert to MB
        const sizeMB = (totalSize / 1024 / 1024).toFixed(2);
        
        ws.send(JSON.stringify({
            type: 'stats_result',
            count: keys.length,
            sizeMB: sizeMB,
            keys: keys.map(k => k.replace('audio:', ''))
        }));
        
        log(`📊 Stats: ${keys.length} files, ${sizeMB}MB`);
    } catch (error) {
        log('❌ Stats error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Stats retrieval failed'
        }));
    }
}

async function handleClearCache(ws) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        
        const keys = await redisClient.keys('audio:*');
        if (keys.length > 0) {
            await redisClient.del(keys);
        }
        
        ws.send(JSON.stringify({
            type: 'clear_cache_result',
            cleared: keys.length
        }));
        
        log(`🗑️ Cleared ${keys.length} cached files`);
    } catch (error) {
        log('❌ Clear cache error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Cache clear failed'
        }));
    }
}

async function handleEvictCache(ws, cacheKey) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        
        const fullKey = `audio:${cacheKey}`;
        const existed = await redisClient.exists(fullKey);
        
        if (existed) {
            await redisClient.del(fullKey);
        }
        
        ws.send(JSON.stringify({
            type: 'evict_cache_result',
            cacheKey: cacheKey,
            evicted: !!existed
        }));
        
        log(`🎯 Evict cache: ${cacheKey} - ${existed ? 'EVICTED' : 'NOT_FOUND'}`);
    } catch (error) {
        log('❌ Evict cache error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Cache evict failed'
        }));
    }
}



// Scoring system handlers
async function handleTrackQuestionResult(ws, uuid, difficulty, isCorrect) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        if (!uuid) {
            throw new Error('UUID is required for question result tracking');
        }

        if (!difficulty) {
            throw new Error('Difficulty level is required for question result tracking');
        }

        // Track total attempts for this difficulty level
        const attemptsKey = `scoring:${uuid}:${difficulty}:attempts`;
        const totalAttempts = await redisClient.incr(attemptsKey);

        // Track correct answers for this difficulty level if correct
        let correctAnswers = 0;
        if (isCorrect) {
            const correctKey = `scoring:${uuid}:${difficulty}:correct`;
            correctAnswers = await redisClient.incr(correctKey);
        } else {
            // Get current correct count without incrementing
            const correctKey = `scoring:${uuid}:${difficulty}:correct`;
            const currentCorrect = await redisClient.get(correctKey);
            correctAnswers = parseInt(currentCorrect) || 0;
        }

        const successRate = totalAttempts > 0 ? Math.round((correctAnswers / totalAttempts) * 100) : 0;

        log(`📊 Question result tracked: ${uuid} | ${difficulty} | ${isCorrect ? 'CORRECT' : 'INCORRECT'} | Success rate: ${successRate}% (${correctAnswers}/${totalAttempts})`);

        ws.send(JSON.stringify({
            type: 'question_result_tracked',
            uuid: uuid,
            difficulty: difficulty,
            isCorrect: isCorrect,
            totalAttempts: totalAttempts,
            correctAnswers: correctAnswers,
            successRate: successRate
        }));

    } catch (error) {
        log('❌ Track question result error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Question result tracking failed'
        }));
    }
}

async function handleGetScoringStats(ws, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        if (!uuid) {
            throw new Error('UUID is required for scoring stats');
        }

        const difficultyLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
        const stats = {};

        for (const difficulty of difficultyLevels) {
            const attemptsKey = `scoring:${uuid}:${difficulty}:attempts`;
            const correctKey = `scoring:${uuid}:${difficulty}:correct`;

            const attempts = await redisClient.get(attemptsKey);
            const correct = await redisClient.get(correctKey);

            const totalAttempts = parseInt(attempts) || 0;
            const correctAnswers = parseInt(correct) || 0;
            const successRate = totalAttempts > 0 ? Math.round((correctAnswers / totalAttempts) * 100) : 0;

            stats[difficulty] = {
                attempts: totalAttempts,
                correct: correctAnswers,
                successRate: successRate
            };
        }

        log(`📊 Scoring stats sent for ${uuid}`);

        ws.send(JSON.stringify({
            type: 'scoring_stats_result',
            uuid: uuid,
            stats: stats
        }));

    } catch (error) {
        log('❌ Get scoring stats error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Get scoring stats failed'
        }));
    }
}

async function handleClearScoringStats(ws, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        if (!uuid) {
            throw new Error('UUID is required for clearing scoring stats');
        }

        const keys = await redisClient.keys(`scoring:${uuid}:*`);
        let deleted = 0;

        if (keys.length > 0) {
            deleted = await redisClient.del(keys);
        }

        log(`🗑️ Cleared ${deleted} scoring stats for ${uuid}`);

        ws.send(JSON.stringify({
            type: 'scoring_stats_cleared',
            uuid: uuid,
            deletedCount: deleted
        }));

    } catch (error) {
        log('❌ Clear scoring stats error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Clear scoring stats failed'
        }));
    }
}

// Detailed question response tracking
async function handleTrackDetailedQuestionResponse(ws, data) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        const { uuid, questionId, isCorrect, responseTime, difficulty, questionType } = data;
        
        log('🔍 DETAILED TRACKING - Extracted data:', {
            uuid: uuid,
            questionId: questionId,
            isCorrect: isCorrect,
            responseTime: responseTime,
            difficulty: difficulty,
            questionType: questionType
        });
        
        if (!uuid || !questionId) {
            throw new Error('UUID and questionId are required for detailed response tracking');
        }

        const timestamp = Date.now();
        const responseKey = `response:${uuid}:${questionId}:${timestamp}`;
        
        log('📝 DETAILED TRACKING - Storing individual response with key:', responseKey);
        
        // Store detailed response data
        const responseData = {
            uuid,
            questionId,
            isCorrect: !!isCorrect,
            responseTime: responseTime || null,
            difficulty: difficulty || null,
            questionType: questionType || null,
            timestamp,
            date: new Date(timestamp).toISOString()
        };
        
        // Store individual response (expires after 90 days)
        await redisClient.setEx(responseKey, 7776000, JSON.stringify(responseData));
        
        // Update question-specific analytics
        const questionStatsKey = `question_stats:${questionId}`;
        const questionStats = await redisClient.hGetAll(questionStatsKey);
        
        const totalAttempts = parseInt(questionStats.total_attempts || '0') + 1;
        const correctAttempts = parseInt(questionStats.correct_attempts || '0') + (isCorrect ? 1 : 0);
        const totalResponseTime = parseFloat(questionStats.total_response_time || '0') + (responseTime || 0);
        const successRate = Math.round((correctAttempts / totalAttempts) * 100);
        const avgResponseTime = responseTime ? Math.round(totalResponseTime / totalAttempts) : null;
        
        // Update question statistics
        await redisClient.hSet(questionStatsKey, {
            total_attempts: totalAttempts.toString(),
            correct_attempts: correctAttempts.toString(),
            success_rate: successRate.toString(),
            total_response_time: totalResponseTime.toString(),
            avg_response_time: avgResponseTime ? avgResponseTime.toString() : '0',
            last_answered: timestamp.toString(),
            difficulty: difficulty || 'unknown',
            question_type: questionType || 'unknown'
        });
        
        // Set expiration for question stats (1 year)
        await redisClient.expire(questionStatsKey, 31536000);
        
        // Also track per-user, per-question statistics for personalized feedback
        const userQuestionKey = `user_question:${uuid}:${questionId}`;
        log('👤 DETAILED TRACKING - Getting user question stats for key:', userQuestionKey);
        const userQuestionStats = await redisClient.hGetAll(userQuestionKey);
        
        const userTotalAttempts = parseInt(userQuestionStats.attempts || '0') + 1;
        const userCorrectAttempts = parseInt(userQuestionStats.correct || '0') + (isCorrect ? 1 : 0);
        const userSuccessRate = Math.round((userCorrectAttempts / userTotalAttempts) * 100);
        
        log('👤 DETAILED TRACKING - User stats for Q' + questionId + ':', {
            previousAttempts: parseInt(userQuestionStats.attempts || '0'),
            newTotalAttempts: userTotalAttempts,
            previousCorrect: parseInt(userQuestionStats.correct || '0'),
            newCorrectAttempts: userCorrectAttempts,
            newSuccessRate: userSuccessRate + '%'
        });
        
        await redisClient.hSet(userQuestionKey, {
            attempts: userTotalAttempts.toString(),
            correct: userCorrectAttempts.toString(),
            success_rate: userSuccessRate.toString(),
            last_attempted: timestamp.toString(),
            question_id: questionId.toString(),
            difficulty: difficulty || 'unknown',
            question_type: questionType || 'unknown'
        });
        
        // Set expiration for user question stats (1 year)
        await redisClient.expire(userQuestionKey, 31536000);
        
        log('💾 DETAILED TRACKING - Saved user question stats to Redis');
        log(`📝 DETAILED TRACKING COMPLETE: Q${questionId} | ${uuid} | ${isCorrect ? 'CORRECT' : 'INCORRECT'} | ${responseTime}ms | Global: ${successRate}% | Personal: ${userSuccessRate}%`);

        const responseMessage = {
            type: 'detailed_response_tracked',
            questionId,
            uuid,
            isCorrect,
            totalAttempts,
            correctAttempts,
            successRate,
            avgResponseTime,
            userAttempts: userTotalAttempts,
            userCorrect: userCorrectAttempts,
            userSuccessRate: userSuccessRate
        };
        
        log('📤 DETAILED TRACKING - Sending response to client:', JSON.stringify(responseMessage, null, 2));
        ws.send(JSON.stringify(responseMessage));

    } catch (error) {
        log('❌ Track detailed response error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Detailed response tracking failed'
        }));
    }
}

// Get analytics for a specific question
async function handleGetQuestionAnalytics(ws, questionId) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        if (!questionId) {
            throw new Error('QuestionId is required for analytics');
        }

        const questionStatsKey = `question_stats:${questionId}`;
        const stats = await redisClient.hGetAll(questionStatsKey);
        
        if (Object.keys(stats).length === 0) {
            ws.send(JSON.stringify({
                type: 'question_analytics_result',
                questionId,
                stats: null,
                message: 'No data available for this question'
            }));
            return;
        }

        // Get recent responses (last 50)
        const responseKeys = await redisClient.keys(`response:*:${questionId}:*`);
        const recentResponses = [];
        
        // Sort by timestamp and take last 50
        const sortedKeys = responseKeys
            .map(key => {
                const parts = key.split(':');
                return {
                    key,
                    timestamp: parseInt(parts[3])
                };
            })
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, 50);

        for (const { key } of sortedKeys) {
            try {
                const responseData = await redisClient.get(key);
                if (responseData) {
                    recentResponses.push(JSON.parse(responseData));
                }
            } catch (parseError) {
                // Skip invalid JSON entries
                continue;
            }
        }

        const analytics = {
            totalAttempts: parseInt(stats.total_attempts || '0'),
            correctAttempts: parseInt(stats.correct_attempts || '0'),
            successRate: parseInt(stats.success_rate || '0'),
            avgResponseTime: parseInt(stats.avg_response_time || '0'),
            lastAnswered: new Date(parseInt(stats.last_answered || '0')).toISOString(),
            difficulty: stats.difficulty || 'unknown',
            questionType: stats.question_type || 'unknown',
            recentResponses: recentResponses
        };

        log(`📊 Question analytics sent for Q${questionId}: ${analytics.successRate}% success (${analytics.correctAttempts}/${analytics.totalAttempts})`);

        ws.send(JSON.stringify({
            type: 'question_analytics_result',
            questionId,
            stats: analytics
        }));

    } catch (error) {
        log('❌ Get question analytics error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Get question analytics failed'
        }));
    }
}

// Get user's personal performance on all questions they've attempted
async function handleGetUserQuestionPerformance(ws, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }

        if (!uuid) {
            throw new Error('UUID is required for user question performance');
        }

        // Get all user question performance keys
        const userQuestionKeys = await redisClient.keys(`user_question:${uuid}:*`);
        const questionPerformances = [];

        for (const key of userQuestionKeys) {
            try {
                const stats = await redisClient.hGetAll(key);
                
                if (Object.keys(stats).length > 0) {
                    const questionId = parseInt(stats.question_id);
                    const attempts = parseInt(stats.attempts || '0');
                    const correct = parseInt(stats.correct || '0');
                    const successRate = parseInt(stats.success_rate || '0');
                    const lastAttempted = new Date(parseInt(stats.last_attempted || '0')).toISOString();
                    
                    questionPerformances.push({
                        questionId,
                        attempts,
                        correct,
                        successRate,
                        lastAttempted,
                        difficulty: stats.difficulty || 'unknown',
                        questionType: stats.question_type || 'unknown'
                    });
                }
            } catch (parseError) {
                // Skip invalid entries
                continue;
            }
        }

        // Sort by question ID for consistent display
        questionPerformances.sort((a, b) => a.questionId - b.questionId);

        log(`📊 User question performance sent for ${uuid}: ${questionPerformances.length} questions attempted`);

        ws.send(JSON.stringify({
            type: 'user_question_performance_result',
            uuid,
            questionPerformances,
            totalQuestionsAttempted: questionPerformances.length
        }));

    } catch (error) {
        log('❌ Get user question performance error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Get user question performance failed'
        }));
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down Redis Cache Server...');
    try {
        await redisClient.quit();
        console.log('✅ Redis connection closed');
    } catch (error) {
        console.error('❌ Error closing Redis:', error);
    }
    wss.close();
    process.exit(0);
});

// Start the server
async function startServer() {
    await initializeRedis();
    console.log('🚀 WebSocket server listening on port 8080');
    console.log('🔗 Connect with: ws://localhost:8080');
}

// Initialize everything
startServer().catch(console.error); 