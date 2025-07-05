#!/usr/bin/env node

/**
 * JSON Move (jmv) - Tool for extracting individual questions from monolithic JSON files
 * 
 * Usage: node jmv.js <question_id> <source_file>
 * Example: node jmv.js 132 questions-a.json
 * 
 * This will:
 * 1. Find question with ID 132 in questions-a.json
 * 2. Create questions/source/q132.json with that question
 * 3. Remove the question from questions-a.json
 * 4. Update the compiled files
 */

const fs = require('fs');
const path = require('path');

// ANSI colors for console output
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
    reset: '\x1b[0m',
    bright: '\x1b[1m'
};

function log(color, emoji, ...args) {
    console.log(`${colors[color]}${emoji} ${args.join(' ')}${colors.reset}`);
}

function validateArgs() {
    if (process.argv.length !== 4) {
        log('red', '❌', 'Usage: node jmv.js <question_id> <source_file>');
        log('yellow', '💡', 'Example: node jmv.js 132 questions-a.json');
        log('yellow', '💡', 'Example: node jmv.js 250 questions/questions-b.json');
        process.exit(1);
    }
    
    const questionId = parseInt(process.argv[2]);
    const sourceFile = process.argv[3];
    
    if (isNaN(questionId)) {
        log('red', '❌', 'Question ID must be a number');
        process.exit(1);
    }
    
    return { questionId, sourceFile };
}

function resolveSourceFile(sourceFile) {
    // Handle both relative and absolute paths
    if (sourceFile.startsWith('questions/')) {
        return sourceFile;
    } else if (sourceFile.startsWith('questions-')) {
        return `questions/${sourceFile}`;
    } else {
        return sourceFile;
    }
}

function loadQuestionFile(filePath) {
    try {
        const fullPath = path.resolve(filePath);
        const content = fs.readFileSync(fullPath, 'utf8');
        const data = JSON.parse(content);
        
        // Handle both formats: {questions: [...]} and direct array
        if (data.questions && Array.isArray(data.questions)) {
            return { questions: data.questions, format: 'object', metadata: data };
        } else if (Array.isArray(data)) {
            return { questions: data, format: 'array', metadata: null };
        } else {
            throw new Error('Unexpected JSON format');
        }
    } catch (error) {
        log('red', '❌', `Error loading ${filePath}:`, error.message);
        process.exit(1);
    }
}

function saveQuestionFile(filePath, questions, format, metadata) {
    try {
        let output;
        if (format === 'object') {
            output = {
                ...metadata,
                questions: questions
            };
        } else {
            output = questions;
        }
        
        const content = JSON.stringify(output, null, 2);
        fs.writeFileSync(filePath, content);
        return true;
    } catch (error) {
        log('red', '❌', `Error saving ${filePath}:`, error.message);
        return false;
    }
}

function createSourceFile(questionId, question) {
    const sourceDir = 'questions/source';
    const sourceFile = path.join(sourceDir, `q${questionId}.json`);
    
    // Ensure source directory exists
    if (!fs.existsSync(sourceDir)) {
        fs.mkdirSync(sourceDir, { recursive: true });
        log('blue', '📁', `Created directory: ${sourceDir}`);
    }
    
    // Check if source file already exists - NEVER overwrite
    if (fs.existsSync(sourceFile)) {
        log('red', '❌', `Source file already exists: ${sourceFile}`);
        log('red', '🚫', 'jmv will not overwrite existing files for safety');
        log('yellow', '💡', 'Options:');
        log('white', '  1.', `Manually delete: rm ${sourceFile}`);
        log('white', '  2.', `Choose a different question ID`);
        log('white', '  3.', `Edit the existing file directly if needed`);
        return false;
    }
    
    // Save the individual question
    const content = JSON.stringify(question, null, 2);
    try {
        fs.writeFileSync(sourceFile, content);
        log('green', '✅', `Created source file: ${sourceFile}`);
        return true;
    } catch (error) {
        log('red', '❌', `Error creating source file:`, error.message);
        return false;
    }
}

function findAndExtractQuestion(questionId, sourceFile) {
    log('blue', '🔍', `Looking for question ID ${questionId} in ${sourceFile}...`);
    
    const resolvedFile = resolveSourceFile(sourceFile);
    const { questions, format, metadata } = loadQuestionFile(resolvedFile);
    
    log('cyan', '📚', `Loaded ${questions.length} questions from ${resolvedFile}`);
    
    // Find the question
    const questionIndex = questions.findIndex(q => q.id === questionId);
    if (questionIndex === -1) {
        log('red', '❌', `Question ID ${questionId} not found in ${resolvedFile}`);
        log('yellow', '💡', 'Available question IDs:');
        const ids = questions.map(q => q.id).sort((a, b) => a - b);
        console.log('   ', ids.slice(0, 20).join(', '), ids.length > 20 ? '...' : '');
        process.exit(1);
    }
    
    const question = questions[questionIndex];
    log('green', '✅', `Found question: "${question.audioText?.substring(0, 50)}..."`);
    
    // Create source file
    if (!createSourceFile(questionId, question)) {
        process.exit(1);
    }
    
    // Remove question from original array
    questions.splice(questionIndex, 1);
    log('yellow', '➖', `Removed question ${questionId} from ${resolvedFile}`);
    
    // Save the updated file
    if (!saveQuestionFile(resolvedFile, questions, format, metadata)) {
        process.exit(1);
    }
    
    log('green', '✅', `Updated ${resolvedFile} (${questions.length} questions remaining)`);
    return true;
}

function main() {
    const { questionId, sourceFile } = validateArgs();
    
    log('magenta', '🚀', `JSON Move (jmv) - Extracting question ${questionId}`);
    log('blue', '📂', `Source file: ${sourceFile}`);
    log('blue', '📝', `Target: questions/source/q${questionId}.json`);
    console.log();
    
    if (findAndExtractQuestion(questionId, sourceFile)) {
        console.log();
        log('green', '🎉', 'Question extraction completed successfully!');
        log('yellow', '💡', 'Next steps:');
        log('white', '  1.', 'Run: node compile-questions.js');
        log('white', '  2.', 'Verify the compiled files contain your changes');
        log('white', '  3.', 'Consider running: bash util/analyze-questions.sh');
    }
}

// Run the main function
if (require.main === module) {
    main();
}

module.exports = { findAndExtractQuestion, createSourceFile };