# French Language Learning App - System Internals

## 🏗️ Infrastructure Overview

This document describes the internal architecture and setup of the French language learning application across multiple environments.

## 📍 System Architecture

### Local Development Environment
- **Location**: `/var/www/html/language`
- **Redis Role**: Master (Primary cache and data store)
- **IP**: 192.168.1.6 (internal) / 108.28.39.81 (public)
- **Services**: 
  - Redis Server (port 6379) - Master instance
  - WebSocket Cache Server (port 8080) - `redis-cache-server.js`

### Production VPS Environment (Hetzner)
- **Location**: `/var/www/html/language` (and `/home/mike/var/www/html/language`)
- **IP**: 5.78.137.108
- **Redis Role**: Slave (Replica of local Redis)
- **Services**:
  - Redis Server (port 6379) - Slave instance
  - WebSocket Cache Server (port 8080) - `redis-cache-server.js`

## 🔄 Redis Replication Setup

### Master-Slave Configuration
```
Local Redis (Master) ←──── VPS Redis (Slave)
108.28.39.81:6379           5.78.137.108:6379
```

**Replication Flow:**
1. **Local Redis** serves as the primary data store
2. **VPS Redis** automatically replicates all data in real-time
3. Audio cache, user performance data, and analytics sync instantly
4. Both systems can serve cached audio without regeneration

### Configuration Details

**Local Redis Master:**
- Bind: `0.0.0.0:6379` (accepts external connections)
- Protected Mode: `no`
- Firewall: Port 6379 open for VPS access

**VPS Redis Slave:**
- Command: `redis-cli slaveof 108.28.39.81 6379`
- Auto-reconnection on network issues
- Read-only replica of master data

## 🌐 WebSocket Cache Server

### Purpose
- **Audio Caching**: Stores expensive TTS-generated French audio
- **Performance Tracking**: User learning analytics and response data
- **Cache Management**: Handles cache operations, stats, and eviction

### Communication Protocol
```
French App (Browser) ←──WebSocket──→ redis-cache-server.js ←──→ Redis
                        Port 8080                               Port 6379
```

### Key Operations
- `check_cache`: Verify if audio exists in cache
- `store_cache`: Save new TTS audio with TTL
- `track_detailed_question_response`: Store user performance data
- `get_user_question_performance`: Retrieve learning analytics

## 📊 Question Database System

### File Structure
```
questions/
├── source/              # Individual question files (q1.json - q1037.json+)
│   ├── q1.json         # A1 level questions (ID 1-251)
│   ├── q252.json       # B1/B2 level questions (ID 252-999)
│   └── q1000.json      # C1/C2 level questions (ID 1000+)
├── q-compiled-a.json   # Compiled A1/A2 questions
├── q-compiled-b.json   # Compiled B1/B2 questions
└── q-compiled-c.json   # Compiled C1/C2 questions
```

### Question Types
- **comprehension**: English questions testing understanding
- **listening**: French "Qu'est-ce que vous avez entendu?" questions
- **fill-in-the-blank**: Missing word completion
- **FIB-reading**: Reading comprehension with blanks

### CEFR Level Distribution
- **A-Level**: 229 questions (A1/A2 - Beginner/Elementary)
- **B-Level**: 590 questions (B1/B2 - Intermediate/Upper-Intermediate)  
- **C-Level**: 190 questions (C1/C2 - Advanced/Proficiency)
- **Total**: 1,009+ questions

## 🛠️ Development Tools

### Question Management
- `compile-questions.js`: Compiles source files into app-ready JSON
- `util/getid`: Gets next available question ID by level
- `util/lemma-coverage.py`: Analyzes vocabulary gaps for strategic question creation
- `jmv.js`: Moves questions between files

### Analytics & Analysis
- `util/analyze-questions.sh`: Comprehensive question database analysis
- `util/analyze-conjugations.py`: Verb conjugation coverage analysis
- `util/analyze-tag-network.py`: Content topic network analysis

## 🔧 Cache Expiration Settings

### Redis TTL Configuration
| Data Type | Duration | Purpose |
|-----------|----------|---------|
| Audio Cache | 30 days | TTS-generated French audio |
| Individual Responses | 90 days | Detailed user interaction tracking |
| User Performance | 1 year | Per-user question performance stats |
| Global Analytics | 1 year | Overall question difficulty metrics |

## 🚀 Deployment Architecture

### Automatic Services
- **Redis Server**: Auto-starts on boot (both systems)
- **Cache Server**: Manual start required (`node redis-cache-server.js`)

### Network Requirements
- **Port 6379**: Open on local machine for Redis replication
- **Port 8080**: Open where WebSocket clients need access
- **Stable Internet**: Required for real-time Redis replication

### Data Synchronization
- **Real-time Replication**: All Redis data syncs instantly
- **Application Files**: Manual rsync between environments
- **Question Database**: Synchronized via file transfer

## 🔍 Monitoring & Debugging

### Redis Monitoring
```bash
# Monitor real-time Redis commands
redis-cli monitor

# Check replication status
redis-cli info replication

# View cache keys
redis-cli keys "audio:*"
```

### Application Logs
- **WebSocket Server**: Console output from `redis-cache-server.js`
- **Redis Server**: `/var/log/redis/redis-server.log`
- **Browser Console**: Cache operations and performance tracking

## 💡 Key Benefits

### Performance
- **Instant Audio Serving**: Cached audio available on both systems
- **No Duplicate TTS Costs**: Audio generated once, used everywhere
- **Real-time Analytics**: User performance tracked across environments

### Reliability
- **Automatic Failover**: If local Redis fails, VPS has complete data copy
- **Data Persistence**: Redis handles automatic data durability
- **Network Resilience**: Slave auto-reconnects on connection loss

---

*Last Updated: July 2025*
*Total Questions: 1,037+*
*Redis Version: 6.0.16 (local) / 7.0.15 (VPS)*