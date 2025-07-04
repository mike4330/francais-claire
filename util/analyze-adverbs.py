#!/usr/bin/env python3
"""
French Adverb Coverage Analyzer
Analyzes coverage of top frequent adverbs in the question bank
Uses compiled question files (q-compiled-*.json) for most accurate analysis
"""

import json
import csv
import re
import os
from collections import defaultdict, Counter

# Configuration: Filtering threshold for adverbs needing attention
# Only show adverbs with usage percentage below this threshold
ATTENTION_THRESHOLD = 0.005  # 0.01% of all words

def load_adverbs_from_csv(limit=50, question_text=None):
    """Load top frequent adverbs from CSV file and show question bank usage
    
    Note: CSV was generated using:
    select *,(freqfilms2+freqlivres)/2 as overall from lemme
    where cgram = 'ADV'
    order by overall desc
    limit 3000
    """
    # Determine path based on current directory
    if os.path.exists("res/adverbs.csv"):
        adv_file = "res/adverbs.csv"
    else:
        adv_file = "../res/adverbs.csv"
    
    if not os.path.exists(adv_file):
        print(f"❌ Adverbs file not found at {adv_file}")
        return {}
    
    adverbs_data = []
    
    try:
        with open(adv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lemme = row['lemme']
                overall_freq = float(row['overall_freq']) if row['overall_freq'] else 0
                
                adverbs_data.append({
                    'lemme': lemme,
                    'freq': overall_freq
                })
    
    except Exception as e:
        print(f"❌ Error loading adverbs: {e}")
        return {}
    
    # Sort by frequency 
    adverbs_data.sort(key=lambda x: x['freq'], reverse=True)
    
    # Return top N adverbs for other analysis functions
    result = {}
    for i, adv_data in enumerate(adverbs_data[:limit]):
        result[adv_data['lemme']] = {
            'freq': adv_data['freq'],
            'rank': i + 1
        }
    
    # If question text provided, calculate usage in question bank
    word_counts = Counter()
    total_word_instances = 0
    if question_text:
        words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç\'-]+\b', question_text)
        word_counts = Counter(words)
        total_word_instances = sum(word_counts.values())
        
    target_count = 30  # Always try to find 30 adverbs needing attention
    print(f"🎯 TOP {target_count} HIGH-FREQUENCY ADVERBS NEEDING ATTENTION:")
    if total_word_instances > 0:
        print(f"     (Scanning through CSV to find {target_count} adverbs with weight < {ATTENTION_THRESHOLD}% - based on {total_word_instances:,} total word instances)")
    print(f"     {'Adverb':15}   {'Corpus':>8}   {'%':>7}   Status")
    print(f"     {'-'*15}   {'-'*8}   {'-'*7}   ------")
    
    shown_count = 0
    corpus_rank = 0
    # Continue scanning until we find target_count adverbs that need attention
    for adv_data in adverbs_data:
        corpus_rank += 1
        lemme = adv_data['lemme']
        corpus_freq = adv_data['freq']
        question_usage = word_counts.get(lemme, 0)
        
        # Calculate percentage weight (frequency / total instances)
        if total_word_instances > 0:
            percentage = (question_usage / total_word_instances) * 100
        else:
            percentage = 0.0
        
        # Only show adverbs with weight below threshold
        if percentage < ATTENTION_THRESHOLD:
            # Add usage indicator
            usage_indicator = "✅" if question_usage > 0 else "❌"
            
            print(f"{corpus_rank:3d}. {lemme:15} - {corpus_freq:7.1f}   {percentage:6.5f}   {usage_indicator}")
            shown_count += 1
            
            # Stop when we've found enough adverbs that need attention
            if shown_count >= target_count:
                break
    
    if shown_count == 0:
        print("     🎉 All adverbs are well-represented!")
    elif shown_count < target_count:
        print(f"     (Found only {shown_count} adverbs needing attention in entire corpus)")
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
    
    print("📁 Using compiled question files for adverb analysis...")
    
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
                            #print(f"   📈 Sources: {meta.get('originalQuestions', 0)} original + {meta.get('sourceQuestions', 0)} individual")
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

