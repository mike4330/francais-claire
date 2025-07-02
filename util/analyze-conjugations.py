#!/usr/bin/env python3
"""
French Conjugation Coverage Analyzer
Analyzes coverage of top 20 verbs in ALL their conjugated forms
"""

import json
import sqlite3
import re
import os
from collections import defaultdict, Counter

# ANSI Color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Determine database path based on current directory
if os.path.exists("database/lexique-experiments/lexique.sqlite3"):
    LEXIQUE_DB_PATH = "database/lexique-experiments/lexique.sqlite3"
else:
    LEXIQUE_DB_PATH = "../database/lexique-experiments/lexique.sqlite3"

def connect_to_lexique():
    """Connect to the Lexique database"""
    if not os.path.exists(LEXIQUE_DB_PATH):
        print(f"{Colors.RED}❌ Lexique database not found at {LEXIQUE_DB_PATH}{Colors.END}")
        return None
    
    try:
        conn = sqlite3.connect(LEXIQUE_DB_PATH)
        return conn
    except Exception as e:
        print(f"{Colors.RED}❌ Error connecting to database: {e}{Colors.END}")
        return None

def get_top_verbs(limit=20):
    """Get the top N most frequent verbs"""
    conn = connect_to_lexique()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lemme, freqfilms2 
            FROM verbe 
            WHERE freqfilms2 > 0 
            ORDER BY freqfilms2 DESC 
            LIMIT ?
        """, (limit,))
        
        top_verbs = cursor.fetchall()
        conn.close()
        
        print(f"{Colors.CYAN}{Colors.BOLD}🎯 TOP {limit} MOST FREQUENT VERBS:{Colors.END}")
        for i, (verb, freq) in enumerate(top_verbs, 1):
            print(f"  {Colors.YELLOW}{i:2d}.{Colors.END} {Colors.GREEN}{verb:12}{Colors.END} - {Colors.WHITE}{freq:8.1f}{Colors.END}")
        
        return [verb for verb, freq in top_verbs]
        
    except Exception as e:
        print(f"❌ Error getting top verbs: {e}")
        conn.close()
        return []

def get_all_conjugated_forms(verb_infinitive):
    """Get all conjugated forms of a verb from Lexique database"""
    conn = connect_to_lexique()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ortho, cgram, freqfilms2 
            FROM lexique 
            WHERE lemme = ? AND cgram LIKE '%VER%'
            ORDER BY freqfilms2 DESC
        """, (verb_infinitive,))
        
        forms = cursor.fetchall()
        conn.close()
        
        return [(form, grammar, freq) for form, grammar, freq in forms if form != verb_infinitive]
        
    except Exception as e:
        print(f"❌ Error getting conjugated forms for {verb_infinitive}: {e}")
        if conn:
            conn.close()
        return []

def load_question_files():
    """Load and combine all question files"""
    # Determine path based on current directory
    if os.path.exists("questions/questions.json"):
        path_prefix = "questions/"
    elif os.path.exists("../questions/questions.json"):
        path_prefix = "../questions/"
    else:
        path_prefix = "questions/"
    
    question_files = [f'{path_prefix}questions.json', f'{path_prefix}questions-a.json', 
                     f'{path_prefix}questions-b.json', f'{path_prefix}questions-c.json']
    all_questions = []
    
    for filename in question_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'questions' in data:
                        questions = data['questions']
                    elif isinstance(data, list):
                        questions = data
                    else:
                        continue
                    
                    all_questions.extend(questions)
                    print(f"{Colors.GREEN}✅ Loaded {len(questions)} questions from {filename}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error loading {filename}: {e}{Colors.END}")
    
    return all_questions

def extract_text_from_questions(questions):
    """Extract all text content from questions"""
    all_text = ""
    
    for q in questions:
        if 'audioText' in q:
            all_text += " " + q['audioText']
        if 'question' in q:
            all_text += " " + q['question']
        if 'options' in q:
            for option in q['options']:
                all_text += " " + option
        if 'explanation' in q:
            all_text += " " + q['explanation']
    
    return all_text.lower()

