#!/usr/bin/env node

/**
 * Question Compilation Script
 * 
 * Transition Process:
 * questions-a.json + questions/source/q*.json → q-compiled-a.json
 * questions-b.json + questions/source/q*.json → q-compiled-b.json  
 * questions-c.json + questions/source/q*.json → q-compiled-c.json
 */

const fs = require('fs');
const path = require('path');

class QuestionCompiler {
    constructor() {
        this.sourceDir = 'questions/source';
        this.outputDir = 'questions';
        this.compiledPrefix = 'q-compiled-';
        this.configFile = 'config.json';
        
        // Load ranges from config.json
        this.loadConfig();
    }
    
    loadConfig() {
        try {
            const config = JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
            this.ranges = {};
            
            for (const [key, value] of Object.entries(config.levelRanges)) {
                this.ranges[key] = {
                    min: value.minId,
                    max: value.maxId,
                    levels: value.levels
                };
            }
            
            this.log('info', `📋 Loaded level ranges from ${this.configFile}`);
        } catch (error) {
            this.log('error', `Failed to load ${this.configFile}: ${error.message}`);
            this.log('info', 'Using default ranges...');
            // Fallback to hardcoded ranges
            this.ranges = {
                'a': { min: 1, max: 199, levels: ['A1', 'A2'] },
                'b': { min: 200, max: 399, levels: ['B1', 'B2'] },
                'c': { min: 400, max: 499, levels: ['C1', 'C2'] }
            };
        }
    }

    log(level, ...args) {
        const prefix = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : '✅';
        console.log(prefix, ...args);
    }

    async compile() {
        try {
            this.log('info', '🔄 Starting question compilation...');
            
            // Load source questions
            const sourceQuestions = await this.loadSourceQuestions();
            this.log('info', `📁 Loaded ${sourceQuestions.length} source questions`);
            
            // Compile each level
            for (const level of ['a', 'b', 'c']) {
                await this.compileLevel(level, sourceQuestions);
            }
            
            this.log('info', '🎉 Compilation completed successfully!');
            
        } catch (error) {
            this.log('error', 'Compilation failed:', error.message);
            process.exit(1);
        }
    }

    async loadSourceQuestions() {
        const sourceQuestions = [];
        
        if (!fs.existsSync(this.sourceDir)) {
            this.log('warn', `Source directory ${this.sourceDir} doesn't exist, creating...`);
            fs.mkdirSync(this.sourceDir, { recursive: true });
            return sourceQuestions;
        }

        const files = fs.readdirSync(this.sourceDir)
            .filter(file => file.startsWith('q') && file.endsWith('.json'))
            .sort((a, b) => {
                const numA = parseInt(a.match(/q(\d+)\.json/)?.[1] || '0');
                const numB = parseInt(b.match(/q(\d+)\.json/)?.[1] || '0');
                return numA - numB;
            });

        for (const file of files) {
            try {
                const filePath = path.join(this.sourceDir, file);
                const content = fs.readFileSync(filePath, 'utf8');
                const question = JSON.parse(content);
                
                // Validate question structure
                if (this.validateQuestion(question)) {
                    sourceQuestions.push({ ...question, sourceFile: file });
                } else {
                    this.log('warn', `Invalid question in ${file}, skipping`);
                }
            } catch (error) {
                this.log('warn', `Error reading ${file}:`, error.message);
            }
        }

        return sourceQuestions;
    }

    validateQuestion(question) {
        // Base required fields for all questions
        const baseRequired = ['id', 'question', 'questionType', 'options', 'correct', 'explanation', 'difficulty', 'source', 'tags'];
        
        // Check for either audioText (standard) or audioTemplate (dynamic template)
        const hasAudioText = 'audioText' in question;
        const hasAudioTemplate = 'audioTemplate' in question && 'templateVariables' in question;
        
        if (!hasAudioText && !hasAudioTemplate) {
            return false;
        }
        
        // Validate base required fields
        for (const field of baseRequired) {
            if (!(field in question)) {
                return false;
            }
        }

        // Validate options array
        if (!Array.isArray(question.options) || question.options.length !== 4) {
            return false;
        }

        // Validate correct index
        if (typeof question.correct !== 'number' || question.correct < 0 || question.correct > 3) {
            return false;
        }

        // Additional validation for template questions
        if (hasAudioTemplate) {
            if (typeof question.audioTemplate !== 'string') {
                return false;
            }
            
            if (typeof question.templateVariables !== 'object' || question.templateVariables === null) {
                return false;
            }
            
            // Validate template variables structure
            for (const [varName, varData] of Object.entries(question.templateVariables)) {
                if (!varData.options || !Array.isArray(varData.options) || varData.options.length === 0) {
                    return false;
                }
                
                // Optional: validate weights if provided
                if (varData.weights) {
                    if (!Array.isArray(varData.weights) || varData.weights.length !== varData.options.length) {
                        return false;
                    }
                }
            }
        }

        return true;
    }

