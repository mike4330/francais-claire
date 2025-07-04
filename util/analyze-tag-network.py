#!/usr/bin/env python3
"""
Tag Co-occurrence Network Analyzer
Extracts tag relationships from question files and generates network visualization data
"""

import json
import itertools
from collections import defaultdict, Counter
import os

def load_questions():
    """Load all questions from JSON files"""
    questions = []
    question_files = ['questions/q-compiled-a.json', 'questions/q-compiled-b.json', 'questions/q-compiled-c.json']
    
    for filename in question_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'questions' in data:
                        questions.extend(data['questions'])
                    print(f"✅ Loaded {len(data.get('questions', []))} questions from {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    return questions

def analyze_tag_cooccurrence(questions):
    """Analyze tag co-occurrence patterns"""
    # Count individual tags
    tag_counts = Counter()
    
    # Count tag pairs (co-occurrences)
    pair_counts = Counter()
    
    # Track which questions have each tag
    tag_questions = defaultdict(list)
    
    for i, q in enumerate(questions):
        if 'tags' not in q or not q['tags']:
            continue
            
        tags = q['tags']
        
        # Count individual tags
        for tag in tags:
            tag_counts[tag] += 1
            tag_questions[tag].append(i)
        
        # Count all pairs of tags in this question
        for tag1, tag2 in itertools.combinations(sorted(tags), 2):
            pair_counts[(tag1, tag2)] += 1
    
    return tag_counts, pair_counts, tag_questions

def generate_network_data(tag_counts, pair_counts, min_tag_freq=2, min_pair_freq=1):
    """Generate nodes and links for network visualization"""
    
    # Filter tags by frequency
    frequent_tags = {tag for tag, count in tag_counts.items() if count >= min_tag_freq}
    
    # Create nodes
    nodes = []
    for tag in frequent_tags:
        nodes.append({
            'id': tag,
            'size': tag_counts[tag],
            'group': categorize_tag(tag)
        })
    
    # Create links
    links = []
    for (tag1, tag2), count in pair_counts.items():
        if count >= min_pair_freq and tag1 in frequent_tags and tag2 in frequent_tags:
            links.append({
                'source': tag1,
                'target': tag2,
                'weight': count
            })
    
    return {'nodes': nodes, 'links': links}

def categorize_tag(tag):
    """Categorize tags for coloring with comprehensive pattern matching"""
    
    # Define categories with extensive keyword patterns
    categories = {
        'daily-life': [
            'daily-life', 'family', 'food', 'shopping', 'home', 'routine', 'household', 'morning', 'evening',
            'breakfast', 'lunch', 'dinner', 'cooking', 'kitchen', 'bedroom', 'living', 'bathroom', 'cleaning',
            'neighborhood', 'neighbors', 'pets', 'animals', 'garden', 'plants', 'furniture', 'appliances',
            'bread', 'meat', 'vegetables', 'fruits', 'drinks', 'coffee', 'tea', 'wine', 'restaurant',
            'cafe', 'grocery', 'supermarket', 'market', 'eating', 'meal', 'recipe', 'ingredient',
            'mother', 'father', 'parent', 'child', 'son', 'daughter', 'brother', 'sister', 'grandparent',
            'uncle', 'aunt', 'cousin', 'family-gathering', 'birthday', 'celebration', 'gifts', 'presents'
        ],
        
        'work-business': [
            'work', 'professional', 'business', 'career', 'office', 'job', 'employment', 'workplace',
            'meeting', 'presentation', 'project', 'deadline', 'manager', 'employee', 'colleague',
            'company', 'corporation', 'industry', 'finance', 'banking', 'accounting', 'marketing',
            'sales', 'customer', 'client', 'service', 'commerce', 'trade', 'economy', 'economic',
            'money', 'salary', 'budget', 'investment', 'profit', 'business-strategy', 'corporate',
            'entrepreneur', 'startup', 'competition', 'market', 'commercial', 'professional-development'
        ],
        
        'politics-government': [
            'politics', 'government', 'policy', 'elections', 'democracy', 'political', 'minister',
            'president', 'parliament', 'congress', 'senate', 'deputy', 'mayor', 'candidate',
            'voting', 'campaign', 'referendum', 'law', 'legislation', 'constitution', 'reform',
            'administration', 'bureaucracy', 'public', 'state', 'federal', 'local', 'municipal',
            'taxation', 'regulation', 'governance', 'diplomatic', 'foreign-policy', 'domestic-policy',
            'elysee', 'vatican', 'pope', 'censure', 'coalition', 'coup', 'debate', 'budget',
            'departments', 'dismissal', 'disagreement', 'leadership', 'legal-action', 'premier',
            'president', 'public-enterprise', 'public-figures', 'socialist-party', 'proposals',
            'parliament', 'crisis', 'scandal', 'political-statement', 'austerity', 'rule-of-law'
        ],
        
        'education-learning': [
            'education', 'school', 'learning', 'academic', 'university', 'student', 'teacher', 'professor',
            'class', 'classroom', 'course', 'lesson', 'lecture', 'exam', 'test', 'homework', 'assignment',
            'grade', 'degree', 'diploma', 'graduation', 'study', 'research', 'thesis', 'dissertation',
            'library', 'textbook', 'curriculum', 'pedagogy', 'knowledge', 'skill', 'training',
            'language-learning', 'french-class', 'language', 'linguistics', 'grammar', 'vocabulary'
        ],
        
        'health-medical': [
            'healthcare', 'medical', 'health', 'doctor', 'hospital', 'symptoms', 'illness', 'disease',
            'medicine', 'treatment', 'therapy', 'surgery', 'patient', 'nurse', 'physician', 'clinic',
            'pharmacy', 'medication', 'drug', 'prescription', 'diagnosis', 'recovery', 'wellness',
            'fitness', 'exercise', 'nutrition', 'diet', 'mental-health', 'psychology', 'stress',
            'pain', 'injury', 'accident', 'emergency', 'first-aid', 'preventive', 'rehabilitation'
        ],
        
        'leisure-entertainment': [
            'travel', 'vacation', 'sports', 'music', 'art', 'entertainment', 'leisure', 'hobby',
            'tourism', 'holiday', 'trip', 'journey', 'adventure', 'recreation', 'fun', 'relaxation',
            'game', 'play', 'cinema', 'film', 'movie', 'theater', 'concert', 'festival', 'event',
            'party', 'celebration', 'dancing', 'singing', 'reading', 'book', 'literature', 'novel',
            'museum', 'gallery', 'exhibition', 'culture', 'cultural', 'tradition', 'heritage',
            'football', 'tennis', 'basketball', 'swimming', 'running', 'cycling', 'hiking', 'camping',
            'games', 'guitar', 'music-theory', 'musicology', 'bach', 'stradivarius', 'violin',
            'harmonic-analysis', 'music-history', 'song', 'collecting', 'philately', 'stamps',
            'team-sports', 'fitness', 'gym', 'gardens', 'park', 'movies', 'festival', 'culinary-arts',
            'gastronomy', 'gourmet-cooking', 'romantic', 'romance', 'wedding', 'birthday'
        ],
        
        'technology-digital': [
            'technology', 'computer', 'digital', 'internet', 'software', 'artificial-intelligence',
            'online', 'website', 'app', 'mobile', 'smartphone', 'tablet', 'laptop', 'device',
            'programming', 'coding', 'data', 'algorithm', 'database', 'network', 'cyber',
            'virtual', 'electronic', 'automation', 'innovation', 'tech', 'IT', 'communication',
            'social-media', 'platform', 'digital-transformation', 'cybersecurity', 'cloud'
        ],
        
        'science-research': [
            'science', 'research', 'astronomy', 'space', 'laboratory', 'physics', 'chemistry',
            'biology', 'mathematics', 'scientific', 'experiment', 'theory', 'hypothesis',
            'discovery', 'innovation', 'technology', 'engineering', 'medicine', 'environment',
            'climate', 'ecology', 'nature', 'analysis', 'study', 'investigation', 'data',
            'statistics', 'methodology', 'academic-research', 'scholarly', 'space-exploration',
            'space-missions', 'biodiversity', 'clean-energy', 'algorithms', 'data-protection',
            'psychoanalysis', 'aesthetic-theory', 'literary-theory', 'poststructuralism',
            'postmodernism', 'postcolonialism', 'orientalism', 'intellectual-discourse',
            'evaluation', 'examination', 'archives', 'academic-freedom', 'academia'
        ],
        
        'transportation-travel': [
            'transportation', 'transport', 'travel', 'car', 'bus', 'train', 'plane', 'airplane',
            'metro', 'subway', 'bicycle', 'bike', 'walking', 'driving', 'traffic', 'road',
            'highway', 'street', 'station', 'airport', 'port', 'journey', 'trip', 'commute',
            'vehicle', 'motorcycle', 'taxi', 'uber', 'public-transport', 'private-transport'
        ],
        
        'social-relationships': [
            'friendship', 'friends', 'social', 'relationship', 'dating', 'romance', 'love',
            'marriage', 'wedding', 'couple', 'partner', 'spouse', 'community', 'society',
            'social-bonds', 'interpersonal', 'communication', 'conversation', 'meeting',
            'gathering', 'networking', 'collaboration', 'teamwork', 'cooperation',
            'helping-others', 'kindness', 'respect', 'shared-activities', 'sharing',
            'siblings', 'neighbors', 'social-movements', 'social-policy', 'social-business',
            'social-controversy', 'social-tensions', 'intergenerational'
        ],
        
        'emotions-psychology': [
            'emotions', 'feelings', 'happiness', 'sadness', 'anger', 'love', 'fear', 'joy',
            'depression', 'anxiety', 'stress', 'mood', 'emotional', 'psychology', 'mental',
            'behavior', 'personality', 'character', 'attitude', 'motivation', 'confidence',
            'self-esteem', 'empathy', 'compassion', 'kindness', 'patience', 'understanding'
        ],
        
        'geography-places': [
            'geography', 'location', 'place', 'city', 'town', 'village', 'country', 'region',
            'continent', 'mountain', 'river', 'ocean', 'sea', 'lake', 'forest', 'desert',
            'climate', 'weather', 'temperature', 'rain', 'snow', 'sun', 'wind', 'storm',
            'france', 'paris', 'europe', 'america', 'asia', 'africa', 'directions', 'map',
            'eure', 'marseille', 'normandy', 'provence', 'balkans', 'geneva', 'italy',
            'scandinavia', 'tokyo', 'myanmar', 'middle-east', 'moon', 'space', 'sky',
            'regions', 'street', 'highway', 'landscape', 'monuments', 'parks', 'desert'
        ],
        
        'time-calendar': [
            'time', 'calendar', 'schedule', 'appointment', 'date', 'day', 'week', 'month',
            'year', 'season', 'summer', 'winter', 'spring', 'autumn', 'morning', 'afternoon',
            'evening', 'night', 'today', 'tomorrow', 'yesterday', 'future', 'past', 'present',
            'deadline', 'duration', 'period', 'moment', 'instant', 'timing', 'punctuality',
            '19th-century', 'imperial-period', 'historic', 'napoleon', 'french-revolution',
            'millennium', 'near-future', 'past-activities', 'past-knowledge', 'weekend'
        ],
        
        'legal-crime': [
            'crime', 'criminal', 'legal', 'law', 'court', 'tribunal', 'prison', 'jail',
            'murder', 'fraud', 'theft', 'violence', 'accident', 'accidents', 'injuries',
            'emergency', 'legal-action', 'criminal-responsibility', 'investigation', 'scandal',
            'judicial', 'lawsuit', 'compliance', 'regulation', 'legal-system', 'justice'
        ],
        
        'culture-arts': [
            'culture', 'cultural', 'art', 'arts', 'heritage', 'tradition', 'traditions',
            'museum', 'gallery', 'exhibition', 'literature', 'authors', 'writers', 'poetry',
            'artisanal', 'traditional-crafts', 'cultural-analysis', 'cultural-hegemony',
            'french-heritage', 'french-values', 'spiritual-heritage', 'monuments',
            'historic-towns', 'beauty', 'contemplative', 'monasticism', 'beatification'
        ]
    }
    
    # Convert tag to lowercase for comparison
    tag_lower = tag.lower()
    
    # Check for exact matches and substring matches
    for category, keywords in categories.items():
        # Exact match
        if tag_lower in keywords:
            return category
        # Substring match (but avoid very short matches)
        for keyword in keywords:
            if len(keyword) > 3 and keyword in tag_lower:
                return category
            # Also check if tag contains keyword
            if len(tag_lower) > 3 and tag_lower in keyword:
                return category
    
    # Special handling for compound tags with hyphens
    if '-' in tag_lower:
        parts = tag_lower.split('-')
        for part in parts:
            if len(part) > 2:  # Avoid very short parts
                for category, keywords in categories.items():
                    if part in keywords:
                        return category
    
    return 'other'

def print_analysis(tag_counts, pair_counts, tag_questions):
    """Print human-readable analysis"""
    print("\n" + "="*60)
    print("🔍 TAG CO-OCCURRENCE NETWORK ANALYSIS")
    print("="*60)
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total unique tags: {len(tag_counts)}")
    print(f"   Total tag pairs: {len(pair_counts)}")
    print(f"   Questions analyzed: {len(set().union(*tag_questions.values()))}")
    
    print(f"\n🔥 TOP 15 MOST FREQUENT TAGS:")
    for tag, count in tag_counts.most_common(15):
        print(f"   {tag:25} {count:3d} questions")
    
    print(f"\n🔗 TOP 15 STRONGEST TAG CONNECTIONS:")
    for (tag1, tag2), count in pair_counts.most_common(15):
        print(f"   {tag1:20} ↔ {tag2:20} ({count:2d} connections)")
    
    print(f"\n🏝️  ISOLATED TAGS (appear in only 1 question):")
    isolated = [tag for tag, count in tag_counts.items() if count == 1]
    for i, tag in enumerate(sorted(isolated)):
        if i % 4 == 0:
            print(f"\n   ", end="")
        print(f"{tag:18}", end=" ")
    
    print(f"\n\n📈 CATEGORY DISTRIBUTION:")
    categories = defaultdict(int)
    for tag, count in tag_counts.items():
        cat = categorize_tag(tag)
        categories[cat] += count
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat:15} {count:3d} total occurrences")

def main():
    print("🏷️  Tag Co-occurrence Network Analyzer")
    print("=====================================")
    
    # Load questions
    questions = load_questions()
    if not questions:
        print("❌ No questions loaded!")
        return
    
    # Analyze tag patterns
    tag_counts, pair_counts, tag_questions = analyze_tag_cooccurrence(questions)
    
    # Print analysis
    print_analysis(tag_counts, pair_counts, tag_questions)
    
    # Generate network data
    network_data = generate_network_data(tag_counts, pair_counts)
    
    # Save network data
    output_file = 'util/tag-network-data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(network_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Network data saved to: {output_file}")
    print(f"   Nodes: {len(network_data['nodes'])}")
    print(f"   Links: {len(network_data['links'])}")
    print(f"\n🎯 Next: Run the HTML visualizer to see the network!")

if __name__ == "__main__":
    main()
