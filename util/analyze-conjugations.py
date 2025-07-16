#!/usr/bin/env python3
"""
French Conjugation Coverage Analyzer
Analyzes coverage of top 25 verbs in ALL their conjugated forms
Uses compiled question files (q-compiled-*.json) for most accurate analysis
Filters out well-covered verbs (>70%) to focus on verbs needing attention
"""

import json
import sqlite3
import re
import os
from collections import defaultdict, Counter

# Configuration
COVERAGE_FILTER_THRESHOLD = 40  # Skip verbs with coverage above this percentage

# Blacklist for conjugate forms that are used as nouns/other parts of speech in questions
# Format: {word: [list_of_question_ids_where_its_not_a_conjugate]}
CONJUGATE_BLACKLIST = {
    'crue': [602],  # Used as noun "en crue" (in flood) in q602, not as past participle of "croire"
}

# Blacklist for literary/rare verb forms not suitable for everyday French learning
LITERARY_VERB_BLACKLIST = {
    # Passé simple forms (literary only)
    'mourut', 'commença', 'devint', 'vint', 'tint', 'prit', 'fit', 'dit', 'vit', 'fut',
    'eut', 'alla', 'donna', 'porta', 'parla', 'regarda', 'trouva', 'passa', 'sentit',
    'sortit', 'partit', 'rentra', 'arriva', 'resta', 'tomba', 'leva', 'tourna', 'plut',
    'commença', 'ouvrit', 'offrit', 'couvrit', 'souffrit', 'découvrit',
    
    # Rare/morbid conjugations
    'mourrait', 'mourrais', 'mourrons', 'mourrez', 'mortes', 'morts',
    
    # Very literary conditional/subjunctive variants
    'sût', 'eût', 'fût', 'dût', 'pût', 'vînt', 'tînt', 'prît', 'fît', 'dît', 'vît',
    
    # Very rare conditionals and low-frequency forms (< 1.0 freq)
    'plairais', 'plairas', 'plairont', 'plaisais', 
    
    # Archaic or very formal forms
    'messied', 'messiéront', 'gît', 'gisent', 'gisant'
}

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

def get_top_verbs(limit=50):
    """Get the top N most frequent verbs (extended list for filtering)"""
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
        
        print(f"{Colors.CYAN}{Colors.BOLD}🎯 TOP {limit} MOST FREQUENT VERBS (for filtering):{Colors.END}")
        for i, (verb, freq) in enumerate(top_verbs, 1):
            print(f"  {Colors.YELLOW}{i:2d}.{Colors.END} {Colors.GREEN}{verb:12}{Colors.END} - {Colors.WHITE}{freq:8.1f}{Colors.END}")
        
        return [verb for verb, freq in top_verbs]
        
    except Exception as e:
        print(f"❌ Error getting top verbs: {e}")
        conn.close()
        return []