def analyze_verb_conjugation_coverage(top_verbs, question_text):
    """Analyze conjugation coverage for each top verb"""
    words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
    word_counts = Counter(words)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}" + "="*80)
    print("📊 CONJUGATION COVERAGE ANALYSIS")
    print("="*80 + f"{Colors.END}")
    
    total_coverage = {}
    
    for i, verb in enumerate(top_verbs, 1):
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 {i:2d}. {verb.upper()} (Rank #{i}){Colors.END}")
        print("-" * 50)
        
        # Get all conjugated forms
        conjugated_forms = get_all_conjugated_forms(verb)
        
        if not conjugated_forms:
            print(f"   {Colors.RED}❌ No conjugated forms found in database{Colors.END}")
            continue
        
        # Check which forms appear in questions
        found_forms = []
        missing_forms = []
        
        # Include infinitive
        if verb in word_counts:
            found_forms.append((verb, "infinitive", word_counts[verb]))
        
        # Check conjugated forms
        for form, grammar, freq in conjugated_forms:
            if form in word_counts:
                found_forms.append((form, grammar, word_counts[form]))
            else:
                missing_forms.append((form, grammar, freq))
        
        # Sort by frequency in our questions
        found_forms.sort(key=lambda x: x[2], reverse=True)
        
        # Report findings
        print(f"   {Colors.GREEN}✅ FOUND FORMS: {len(found_forms)} forms found in questions{Colors.END}")
        
        print(f"   ❌ MISSING FORMS ({len(missing_forms)}) - Top by frequency:")
        missing_forms.sort(key=lambda x: x[2], reverse=True)  # Sort by Lexique frequency
        for form, grammar, freq in missing_forms[:8]:  # Top 8 missing
            print(f"      {form:12} ({grammar:15}) - freq: {freq:6.1f}")
        
        if len(missing_forms) > 8:
            print(f"      ... and {len(missing_forms) - 8} more missing forms")
        
        # Coverage statistics
        total_forms = len(conjugated_forms) + 1  # +1 for infinitive
        coverage_pct = len(found_forms) / total_forms * 100 if total_forms > 0 else 0
        
        total_coverage[verb] = {
            'found': len(found_forms),
            'total': total_forms,
            'coverage': coverage_pct
        }
        
        print(f"   📈 Coverage: {len(found_forms)}/{total_forms} forms ({coverage_pct:.1f}%)")
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 OVERALL CONJUGATION COVERAGE SUMMARY")
    print("="*80)
    
    avg_coverage = sum(data['coverage'] for data in total_coverage.values()) / len(total_coverage)
    print(f"Average coverage across top {len(top_verbs)} verbs: {avg_coverage:.1f}%")
    
    print(f"\n🎯 COVERAGE BY VERB:")
    for verb, data in total_coverage.items():
        status = "🟢" if data['coverage'] > 50 else "🟡" if data['coverage'] > 20 else "🔴"
        print(f"  {status} {verb:12} {data['found']:2d}/{data['total']:2d} ({data['coverage']:5.1f}%)")
    
    # Priority recommendations
    low_coverage = [(v, d) for v, d in total_coverage.items() if d['coverage'] < 30]
    if low_coverage:
        print(f"\n🚨 PRIORITY VERBS NEEDING MORE CONJUGATIONS:")
        for verb, data in sorted(low_coverage, key=lambda x: x[1]['coverage']):
            print(f"   {verb:12} - only {data['coverage']:4.1f}% coverage")

def main():
    print("🔍 French Conjugation Coverage Analyzer")
    print("="*50)
    
    # Get top 25 verbs
    top_verbs = get_top_verbs(25)
    
    if not top_verbs:
        print("❌ Cannot proceed without verb data")
        return
    
    # Load questions
    questions = load_question_files()
    
    if not questions:
        print("❌ No questions found")
        return
    
    print(f"\n📊 Loaded {len(questions)} questions total")
    
    # Extract text
    question_text = extract_text_from_questions(questions)
    
    # Analyze conjugation coverage
    analyze_verb_conjugation_coverage(top_verbs, question_text)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 