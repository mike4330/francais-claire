#!/usr/bin/env node

const fs = require('fs');

// Safe ID mapping that avoids conflicts
const idMapping = {
    // A-level questions (keep as is)
    1: 1,   // A1 - Keep
    21: 21, // A2 - Keep  
    22: 22, // A2 - Keep
    27: 27, // A1 - Keep
    
    // B-level questions (320-334 range)
    3: 320,  // B1 - Weather forecast
    7: 321,  // B1 - Political simplification
    9: 322,  // B2 - Storm description
    11: 323, // B2 - Pope/vocations
    12: 324, // B2 - Environmental lawsuit
    14: 325, // B1 - Weather listening
    15: 326, // B2 - Celebrity listening
    16: 327, // B2 - Road worker accident
    18: 328, // B1 - Election listening
    19: 329, // B2 - Reality TV separation
    20: 330, // B1 - Reality TV listening
    23: 331, // B1 - Fraud death sentence
    24: 332, // B1 - Fraud listening
    25: 333, // B1 - Weather emergency
    26: 334, // B1 - Learning strategies
    
    // C-level questions (469-472 range)
    5: 469,  // C1 - Celebrity Venice story
    6: 470,  // C2 - Complex politics
    10: 471, // C1 - Healthcare policy listening
    17: 472  // C1 - Deputy election uncertainty
};

// Parent question reference updates
const parentQuestionUpdates = {
    14: 320, // Was parentQuestion: 3, now parentQuestion: 320
    15: 469, // Was parentQuestion: 5, now parentQuestion: 469
    18: 472, // Was parentQuestion: 17, now parentQuestion: 472
    20: 329, // Was parentQuestion: 19, now parentQuestion: 329
    21: 320, // Was parentQuestion: 3, now parentQuestion: 320
    24: 331  // Was parentQuestion: 23, now parentQuestion: 331
};

function safeRenumberQuestions() {
    console.log('🔄 Starting SAFE question renumbering process...');
    
    // Read questions.json
    const questionsPath = 'questions/questions.json';
    if (!fs.existsSync(questionsPath)) {
        console.log('❌ questions.json not found');
        return;
    }
    
    const data = JSON.parse(fs.readFileSync(questionsPath, 'utf8'));
    const questions = data.questions || [];
    
    console.log(`📊 Found ${questions.length} questions to renumber`);
    
    // Renumber questions and update parent references
    const updatedQuestions = questions.map(question => {
        const oldId = question.id;
        const newId = idMapping[oldId];
        
        if (newId === undefined) {
            console.log(`⚠️  No mapping found for question ID ${oldId} - keeping original`);
            return question;
        }
        
        // Update the question ID
        const updatedQuestion = { ...question, id: newId };
        
        // Update parentQuestion if this question has one that needs updating
        if (question.parentQuestion && parentQuestionUpdates[oldId]) {
            updatedQuestion.parentQuestion = parentQuestionUpdates[oldId];
            console.log(`🔗 Updated question ${newId}: parentQuestion ${question.parentQuestion} → ${parentQuestionUpdates[oldId]}`);
        }
        
        console.log(`🔄 Renumbered question: ${oldId} → ${newId} (${question.difficulty})`);
        return updatedQuestion;
    });
    
    // Sort by new ID
    updatedQuestions.sort((a, b) => a.id - b.id);
    
    // Create updated data structure
    const updatedData = {
        ...data,
        questions: updatedQuestions
    };
    
    // Create a timestamped backup
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = `questions/questions-backup-${timestamp}.json`;
    fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
    console.log(`💾 Created backup at ${backupPath}`);
    
    fs.writeFileSync(questionsPath, JSON.stringify(updatedData, null, 2));
    console.log(`✅ Updated ${questionsPath} with SAFE new IDs`);
    
    // Summary
    console.log('\n📈 Safe Renumbering Summary:');
    console.log(`   Total questions processed: ${updatedQuestions.length}`);
    console.log(`   Parent references updated: ${Object.keys(parentQuestionUpdates).length}`);
    console.log(`   A-level questions (1-199): ${updatedQuestions.filter(q => q.id <= 199).length}`);
    console.log(`   B-level questions (200-399): ${updatedQuestions.filter(q => q.id >= 200 && q.id <= 399).length}`);
    console.log(`   C-level questions (400-499): ${updatedQuestions.filter(q => q.id >= 400).length}`);
    
    // Show ID ranges used
    const aIds = updatedQuestions.filter(q => q.id <= 199).map(q => q.id);
    const bIds = updatedQuestions.filter(q => q.id >= 200 && q.id <= 399).map(q => q.id);
    const cIds = updatedQuestions.filter(q => q.id >= 400).map(q => q.id);
    
    console.log('\n🎯 ID Ranges Used:');
    if (aIds.length > 0) console.log(`   A-level: ${Math.min(...aIds)}-${Math.max(...aIds)}`);
    if (bIds.length > 0) console.log(`   B-level: ${Math.min(...bIds)}-${Math.max(...bIds)}`);
    if (cIds.length > 0) console.log(`   C-level: ${Math.min(...cIds)}-${Math.max(...cIds)}`);
    
    console.log('\n🎯 Next steps:');
    console.log('   1. Use jmv tool to move questions to individual source files');
    console.log('   2. Organize into questions-a.json, questions-b.json, questions-c.json');
    console.log('   3. Recompile the question banks');
    console.log('   ⚠️  Note: Question 10 still references missing parentQuestion 8');
}

if (require.main === module) {
    safeRenumberQuestions();
}

module.exports = { safeRenumberQuestions, idMapping, parentQuestionUpdates };