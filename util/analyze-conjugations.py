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
    skipped_verbs = []
    
    # First pass: calculate coverage for all verbs to identify well-covered ones
    print(f"{Colors.YELLOW}🔍 Quick coverage assessment for filtering...{Colors.END}")
    
    for i, verb in enumerate(top_verbs, 1):
        # Get all conjugated forms
        conjugated_forms = get_all_conjugated_forms(verb)
        
        if not conjugated_forms:
            continue
        
        # Check which forms appear in questions
        found_forms = []
        
        # Include infinitive
        if verb in word_counts:
            found_forms.append((verb, "infinitive", word_counts[verb]))
        
        # Check conjugated forms
        for form, grammar, freq in conjugated_forms:
            if form in word_counts:
                found_forms.append((form, grammar, word_counts[form]))
        
        # Coverage statistics
        total_forms = len(conjugated_forms) + 1  # +1 for infinitive
        coverage_pct = len(found_forms) / total_forms * 100 if total_forms > 0 else 0
        
        total_coverage[verb] = {
            'found': len(found_forms),
            'total': total_forms,
            'coverage': coverage_pct
        }
        
        # Skip verbs with >65% coverage
        if coverage_pct > 65:
            skipped_verbs.append((verb, coverage_pct))
    
    # Filter out well-covered verbs and select exactly 25 that need attention
    verbs_needing_attention = [verb for verb in top_verbs if total_coverage.get(verb, {}).get('coverage', 0) <= 65]
    verbs_to_analyze = verbs_needing_attention[:25]  # Take first 25 that need attention
    
    print(f"\n{Colors.GREEN}✅ Skipping {len(skipped_verbs)} well-covered verbs (>65% coverage):{Colors.END}")
    for verb, coverage in skipped_verbs:
        rank = top_verbs.index(verb) + 1
        print(f"   🟢 #{rank:2d} {verb:12} - {coverage:5.1f}% coverage (well covered)")
    
    print(f"\n{Colors.CYAN}📋 Analyzing top 25 verbs needing attention (≤65% coverage):{Colors.END}")
    if len(verbs_needing_attention) > 25:
        print(f"{Colors.YELLOW}   (Selected first 25 from {len(verbs_needing_attention)} candidates needing attention){Colors.END}")
    
    # Second pass: detailed analysis for verbs needing attention
    for verb in verbs_to_analyze:
        rank = top_verbs.index(verb) + 1
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 {rank:2d}. {verb.upper()} (Rank #{rank}){Colors.END}")
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
        coverage_pct = total_coverage[verb]['coverage']
        print(f"   📈 Coverage: {total_coverage[verb]['found']}/{total_coverage[verb]['total']} forms ({coverage_pct:.1f}%)")
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 OVERALL CONJUGATION COVERAGE SUMMARY")
    print("="*80)
    
    # Calculate statistics for analyzed verbs only
    analyzed_coverage = sum(total_coverage[verb]['coverage'] for verb in verbs_to_analyze) / len(verbs_to_analyze)
    total_candidates = len(skipped_verbs) + len(verbs_needing_attention)
    
    print(f"Total verb candidates examined: {total_candidates}")
    print(f"Well-covered verbs (>65%): {len(skipped_verbs)} skipped")
    print(f"Verbs analyzed (≤65%): {len(verbs_to_analyze)} (top 25 needing attention)")
    print(f"Average coverage of analyzed verbs: {analyzed_coverage:.1f}%")
    
    print(f"\n🎯 TOP 25 VERBS NEEDING ATTENTION (≤65% coverage):")
    for verb in verbs_to_analyze:
        data = total_coverage[verb]
        status = "🟡" if data['coverage'] > 40 else "🟠" if data['coverage'] > 20 else "🔴"
        rank = top_verbs.index(verb) + 1
        print(f"  {status} #{rank:2d} {verb:12} {data['found']:2d}/{data['total']:2d} ({data['coverage']:5.1f}%)")
    
    if skipped_verbs:
        print(f"\n✅ WELL-COVERED VERBS SKIPPED (>65% coverage):")
        for verb, coverage in skipped_verbs:
            rank = top_verbs.index(verb) + 1
            data = total_coverage[verb]
            print(f"  🟢 #{rank:2d} {verb:12} {data['found']:2d}/{data['total']:2d} ({coverage:5.1f}%)")
    
    # Priority recommendations - focus on lowest coverage
    priority_verbs = sorted(verbs_to_analyze, key=lambda v: total_coverage[v]['coverage'])[:5]
    if priority_verbs:
        print(f"\n🚨 TOP 5 PRIORITY VERBS (lowest coverage):")
        for verb in priority_verbs:
            data = total_coverage[verb]
            rank = top_verbs.index(verb) + 1
            print(f"   🔴 #{rank:2d} {verb:12} - only {data['coverage']:4.1f}% coverage")

def main():
    print("🔍 French Conjugation Coverage Analyzer")
    print("="*50)
    
    # Get top 50 verbs (to ensure we have 25 after filtering)
    top_verbs = get_top_verbs(50)
    
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