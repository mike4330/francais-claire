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
                    await handleTrackQuestionResult(ws, data.uuid, data.difficulty, data.isCorrect);
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