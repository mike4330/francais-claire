#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ID mapping based on difficulty levels
const idMapping = {
    // A-level questions (1-199)
    1: 1,   // A1 - Keep as is
    21: 21, // A2 - Keep as is  
    22: 22, // A2 - Keep as is
    27: 27, // A1 - Keep as is
    
    // B-level questions (200-399)
    3: 200,  // B1 - Weather forecast
    7: 201,  // B1 - Political simplification
    9: 202,  // B2 - Storm description
    11: 203, // B2 - Pope/vocations
    12: 204, // B2 - Environmental lawsuit
    14: 205, // B1 - Weather listening
    15: 206, // B2 - Celebrity listening
    16: 207, // B2 - Road worker accident
    18: 208, // B1 - Election listening
    19: 209, // B2 - Reality TV separation
    20: 210, // B1 - Reality TV listening
    23: 211, // B1 - Fraud death sentence
    24: 212, // B1 - Fraud listening
    25: 213, // B1 - Weather emergency
    26: 214, // B1 - Learning strategies
    
    // C-level questions (400-499)
    5: 400,  // C1 - Celebrity Venice story
    6: 401,  // C2 - Complex politics
    10: 402, // C1 - Healthcare policy listening
    17: 403  // C1 - Deputy election uncertainty
};

// Parent question reference updates
const parentQuestionUpdates = {
    14: 200, // Was parentQuestion: 3, now parentQuestion: 200
    15: 400, // Was parentQuestion: 5, now parentQuestion: 400
    18: 403, // Was parentQuestion: 17, now parentQuestion: 403
    20: 209, // Was parentQuestion: 19, now parentQuestion: 209
    21: 200, // Was parentQuestion: 3, now parentQuestion: 200
    24: 211  // Was parentQuestion: 23, now parentQuestion: 211
};

function renumberQuestions() {
    console.log('🔄 Starting question renumbering process...');
    
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
            console.log(`⚠️  No mapping found for question ID ${oldId}`);
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
    
    // Write back to file
    const backupPath = 'questions/questions-backup.json';
    fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
    console.log(`💾 Created backup at ${backupPath}`);
    
    fs.writeFileSync(questionsPath, JSON.stringify(updatedData, null, 2));
    console.log(`✅ Updated ${questionsPath} with new IDs`);
    
    // Summary
    console.log('\n📈 Renumbering Summary:');
    console.log(`   Total questions processed: ${updatedQuestions.length}`);
    console.log(`   Parent references updated: ${Object.keys(parentQuestionUpdates).length}`);
    
    console.log('\n🎯 Next steps:');
    console.log('   1. Run the jmv tool to move questions to individual source files');
    console.log('   2. Organize into questions-a.json, questions-b.json, questions-c.json');
    console.log('   3. Recompile the question banks');
}

if (require.main === module) {
    renumberQuestions();
}

module.exports = { renumberQuestions, idMapping, parentQuestionUpdates };