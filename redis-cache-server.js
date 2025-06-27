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
                    
                case 'track_vocab_miss':
                    await handleTrackVocabMiss(ws, data.words, data.uuid);
                    break;
                case 'get_vocab_miss_stats':
                    await handleGetVocabMissStats(ws, data.uuid);
                    break;
                case 'clear_vocab_miss':
                    await handleClearVocabMiss(ws, data.uuid);
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

// Handler to track vocabulary misses
async function handleTrackVocabMiss(ws, words, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        if (!Array.isArray(words)) {
            throw new Error('Words must be an array');
        }
        if (!uuid) {
            throw new Error('UUID is required for vocab miss tracking');
        }
        for (const word of words) {
            if (typeof word === 'string' && word.trim().length > 0) {
                const key = `vocabmiss:${uuid}:${word.toLowerCase()}`;
                const newCount = await redisClient.incr(key);
                log(`🔢 Vocab miss incremented: ${uuid} | ${word.toLowerCase()} = ${newCount}`);
            }
        }
        ws.send(JSON.stringify({
            type: 'track_vocab_miss_result',
            success: true,
            words: words
        }));
        log(`📝 Tracked vocab misses for ${uuid}: ${words.join(', ')}`);
    } catch (error) {
        log('❌ Vocab miss tracking error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Vocab miss tracking failed'
        }));
    }
}

// Handler to get all vocabulary miss stats
async function handleGetVocabMissStats(ws, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        if (!uuid) {
            throw new Error('UUID is required for vocab miss stats');
        }
        const keys = await redisClient.keys(`vocabmiss:${uuid}:*`);
        const stats = {};
        for (const key of keys) {
            const word = key.replace(`vocabmiss:${uuid}:`, '');
            const count = await redisClient.get(key);
            stats[word] = parseInt(count, 10) || 0;
        }
        ws.send(JSON.stringify({
            type: 'vocab_miss_stats',
            stats: stats
        }));
        log(`📊 Vocab miss stats sent for ${uuid} (${keys.length} words)`);
    } catch (error) {
        log('❌ Vocab miss stats error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Vocab miss stats retrieval failed'
        }));
    }
}

// Handler to clear all vocabulary miss stats
async function handleClearVocabMiss(ws, uuid) {
    try {
        if (!redisClient.isReady) {
            throw new Error('Redis client not ready');
        }
        if (!uuid) {
            throw new Error('UUID is required for clearing vocab miss stats');
        }
        const keys = await redisClient.keys(`vocabmiss:${uuid}:*`);
        let deleted = 0;
        if (keys.length > 0) {
            deleted = await redisClient.del(keys);
        }
        ws.send(JSON.stringify({
            type: 'clear_vocab_miss_result',
            deleted: deleted
        }));
        log(`🗑️ Cleared ${deleted} vocab miss stats for ${uuid}`);
    } catch (error) {
        log('❌ Clear vocab miss error:', error.message);
        ws.send(JSON.stringify({
            type: 'error',
            message: 'Vocab miss clear failed'
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