def analyze_adverb_coverage(top_adverbs, question_text):
    """Analyze coverage for each top adverb"""
    words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿñç\'-]+\b', question_text)
    word_counts = Counter(words)
    
    print(f"\n" + "="*80)
    print("📊 ADVERB COVERAGE ANALYSIS")
    print("="*80)
    
    total_coverage = {}
    
    for i, (lemme, adv_data) in enumerate(top_adverbs.items(), 1):
        print(f"\n🔍 {i:2d}. {lemme.upper()} (Rank #{adv_data['rank']})")
        print("-" * 50)
        
        corpus_freq = adv_data['freq']
        question_usage = word_counts.get(lemme, 0)
        
        # Calculate percentage weight (frequency / total instances)
        total_word_instances = sum(word_counts.values())
        if total_word_instances > 0:
            percentage = (question_usage / total_word_instances) * 100
        else:
            percentage = 0.0
        
        # Coverage assessment
        coverage_status = "✅ FOUND" if question_usage > 0 else "❌ MISSING"
        
        print(f"   📊 Corpus frequency: {corpus_freq:7.1f}")
        print(f"   📝 Question usage: {question_usage} times ({percentage:.4f}% of all words)")
        print(f"   {coverage_status}")
        
        total_coverage[lemme] = {
            'usage': question_usage,
            'percentage': percentage,
            'freq': corpus_freq,
            'rank': adv_data['rank']
        }
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 OVERALL ADVERB COVERAGE SUMMARY")
    print("="*80)
    
    found_count = sum(1 for data in total_coverage.values() if data['usage'] > 0)
    total_count = len(total_coverage)
    coverage_pct = found_count / total_count * 100 if total_count > 0 else 0
    
    print(f"Coverage: {found_count}/{total_count} adverbs found ({coverage_pct:.1f}%)")
    
    print(f"\n🎯 COVERAGE BY ADVERB:")
    for lemme, data in total_coverage.items():
        status = "🟢" if data['usage'] > 0 else "🔴"
        print(f"  {status} {lemme:15} - used {data['usage']:2d} times ({data['percentage']:5.3f}%) - freq: {data['freq']:7.1f}")
    
    # Priority recommendations
    missing_adverbs = [(l, d) for l, d in total_coverage.items() if d['usage'] == 0]
    if missing_adverbs:
        print(f"\n🚨 HIGH-FREQUENCY ADVERBS COMPLETELY MISSING:")
        for lemme, data in sorted(missing_adverbs, key=lambda x: x[1]['freq'], reverse=True)[:15]:
            print(f"   {lemme:15} - rank #{data['rank']:2d}, freq: {data['freq']:7.1f}")
    
    # Well-represented adverbs
    well_represented = [(l, d) for l, d in total_coverage.items() if d['usage'] > 0]
    if well_represented:
        print(f"\n✅ WELL-REPRESENTED ADVERBS:")
        for lemme, data in sorted(well_represented, key=lambda x: x[1]['usage'], reverse=True)[:10]:
            print(f"   {lemme:15} - used {data['usage']:2d} times, rank #{data['rank']:2d}, freq: {data['freq']:7.1f}")

def main():
    print("🔍 French Adverb Coverage Analyzer")
    print("="*50)
    
    # Load questions first
    questions = load_question_files()
    
    if not questions:
        print("❌ No questions found")
        return
    
    print(f"\n📊 Loaded {len(questions)} questions total")
    
    # Extract text
    question_text = extract_text_from_questions(questions)
    
    # Load top adverbs with question bank usage stats (will scan through to find 30 needing attention)
    top_adverbs = load_adverbs_from_csv(50, question_text)
    
    if not top_adverbs:
        print("❌ Cannot proceed without adverb data")
        return
    
    # Perform detailed coverage analysis
    analyze_adverb_coverage(top_adverbs, question_text)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