    async compileLevel(level, sourceQuestions) {
        const range = this.ranges[level];
        const originalFile = `questions/questions-${level}.json`;
        const compiledFile = `${this.outputDir}/${this.compiledPrefix}${level}.json`;

        // Load original questions (legacy support)
        let originalQuestions = [];
        if (fs.existsSync(originalFile)) {
            try {
                const originalData = JSON.parse(fs.readFileSync(originalFile, 'utf8'));
                originalQuestions = originalData.questions || [];
            } catch (error) {
                this.log('warn', `Error reading ${originalFile}:`, error.message);
            }
        }

        // Filter source questions for this level
        const levelSourceQuestions = sourceQuestions.filter(q => {
            const id = parseInt(q.id);
            const inRange = id >= range.min && id <= range.max;
            const matchesLevel = range.levels.includes(q.difficulty);
            return inRange && matchesLevel;
        });

        // Merge questions (source questions override originals by ID)
        const questionMap = new Map();
        
        // Add original questions first
        originalQuestions.forEach(q => {
            questionMap.set(q.id, q);
        });
        
        // Override with source questions
        levelSourceQuestions.forEach(q => {
            const { sourceFile, ...cleanQuestion } = q; // Remove sourceFile metadata
            questionMap.set(q.id, cleanQuestion);
        });

        // Sort by ID and create final array
        const compiledQuestions = Array.from(questionMap.values())
            .sort((a, b) => a.id - b.id);

        // Create compiled output
        const compiledData = {
            questions: compiledQuestions,
            metadata: {
                compiledAt: new Date().toISOString(),
                totalQuestions: compiledQuestions.length,
                level: level.toUpperCase(),
                idRange: `${range.min}-${range.max}`,
                difficulties: range.levels
            }
        };

        // Write compiled file
        fs.writeFileSync(compiledFile, JSON.stringify(compiledData, null, 2));
        this.log('info', `✅ Level ${level.toUpperCase()}: ${compiledQuestions.length} questions → ${compiledFile}`);
    }


    // Utility method to create a new question template
    createQuestionTemplate(id, difficulty) {
        const template = {
            id: parseInt(id),
            audioText: "",
            question: "",
            questionType: "comprehension",
            options: ["", "", "", ""],
            correct: 0,
            explanation: "",
            difficulty: difficulty,
            source: "",
            tags: [],
            timeCreated: Math.floor(Date.now() / 1000)
        };

        const filename = `${this.sourceDir}/q${id}.json`;
        fs.writeFileSync(filename, JSON.stringify(template, null, 2));
        this.log('info', `📝 Created template: ${filename}`);
        return filename;
    }
}

// CLI Interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const compiler = new QuestionCompiler();

    if (args.length === 0) {
        // Default: compile all
        compiler.compile();
    } else if (args[0] === 'template') {
        // Create template: node compile-questions.js template <id> <difficulty>
        const id = args[1];
        const difficulty = args[2] || 'A2';
        
        if (!id) {
            console.log('Usage: node compile-questions.js template <id> [difficulty]');
            process.exit(1);
        }
        
        compiler.createQuestionTemplate(id, difficulty);
    } else if (args[0] === 'validate') {
        // Validate source questions only
        compiler.loadSourceQuestions().then(questions => {
            console.log(`✅ Validated ${questions.length} source questions`);
        });
    } else {
        console.log('Usage:');
        console.log('  node compile-questions.js           # Compile all questions');
        console.log('  node compile-questions.js template <id> [difficulty]  # Create template');
        console.log('  node compile-questions.js validate  # Validate source questions');
    }
}

module.exports = QuestionCompiler;