def get_verbs_needing_attention(target_count=25):
    """Dynamically expand verb pool until we have enough verbs needing attention"""
    conn = connect_to_lexique()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Get total verb count for limit calculations
        cursor.execute("SELECT COUNT(*) FROM verbe WHERE freqfilms2 > 0")
        total_verbs = cursor.fetchone()[0]
        
        print(f"{Colors.CYAN}🔄 Dynamic verb pool expansion (targeting {target_count} verbs needing attention)...{Colors.END}")
        
        pool_size = 250  # Start with 250 verbs
        verbs_needing_attention = []
        
        while len(verbs_needing_attention) < target_count and pool_size <= total_verbs:
            # Get current pool of verbs
            cursor.execute("""
                SELECT lemme, freqfilms2 
                FROM verbe 
                WHERE freqfilms2 > 0 
                ORDER BY freqfilms2 DESC 
                LIMIT ?
            """, (pool_size,))
            
            top_verbs = cursor.fetchall()
            
            # Quick coverage check for all verbs in current pool
            print(f"{Colors.YELLOW}📊 Checking coverage for top {pool_size} verbs...{Colors.END}")
            
            # Load questions for coverage analysis
            questions = load_question_files()
            if not questions:
                print(f"{Colors.RED}❌ Cannot load questions for coverage analysis{Colors.END}")
                break
            
            question_text = extract_text_from_questions(questions)
            words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
            word_counts = Counter(words)
            
            # Reset the list for this iteration
            verbs_needing_attention = []
            
            for verb, freq in top_verbs:
                # Quick coverage calculation
                conjugated_forms = get_all_conjugated_forms(verb)
                if not conjugated_forms:
                    continue
                
                # Check which forms appear in questions
                found_forms = []
                if verb in word_counts:
                    found_forms.append(verb)
                
                for form, grammar, form_freq in conjugated_forms:
                    if form in word_counts:
                        found_forms.append(form)
                
                # Coverage statistics
                total_forms = len(conjugated_forms) + 1  # +1 for infinitive
                coverage_pct = len(found_forms) / total_forms * 100 if total_forms > 0 else 0
                
                # Add to attention list if below threshold
                if coverage_pct <= COVERAGE_FILTER_THRESHOLD:
                    verbs_needing_attention.append(verb)
                    
                    # Stop when we have enough
                    if len(verbs_needing_attention) >= target_count:
                        break
            
            # If we have enough verbs, we're done
            if len(verbs_needing_attention) >= target_count:
                print(f"{Colors.GREEN}✅ Found {len(verbs_needing_attention)} verbs needing attention from pool of {pool_size}{Colors.END}")
                break
            
            # Otherwise, expand the pool
            old_pool_size = pool_size
            pool_size += 50  # Expand by 50 each time
            print(f"{Colors.YELLOW}🔄 Only found {len(verbs_needing_attention)} verbs needing attention, expanding pool from {old_pool_size} to {pool_size}...{Colors.END}")
        
        conn.close()
        
        if len(verbs_needing_attention) < target_count:
            print(f"{Colors.YELLOW}⚠️  Only found {len(verbs_needing_attention)} verbs needing attention (out of {total_verbs} total verbs){Colors.END}")
        
        return verbs_needing_attention[:target_count]
        
    except Exception as e:
        print(f"❌ Error in dynamic verb selection: {e}")
        if conn:
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
    """Load and combine all compiled question files"""
    # Determine path based on current directory
    if os.path.exists("questions/q-compiled-a.json"):
        path_prefix = "questions/"
    elif os.path.exists("../questions/q-compiled-a.json"):
        path_prefix = "../questions/"
    else:
        path_prefix = "questions/"
    
    # Use compiled question files for better coverage and accuracy
    question_files = [f'{path_prefix}q-compiled-a.json', 
                     f'{path_prefix}q-compiled-b.json', 
                     f'{path_prefix}q-compiled-c.json']
    all_questions = []
    
    print(f"{Colors.CYAN}📁 Using compiled question files for analysis...{Colors.END}")
    
    for filename in question_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'questions' in data:
                        questions = data['questions']
                        # Show metadata if available
                        if 'metadata' in data:
                            meta = data['metadata']
                            print(f"{Colors.GREEN}✅ Loaded {len(questions)} questions from {filename}{Colors.END}")
                            print(f"   📊 Compiled: {meta.get('compiledAt', 'unknown')}")
                            print(f"   📈 Sources: {meta.get('originalQuestions', 0)} original + {meta.get('sourceQuestions', 0)} individual")
                        else:
                            print(f"{Colors.GREEN}✅ Loaded {len(questions)} questions from {filename}{Colors.END}")
                    elif isinstance(data, list):
                        questions = data
                        print(f"{Colors.GREEN}✅ Loaded {len(questions)} questions from {filename}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}⚠️  Unexpected format in {filename}{Colors.END}")
                        continue
                    
                    all_questions.extend(questions)
            except Exception as e:
                print(f"{Colors.RED}❌ Error loading {filename}: {e}{Colors.END}")
    
    return all_questions

def is_word_blacklisted(word, question_id):
    """Check if a word should be excluded from conjugate analysis for a specific question"""
    if word.lower() in CONJUGATE_BLACKLIST:
        blacklisted_questions = CONJUGATE_BLACKLIST[word.lower()]
        return question_id in blacklisted_questions
    return False

def extract_text_from_questions(questions):
    """Extract all text content from questions, respecting conjugate blacklist"""
    all_text = ""
    
    for q in questions:
        question_id = q.get('id', 0)
        
        # Collect text from all fields
        text_parts = []
        if 'audioText' in q:
            text_parts.append(q['audioText'])
        if 'question' in q:
            text_parts.append(q['question'])
        if 'options' in q:
            for option in q['options']:
                text_parts.append(option)
        if 'explanation' in q:
            text_parts.append(q['explanation'])
        
        # Process text and apply blacklist
        for text_part in text_parts:
            words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', text_part.lower())
            filtered_words = []
            
            for word in words:
                if not is_word_blacklisted(word, question_id):
                    filtered_words.append(word)
                else:
                    print(f"{Colors.YELLOW}⚠️  Blacklisted '{word}' in question {question_id} (not a conjugate){Colors.END}")
            
            all_text += " " + " ".join(filtered_words)
    
    return all_text.lower()

