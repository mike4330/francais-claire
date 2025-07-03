#!/usr/bin/env python3
"""
French Adjective Coverage Analyzer
Analyzes coverage of top frequent adjectives in ALL their forms (masculine, feminine, singular, plural)
Uses compiled question files (q-compiled-*.json) for most accurate analysis
"""

import json
import csv
import re
import os
from collections import defaultdict, Counter

def load_adjectives_from_csv(limit=50, question_text=None):
    """Load top frequent adjectives from CSV file and show question bank usage
    
    Note: CSV was generated using:
    select *,(freqfilms2+freqlivres)/2 as overall from lemme
    where cgram = 'ADJ'
    order by overall desc
    limit 3000
    """
    # Determine path based on current directory
    if os.path.exists("res/adj.csv"):
        adj_file = "res/adj.csv"
    else:
        adj_file = "../res/adj.csv"
    
    if not os.path.exists(adj_file):
        print(f"❌ Adjectives file not found at {adj_file}")
        return {}
    
    adjectives_data = defaultdict(list)
    
    try:
        with open(adj_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lemme = row['lemme']
                form = row['lemme']  # The form is the same as lemme in this CSV
                genre = row['genre']
                nombre = row['nombre']
                overall_freq = float(row['overall_freq']) if row['overall_freq'] else 0
                
                adjectives_data[lemme].append({
                    'form': form,
                    'genre': genre,
                    'nombre': nombre,
                    'freq': overall_freq
                })
    
    except Exception as e:
        print(f"❌ Error loading adjectives: {e}")
        return {}
    
    # Get top adjectives by highest frequency form
    top_adjectives = {}
    for lemme, forms in adjectives_data.items():
        max_freq = max(form['freq'] for form in forms)
        top_adjectives[lemme] = {
            'max_freq': max_freq,
            'forms': forms
        }
    
    # Sort by max frequency 
    sorted_adjectives = sorted(top_adjectives.items(), 
                              key=lambda x: x[1]['max_freq'], 
                              reverse=True)
    
    # Return top N adjectives for other analysis functions
    result = {}
    for i, (lemme, data) in enumerate(sorted_adjectives[:limit]):
        result[lemme] = data
    
    # If question text provided, calculate usage in question bank
    word_counts = Counter()
    total_word_instances = 0
    if question_text:
        words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
        word_counts = Counter(words)
        total_word_instances = sum(word_counts.values())
        
    target_count = 30  # Always try to find 30 adjectives needing attention
    print(f"🎯 TOP {target_count} HIGH-FREQUENCY ADJECTIVES NEEDING ATTENTION:")
    if total_word_instances > 0:
        print(f"     (Scanning through CSV to find {target_count} adjectives with weight < 0.01% - based on {total_word_instances:,} total word instances)")
    print(f"     {'Adjective':15}   {'Corpus':>8}   {'%':>7}   Status")
    print(f"     {'-'*15}   {'-'*8}   {'-'*7}   ------")
    
    shown_count = 0
    corpus_rank = 0
    # Continue scanning until we find target_count adjectives that need attention
    for lemme, data in sorted_adjectives:
        corpus_rank += 1
        corpus_freq = data['max_freq']
        question_usage = word_counts.get(lemme, 0)
        
        # Calculate percentage weight (frequency / total instances)
        if total_word_instances > 0:
            percentage = (question_usage / total_word_instances) * 100
        else:
            percentage = 0.0
        
        # Only show adjectives with weight < 0.01%
        if percentage < 0.01:
            # Add usage indicator
            usage_indicator = "✅" if question_usage > 0 else "❌"
            
            print(f"{corpus_rank:3d}. {lemme:15} - {corpus_freq:7.1f}   {percentage:6.3f}   {usage_indicator}")
            shown_count += 1
            
            # Stop when we've found enough adjectives that need attention
            if shown_count >= target_count:
                break
    
    if shown_count == 0:
        print("     🎉 All adjectives are well-represented!")
    elif shown_count < target_count:
        print(f"     (Found only {shown_count} adjectives needing attention in entire corpus)")
    print()
    
    return result

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
    
    print("📁 Using compiled question files for adjective analysis...")
    
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
                            print(f"✅ Loaded {len(questions)} questions from {filename}")
                            print(f"   📊 Compiled: {meta.get('compiledAt', 'unknown')}")
                            print(f"   📈 Sources: {meta.get('originalQuestions', 0)} original + {meta.get('sourceQuestions', 0)} individual")
                        else:
                            print(f"✅ Loaded {len(questions)} questions from {filename}")
                    elif isinstance(data, list):
                        questions = data
                        print(f"✅ Loaded {len(questions)} questions from {filename}")
                    else:
                        print(f"⚠️  Unexpected format in {filename}")
                        continue
                    
                    all_questions.extend(questions)
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
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

def analyze_adjective_coverage(top_adjectives, question_text):
    """Analyze coverage for each top adjective"""
    words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
    word_counts = Counter(words)
    
    print(f"\n" + "="*80)
    print("📊 ADJECTIVE COVERAGE ANALYSIS")
    print("="*80)
    
    total_coverage = {}
    
    for i, (lemme, adj_data) in enumerate(top_adjectives.items(), 1):
        print(f"\n🔍 {i:2d}. {lemme.upper()} (Rank #{i})")
        print("-" * 50)
        
        forms = adj_data['forms']
        
        if not forms:
            print(f"   ❌ No forms found for adjective")
            continue
        
        # Check which forms appear in questions
        found_forms = []
        missing_forms = []
        
        # Deduplicate forms by actual form text
        unique_forms = {}
        for form_data in forms:
            form_text = form_data['form']
            if form_text not in unique_forms or form_data['freq'] > unique_forms[form_text]['freq']:
                unique_forms[form_text] = form_data
        
        for form_text, form_data in unique_forms.items():
            if form_text in word_counts:
                found_forms.append((form_text, form_data['genre'], form_data['nombre'], 
                                  word_counts[form_text], form_data['freq']))
            else:
                missing_forms.append((form_text, form_data['genre'], form_data['nombre'], 
                                    form_data['freq']))
        
        # Sort found forms by frequency in our questions
        found_forms.sort(key=lambda x: x[3], reverse=True)
        
        # Sort missing forms by their corpus frequency
        missing_forms.sort(key=lambda x: x[3], reverse=True)
        
        # Report findings
        print(f"   ✅ FOUND FORMS: {len(found_forms)} forms found in questions")
        if found_forms:
            for form, genre, nombre, count, freq in found_forms[:5]:  # Top 5 found
                gender_str = f"{genre}{nombre}" if genre or nombre else "base"
                print(f"      {form:12} ({gender_str:4}) - used {count:2} times, freq: {freq:6.1f}")
            if len(found_forms) > 5:
                print(f"      ... and {len(found_forms) - 5} more found forms")
        
        print(f"   ❌ MISSING FORMS ({len(missing_forms)}) - Top by frequency:")
        for form, genre, nombre, freq in missing_forms[:8]:  # Top 8 missing
            gender_str = f"{genre}{nombre}" if genre or nombre else "base"
            print(f"      {form:12} ({gender_str:4}) - freq: {freq:6.1f}")
        
        if len(missing_forms) > 8:
            print(f"      ... and {len(missing_forms) - 8} more missing forms")
        
        # Coverage statistics
        total_forms = len(unique_forms)
        coverage_pct = len(found_forms) / total_forms * 100 if total_forms > 0 else 0
        
        total_coverage[lemme] = {
            'found': len(found_forms),
            'total': total_forms,
            'coverage': coverage_pct,
            'max_freq': adj_data['max_freq']
        }
        
        print(f"   📈 Coverage: {len(found_forms)}/{total_forms} forms ({coverage_pct:.1f}%)")
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 OVERALL ADJECTIVE COVERAGE SUMMARY")
    print("="*80)
    
    avg_coverage = sum(data['coverage'] for data in total_coverage.values()) / len(total_coverage)
    print(f"Average coverage across top {len(top_adjectives)} adjectives: {avg_coverage:.1f}%")
    
    print(f"\n🎯 COVERAGE BY ADJECTIVE:")
    for lemme, data in total_coverage.items():
        status = "🟢" if data['coverage'] > 50 else "🟡" if data['coverage'] > 20 else "🔴"
        print(f"  {status} {lemme:15} {data['found']:2d}/{data['total']:2d} ({data['coverage']:5.1f}%) - freq: {data['max_freq']:6.1f}")
    
    # Priority recommendations
    low_coverage = [(l, d) for l, d in total_coverage.items() if d['coverage'] < 30]
    if low_coverage:
        print(f"\n🚨 PRIORITY ADJECTIVES NEEDING MORE COVERAGE:")
        for lemme, data in sorted(low_coverage, key=lambda x: x[1]['max_freq'], reverse=True):
            print(f"   {lemme:15} - only {data['coverage']:4.1f}% coverage, freq: {data['max_freq']:6.1f}")
    
    # High frequency missing adjectives
    completely_missing = [(l, d) for l, d in total_coverage.items() if d['found'] == 0]
    if completely_missing:
        print(f"\n🚨 HIGH-FREQUENCY ADJECTIVES COMPLETELY MISSING:")
        for lemme, data in sorted(completely_missing, key=lambda x: x[1]['max_freq'], reverse=True)[:10]:
            print(f"   {lemme:15} - freq: {data['max_freq']:6.1f} (0% coverage)")

def main():
    print("🔍 French Adjective Coverage Analyzer")
    print("="*50)
    
    # Load questions first
    questions = load_question_files()
    
    if not questions:
        print("❌ No questions found")
        return
    
    print(f"\n📊 Loaded {len(questions)} questions total")
    
    # Extract text
    question_text = extract_text_from_questions(questions)
    
    # Load top adjectives with question bank usage stats (will scan through to find 30 needing attention)
    top_adjectives = load_adjectives_from_csv(150, question_text)
    
    if not top_adjectives:
        print("❌ Cannot proceed without adjective data")
        return
    
    # Skip detailed coverage analysis, but show priority missing adjectives
    # analyze_adjective_coverage(top_adjectives, question_text)
    
    # Show high priority missing adjectives
    words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç]+\b', question_text)
    word_counts = Counter(words)
    
    completely_missing = []
    for lemme, adj_data in top_adjectives.items():
        if lemme not in word_counts or word_counts[lemme] == 0:
            completely_missing.append((lemme, adj_data['max_freq']))
    
    if completely_missing:
        print(f"\n🚨 HIGH-FREQUENCY ADJECTIVES COMPLETELY MISSING:")
        for lemme, freq in sorted(completely_missing, key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {lemme:15} - freq: {freq:6.1f} (0% coverage)")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 