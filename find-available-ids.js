#!/usr/bin/env node

const fs = require('fs');

function findAvailableIds() {
    // Collect all existing IDs from compiled files and source files
    const existingIds = new Set();
    
    // Check compiled files
    const compiledFiles = ['questions/q-compiled-a.json', 'questions/q-compiled-b.json', 'questions/q-compiled-c.json'];
    for (const file of compiledFiles) {
        if (fs.existsSync(file)) {
            const data = JSON.parse(fs.readFileSync(file, 'utf8'));
            const questions = data.questions || [];
            questions.forEach(q => existingIds.add(q.id));
        }
    }
    
    // Check source files
    const sourceDir = 'questions/source';
    if (fs.existsSync(sourceDir)) {
        const sourceFiles = fs.readdirSync(sourceDir).filter(f => f.startsWith('q') && f.endsWith('.json'));
        for (const file of sourceFiles) {
            try {
                const data = JSON.parse(fs.readFileSync(`${sourceDir}/${file}`, 'utf8'));
                if (data.id) existingIds.add(data.id);
            } catch (e) {
                console.log(`Warning: Could not read ${file}`);
            }
        }
    }
    
    console.log(`Found ${existingIds.size} existing IDs`);
    
    // Find available ranges
    const ranges = {
        'A-level (1-199)': { min: 1, max: 199, available: [] },
        'B-level (200-399)': { min: 200, max: 399, available: [] },
        'C-level (400-499)': { min: 400, max: 499, available: [] }
    };
    
    for (const [rangeName, range] of Object.entries(ranges)) {
        for (let id = range.min; id <= range.max; id++) {
            if (!existingIds.has(id)) {
                range.available.push(id);
            }
        }
        console.log(`\n${rangeName}: ${range.available.length} available IDs`);
        if (range.available.length > 0) {
            console.log(`  First 10 available: ${range.available.slice(0, 10).join(', ')}`);
            if (range.available.length > 10) {
                console.log(`  ... and ${range.available.length - 10} more`);
            }
        }
    }
    
    return ranges;
}

function createSafeMapping() {
    const ranges = findAvailableIds();
    
    // Questions from questions.json that need new IDs
    const questionsToRenumber = [
        { id: 3, difficulty: 'B1' },   // Weather forecast
        { id: 5, difficulty: 'C1' },   // Celebrity Venice
        { id: 6, difficulty: 'C2' },   // Politics PS/LFI
        { id: 7, difficulty: 'B1' },   // Politics simplified
        { id: 9, difficulty: 'B2' },   // Storm
        { id: 10, difficulty: 'C1' },  // Healthcare listening
        { id: 11, difficulty: 'B2' },  // Pope vocations
        { id: 12, difficulty: 'B2' },  // Environmental lawsuit
        { id: 14, difficulty: 'B1' },  // Weather listening
        { id: 15, difficulty: 'B2' },  // Celebrity listening
        { id: 16, difficulty: 'B2' },  // Road worker
        { id: 17, difficulty: 'C1' },  // Deputy election
        { id: 18, difficulty: 'B1' },  // Election listening
        { id: 19, difficulty: 'B2' },  // Reality TV
        { id: 20, difficulty: 'B1' },  // Reality TV listening
        { id: 23, difficulty: 'B1' },  // Fraud
        { id: 24, difficulty: 'B1' },  // Fraud listening
        { id: 25, difficulty: 'B1' },  // Weather emergency
        { id: 26, difficulty: 'B1' }   // Learning strategies
    ];
    
    // A-level questions (keep as is): 1, 21, 22, 27
    
    console.log('\n=== SAFE RENUMBERING PLAN ===\n');
    
    const mapping = {};
    
    // B-level questions (200-399)
    const bQuestions = questionsToRenumber.filter(q => q.difficulty.startsWith('B'));
    const availableB = ranges['B-level (200-399)'].available;
    
    console.log('B-level questions (B1/B2):');
    bQuestions.forEach((q, index) => {
        if (index < availableB.length) {
            const newId = availableB[index];
            mapping[q.id] = newId;
            console.log(`  ${q.id} → ${newId} (${q.difficulty})`);
        } else {
            console.log(`  ERROR: Not enough B-level IDs for question ${q.id}`);
        }
    });
    
    // C-level questions (400-499)
    const cQuestions = questionsToRenumber.filter(q => q.difficulty.startsWith('C'));
    const availableC = ranges['C-level (400-499)'].available;
    
    console.log('\nC-level questions (C1/C2):');
    cQuestions.forEach((q, index) => {
        if (index < availableC.length) {
            const newId = availableC[index];
            mapping[q.id] = newId;
            console.log(`  ${q.id} → ${newId} (${q.difficulty})`);
        } else {
            console.log(`  ERROR: Not enough C-level IDs for question ${q.id}`);
        }
    });
    
    console.log('\nA-level questions (keeping original IDs):');
    console.log('  1 → 1 (A1)');
    console.log('  21 → 21 (A2)');
    console.log('  22 → 22 (A2)');
    console.log('  27 → 27 (A1)');
    
    return mapping;
}

if (require.main === module) {
    createSafeMapping();
}

module.exports = { findAvailableIds, createSafeMapping };