def analyze_verb_conjugation_coverage(verbs_needing_attention, question_text):
    """Analyze conjugation coverage for pre-filtered verbs that need attention"""
    words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
    word_counts = Counter(words)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}" + "="*80)
    print("📊 CONJUGATION COVERAGE ANALYSIS")
    print("="*80 + f"{Colors.END}")
    
    total_coverage = {}
    
    print(f"{Colors.CYAN}📋 Analyzing {len(verbs_needing_attention)} verbs needing attention (≤{COVERAGE_FILTER_THRESHOLD}% coverage):{Colors.END}")
    if len(LITERARY_VERB_BLACKLIST) > 0:
        print(f"{Colors.CYAN}🚫 Filtering out {len(LITERARY_VERB_BLACKLIST)} literary/rare forms from analysis{Colors.END}")
    
    # Get verb ranks for display (need to query database again)
    conn = connect_to_lexique()
    verb_ranks = {}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lemme, freqfilms2, 
                       ROW_NUMBER() OVER (ORDER BY freqfilms2 DESC) as rank
                FROM verbe 
                WHERE freqfilms2 > 0
            """)
            
            for verb, freq, rank in cursor.fetchall():
                verb_ranks[verb] = rank
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not determine verb ranks: {e}{Colors.END}")
        finally:
            conn.close()
    
    # Detailed analysis for verbs needing attention
    for verb in verbs_needing_attention:
        rank = verb_ranks.get(verb, "?")
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 {verb.upper()} (Rank #{rank}){Colors.END}")
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
        
        # Check conjugated forms (filter out blacklisted literary forms)
        for form, grammar, freq in conjugated_forms:
            if form in word_counts:
                found_forms.append((form, grammar, word_counts[form]))
            elif form not in LITERARY_VERB_BLACKLIST:
                missing_forms.append((form, grammar, freq))
        
        # Sort by frequency in our questions
        found_forms.sort(key=lambda x: x[2], reverse=True)
        
        # Coverage statistics
        total_forms = len(conjugated_forms) + 1  # +1 for infinitive
        coverage_pct = len(found_forms) / total_forms * 100 if total_forms > 0 else 0
        
        total_coverage[verb] = {
            'found': len(found_forms),
            'total': total_forms,
            'coverage': coverage_pct
        }
        
        # Report findings
        print(f"   {Colors.GREEN}✅ FOUND FORMS: {len(found_forms)} forms found in questions{Colors.END}")
        
        print(f"   ❌ MISSING FORMS ({len(missing_forms)}) - Top by frequency:")
        missing_forms.sort(key=lambda x: x[2], reverse=True)  # Sort by Lexique frequency
        for form, grammar, freq in missing_forms[:6]:  # Top 6 missing
            print(f"      {form:12} ({grammar:15}) - freq: {freq:6.1f}")
        
        if len(missing_forms) > 6:
            print(f"      ... and {len(missing_forms) - 6} more missing forms")
        
        # Coverage statistics
        print(f"   📈 Coverage: {total_coverage[verb]['found']}/{total_coverage[verb]['total']} forms ({coverage_pct:.1f}%)")
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 OVERALL CONJUGATION COVERAGE SUMMARY")
    print("="*80)
    
    # Calculate statistics for analyzed verbs
    analyzed_coverage = sum(total_coverage[verb]['coverage'] for verb in verbs_needing_attention) / len(verbs_needing_attention)
    
    print(f"Verbs analyzed (≤{COVERAGE_FILTER_THRESHOLD}%): {len(verbs_needing_attention)} (needing attention)")
    print(f"Average coverage of analyzed verbs: {analyzed_coverage:.1f}%")
    
    print(f"\n🎯 VERBS NEEDING ATTENTION (≤{COVERAGE_FILTER_THRESHOLD}% coverage):")
    for verb in verbs_needing_attention:
        data = total_coverage[verb]
        status = "🟡" if data['coverage'] > 40 else "🟠" if data['coverage'] > 20 else "🔴"
        rank = verb_ranks.get(verb, "?")
        print(f"  {status} #{rank:2} {verb:12} {data['found']:2d}/{data['total']:2d} ({data['coverage']:5.1f}%)")
    
    # Priority recommendations - focus on lowest coverage
    priority_verbs = sorted(verbs_needing_attention, key=lambda v: total_coverage[v]['coverage'])[:5]
    if priority_verbs:
        print(f"\n🚨 TOP 5 PRIORITY VERBS (lowest coverage):")
        for verb in priority_verbs:
            data = total_coverage[verb]
            rank = verb_ranks.get(verb, "?")
            print(f"   🔴 #{rank:2} {verb:12} - only {data['coverage']:4.1f}% coverage")

def main():
    print("🔍 French Conjugation Coverage Analyzer")
    print("="*50)
    
    # Use dynamic verb selection to get verbs needing attention
    verbs_needing_attention = get_verbs_needing_attention(25)
    
    if not verbs_needing_attention:
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
    
    # Analyze conjugation coverage for the dynamically selected verbs
    analyze_verb_conjugation_coverage(verbs_needing_attention, question_text)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 
