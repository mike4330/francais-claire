#!/usr/bin/env python3
"""
Unified French Lemma Coverage Analyzer
Analyzes coverage of adjectives, adverbs, verbs, and nouns in the question bank
Uses compiled question files (q-compiled-*.json) for most accurate analysis
Supports tag frequency analysis from analyze-questions.sh
"""

import json
import csv
import sqlite3
import re
import os
import sys
import argparse
from collections import defaultdict, Counter

# ============================================================================
# THRESHOLD CONFIGURATION - Adjust these values to tune analysis sensitivity
# ============================================================================
ATTENTION_THRESHOLD_ADVERBS = 0.0018
ATTENTION_THRESHOLD_ADJECTIVES = 0.001
ATTENTION_THRESHOLD_NOUNS = 0.0009
CONJUGATION_COVERAGE_FILTER = 20  # Skip verbs with coverage above this percentage
# ============================================================================

# Blacklist for conjugate forms that are used as nouns/other parts of speech in questions
# Format: {word: [list_of_question_ids_where_its_not_a_conjugate]}
CONJUGATE_BLACKLIST = {
    "crue": [
        602
    ],  # Used as noun "en crue" (in flood) in q602, not as past participle of "croire"
}

# Hardcoded hyphenated compound nouns for noun analysis only
HYPHENATED_COMPOUND_NOUNS = {
    "grand-père",
    "grand-mère",
    "grand-parents",
    "beau-père",
    "beau-frère",
    "belle-mère",
    "belle-sœur",
    "ex-mari",
    "ex-femme",
    "arrière-grand-père",
    "arrière-grand-mère",
    "demi-frère",
    "demi-sœur",
}

# Blacklist for nouns with limited pedagogical value
NOUN_BLACKLIST = {
    # Military ranks and titles
    "lieutenant",
    "colonel",
    "général",
    "commandant",
    "capitaine",
    "sergent",
    "maréchal",
    "amiral",
    "brigadier",
    # Vulgar slang
    "bordel",
    "putain",
    "merde",
    "connard",
    "salaud",
    "con",
    "pute",
    # Overly specialized/technical terms
    "métaphysique",
    "épistémologie",
    "ontologie",
    "herméneutique",
    # Archaic/literary terms
    "damoiseau",
    "jouvenceau",
    "occis",
    "gent",
    "iceux",
    # Religious/supernatural with limited modern use
    "diable",
    "démon",
    "ange",
    "archange",
    "séraphin",
    # Very informal slang for professions (prefer standard terms)
    "flic",
    "keuf",
    "toubib",
    "instit",
    # misc
    "anglais",
    "prince",
    "crime",
}

# Blacklist for literary/rare verb forms not suitable for everyday French learning
LITERARY_VERB_BLACKLIST = {
    # Passé simple forms (literary only)
    "mourut",
    "commença",
    "devint",
    "vint",
    "tint",
    "prit",
    "fit",
    "dit",
    "vit",
    "fut",
    "eut",
    "alla",
    "donna",
    "porta",
    "parla",
    "regarda",
    "trouva",
    "passa",
    "sentit",
    "sortit",
    "partit",
    "rentra",
    "arriva",
    "resta",
    "tomba",
    "leva",
    "tourna",
    "plut",
    "commença",
    "ouvrit",
    "offrit",
    "couvrit",
    "souffrit",
    "découvrit",
    # Rare/morbid conjugations
    "mourrait",
    "mourrais",
    "mourrons",
    "mourrez",
    "mortes",
    "morts",
    # Very literary conditional/subjunctive variants
    "sût",
    "eût",
    "fût",
    "dût",
    "pût",
    "vînt",
    "tînt",
    "prît",
    "fît",
    "dît",
    "vît",
    # Very rare conditionals and low-frequency forms (< 1.0 freq)
    "plairais",
    "plairas",
    "plairont",
    "plaisais",
    # Archaic or very formal forms
    "messied",
    "messiéront",
    "gît",
    "gisent",
    "gisant",
}


# ANSI Color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    # Status indicators with colors
    SUCCESS = f"{GREEN}[OK]{END}"
    FAIL = f"{RED}[MISS]{END}"
    WARNING = f"{YELLOW}[WARN]{END}"


def determine_paths():
    """Determine correct paths for database and question files"""
    paths = {
        "questions": None,
        "adj_csv": None,
        "adv_csv": None,
        "nouns_csv": None,
        "lexique_db": None,
    }

    # Question files
    if os.path.exists("questions/q-compiled-a.json"):
        paths["questions"] = "questions/"
    elif os.path.exists("../questions/q-compiled-a.json"):
        paths["questions"] = "../questions/"
    else:
        paths["questions"] = "questions/"

    # CSV files
    if os.path.exists("res/adj.csv"):
        csv_prefix = "res/"
    else:
        csv_prefix = "../res/"

    paths["adj_csv"] = csv_prefix + "adj.csv"
    paths["adv_csv"] = csv_prefix + "adverbs.csv"
    paths["nouns_csv"] = csv_prefix + "nouns.csv"

    # Lexique database
    if os.path.exists("database/lexique-experiments/lexique.sqlite3"):
        paths["lexique_db"] = "database/lexique-experiments/lexique.sqlite3"
    else:
        paths["lexique_db"] = "../database/lexique-experiments/lexique.sqlite3"

    return paths


def load_question_files(paths):
    """Load and combine all compiled question files"""
    question_files = [
        f"{paths['questions']}q-compiled-a.json",
        f"{paths['questions']}q-compiled-b.json",
        f"{paths['questions']}q-compiled-c.json",
    ]

    all_questions = []
    loaded_files = 0

    for filename in question_files:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "questions" in data:
                        questions = data["questions"]
                    elif isinstance(data, list):
                        questions = data
                    else:
                        continue

                    all_questions.extend(questions)
                    loaded_files += 1
            except Exception as e:
                continue

    if loaded_files > 0:
        print(
            f"{Colors.SUCCESS} Loaded {len(all_questions)} questions from {loaded_files} files"
        )
    else:
        print(f"{Colors.FAIL} Failed to load question files")

    return all_questions


def extract_text_from_questions(questions, respect_blacklist=False):
    """Extract all text content from questions, optionally respecting conjugate blacklist"""
    all_text = ""

    for q in questions:
        question_id = q.get("id", 0)

        # Collect text from all fields
        text_parts = []
        if "audioText" in q:
            text_parts.append(q["audioText"])
        if "question" in q:
            text_parts.append(q["question"])
        if "options" in q:
            for option in q["options"]:
                text_parts.append(option)
        if "explanation" in q:
            text_parts.append(q["explanation"])

        # Process text and apply blacklist if requested
        if respect_blacklist:
            for text_part in text_parts:
                words = re.findall(
                    r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ]+\b", text_part.lower()
                )
                filtered_words = []

                for word in words:
                    if not is_word_blacklisted(word, question_id):
                        filtered_words.append(word)
                    else:
                        print(
                            f"{Colors.WARNING} Blacklisted '{word}' in question {question_id} (not a conjugate)"
                        )

                all_text += " " + " ".join(filtered_words)
        else:
            # Simple text extraction for non-verb analysis
            for text_part in text_parts:
                all_text += " " + text_part

    return all_text.lower()


def is_word_blacklisted(word, question_id):
    """Check if a word should be excluded from conjugate analysis for a specific question"""
    if word.lower() in CONJUGATE_BLACKLIST:
        blacklisted_questions = CONJUGATE_BLACKLIST[word.lower()]
        return question_id in blacklisted_questions
    return False


def connect_to_lexique(paths):
    """Connect to the Lexique database"""
    if not os.path.exists(paths["lexique_db"]):
        print(f"{Colors.FAIL} Lexique database not found at {paths['lexique_db']}")
        return None

    try:
        conn = sqlite3.connect(paths["lexique_db"])
        return conn
    except Exception as e:
        print(f"{Colors.FAIL} Error connecting to database: {e}")
        return None


def get_top_verbs(paths, limit=50):
    """Get the top N most frequent verbs"""
    conn = connect_to_lexique(paths)
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT lemme, freqfilms2 
            FROM verbe 
            WHERE freqfilms2 > 0 
            ORDER BY freqfilms2 DESC 
            LIMIT ?
        """,
            (limit,),
        )

        top_verbs = cursor.fetchall()
        conn.close()

        return [verb for verb, freq in top_verbs]

    except Exception as e:
        print(f"{Colors.FAIL} Error getting top verbs: {e}")
        if conn:
            conn.close()
        return []


def get_all_conjugated_forms(verb_infinitive, paths):
    """Get all conjugated forms of a verb from Lexique database"""
    conn = connect_to_lexique(paths)
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ortho, cgram, freqfilms2 
            FROM lexique 
            WHERE lemme = ? AND cgram LIKE '%VER%'
            ORDER BY freqfilms2 DESC
        """,
            (verb_infinitive,),
        )

        forms = cursor.fetchall()
        conn.close()

        return [
            (form, grammar, freq)
            for form, grammar, freq in forms
            if form != verb_infinitive
        ]

    except Exception as e:
        print(
            f"{Colors.FAIL} Error getting conjugated forms for {verb_infinitive}: {e}"
        )
        if conn:
            conn.close()
        return []


def get_verbs_needing_attention_for_lemma(paths, target_count=25):
    """Dynamically expand verb pool until we have enough verbs needing attention"""
    conn = connect_to_lexique(paths)
    if not conn:
        return []

    try:
        cursor = conn.cursor()

        # Get total verb count for limit calculations
        cursor.execute("SELECT COUNT(*) FROM verbe WHERE freqfilms2 > 0")
        total_verbs = cursor.fetchone()[0]

        print(
            f"{Colors.CYAN}🔄 Dynamic verb pool expansion (targeting {target_count} verbs needing attention)...{Colors.END}"
        )

        pool_size = 250  # Start with 250 verbs
        verbs_needing_attention = []

        # Load questions for coverage analysis (do this once)
        questions = load_question_files(paths)
        if not questions:
            print(f"{Colors.FAIL} Cannot load questions for coverage analysis")
            return []

        question_text = extract_text_from_questions(questions, respect_blacklist=True)
        words = re.findall(r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ]+\b", question_text)
        word_counts = Counter(words)

        while len(verbs_needing_attention) < target_count and pool_size <= total_verbs:
            # Get current pool of verbs
            cursor.execute(
                """
                SELECT lemme, freqfilms2 
                FROM verbe 
                WHERE freqfilms2 > 0 
                ORDER BY freqfilms2 DESC 
                LIMIT ?
            """,
                (pool_size,),
            )

            top_verbs = cursor.fetchall()

            # Quick coverage check for all verbs in current pool
            print(
                f"{Colors.YELLOW}📊 Checking coverage for top {pool_size} verbs...{Colors.END}"
            )

            # Reset the list for this iteration
            verbs_needing_attention = []

            for verb, freq in top_verbs:
                # Quick coverage calculation
                conjugated_forms = get_all_conjugated_forms(verb, paths)
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
                coverage_pct = (
                    len(found_forms) / total_forms * 100 if total_forms > 0 else 0
                )

                # Add to attention list if below threshold
                if coverage_pct <= CONJUGATION_COVERAGE_FILTER:
                    verbs_needing_attention.append(verb)

                    # Stop when we have enough
                    if len(verbs_needing_attention) >= target_count:
                        break

            # If we have enough verbs, we're done
            if len(verbs_needing_attention) >= target_count:
                print(
                    f"{Colors.SUCCESS} Found {len(verbs_needing_attention)} verbs needing attention from pool of {pool_size}"
                )
                break

            # Otherwise, expand the pool
            old_pool_size = pool_size
            pool_size += 50  # Expand by 50 each time
            print(
                f"{Colors.YELLOW}🔄 Only found {len(verbs_needing_attention)} verbs needing attention, expanding pool from {old_pool_size} to {pool_size}...{Colors.END}"
            )

        conn.close()

        if len(verbs_needing_attention) < target_count:
            print(
                f"{Colors.WARNING} Only found {len(verbs_needing_attention)} verbs needing attention (out of {total_verbs} total verbs)"
            )

        return verbs_needing_attention[:target_count]

    except Exception as e:
        print(f"{Colors.FAIL} Error in dynamic verb selection: {e}")
        if conn:
            conn.close()
        return []


def analyze_verb_conjugations(paths, question_text, limit=50):
    """Analyze verb conjugation coverage and return prioritized missing conjugates"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 VERB CONJUGATION ANALYSIS{Colors.END}")
    print("=" * 60)

    # Get verbs needing attention using dynamic pool expansion
    verbs_needing_attention = get_verbs_needing_attention_for_lemma(paths, 25)
    if not verbs_needing_attention:
        print(f"{Colors.FAIL} Cannot proceed without verb data")
        return []

    print(
        f"{Colors.CYAN}📊 Analyzing {len(verbs_needing_attention)} verbs needing attention for conjugation coverage...{Colors.END}"
    )

    # Extract words from question text (respecting blacklist)
    words = re.findall(r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ]+\b", question_text)
    word_counts = Counter(words)

    # Collect all missing conjugates with their frequencies
    all_missing_conjugates = []

    # Get verb ranks for display
    conn = connect_to_lexique(paths)
    verb_ranks = {}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT lemme, freqfilms2, 
                       ROW_NUMBER() OVER (ORDER BY freqfilms2 DESC) as rank
                FROM verbe 
                WHERE freqfilms2 > 0
            """
            )

            for verb, freq, rank in cursor.fetchall():
                verb_ranks[verb] = rank

        except Exception as e:
            print(f"{Colors.WARNING} Could not determine verb ranks: {e}")
        finally:
            conn.close()

    # Analyze each verb needing attention
    for verb in verbs_needing_attention:
        verb_rank = verb_ranks.get(verb, "?")

        # Get all conjugated forms
        conjugated_forms = get_all_conjugated_forms(verb, paths)

        if not conjugated_forms:
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

        # Add missing forms to the global list (filter out blacklisted forms)
        for form, grammar, freq in missing_forms:
            if form not in LITERARY_VERB_BLACKLIST:
                all_missing_conjugates.append((form, grammar, freq, verb, verb_rank))

    print(
        f"\n{Colors.CYAN}📋 Analyzing {len(verbs_needing_attention)} verbs needing attention (≤{CONJUGATION_COVERAGE_FILTER}% coverage){Colors.END}"
    )

    # Sort all missing conjugates by frequency (highest first)
    all_missing_conjugates.sort(key=lambda x: x[2], reverse=True)

    # Count filtered forms for debug output
    total_missing_before_filter = sum(
        len([f for f, g, freq in missing_forms])
        for verb in verbs_needing_attention
        for missing_forms in [[]]
    )
    filtered_count = len(
        [
            form
            for form in LITERARY_VERB_BLACKLIST
            if any(
                form in [f for f, g, freq, v, r in all_missing_conjugates]
                for f, g, freq, v, r in all_missing_conjugates
            )
        ]
    )
    if len(LITERARY_VERB_BLACKLIST) > 0:
        print(
            f"{Colors.CYAN}🚫 Filtered out {len(LITERARY_VERB_BLACKLIST)} literary/rare forms from analysis{Colors.END}"
        )

    # Display prioritized missing conjugates
    print(
        f"\n{Colors.BOLD}{Colors.MAGENTA}🎯 PRIORITIZED MISSING CONJUGATES:{Colors.END}"
    )
    print(f"{Colors.CYAN}   (Sorted by Lexique frequency){Colors.END}")
    print("   " + "-" * 50)

    missing_for_llm = []
    for i, (form, grammar, freq, verb, verb_rank) in enumerate(
        all_missing_conjugates[:30], 1
    ):
        # Calculate percentage for this specific conjugate
        conjugate_usage = word_counts.get(form, 0)
        total_word_instances = sum(word_counts.values())
        percentage = (
            (conjugate_usage / total_word_instances) * 100
            if total_word_instances > 0
            else 0.0
        )

        print(
            f"   {i:2d}. {form:15} - freq: {freq:6.1f} ({percentage:5.3f}%) ({verb}, {grammar})"
        )
        missing_for_llm.append(
            {
                "form": form,
                "verb": verb,
                "grammar": grammar,
                "frequency": freq,
                "percentage": percentage,
                "verb_rank": verb_rank,
            }
        )

    return missing_for_llm


def load_adverbs_from_csv(paths, limit=50, question_text=None):
    """Load top frequent adverbs from CSV file and return those needing attention"""
    adv_file = paths["adv_csv"]

    if not os.path.exists(adv_file):
        print(f"{Colors.FAIL} Adverbs file not found at {adv_file}")
        return []

    adverbs_data = []

    try:
        with open(adv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lemme = row["lemme"]
                overall_freq = float(row["overall_freq"]) if row["overall_freq"] else 0

                adverbs_data.append({"lemme": lemme, "freq": overall_freq})

    except Exception as e:
        print(f"{Colors.FAIL} Error loading adverbs: {e}")
        return []

    # Sort by frequency
    adverbs_data.sort(key=lambda x: x["freq"], reverse=True)

    # Calculate usage in question bank
    words = re.findall(r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ\'-]+\b", question_text)
    word_counts = Counter(words)

    # Special handling for compound adverbs like "à tâtons"
    # These are treated as single units in the corpus but appear as separate words in regex
    compound_adverbs = {
        "à tâtons": ["à", "tâtons"],
        "aux aguets": ["aux", "aguets"],
        "à l'improviste": ["à", "l", "improviste"],
        "ici-bas": ["ici", "bas"],
        "à jeun": ["à", "jeun"],
        "à grand-peine": ["à", "grand", "peine"],
        "outre-mer": ["outre", "mer"],
    }

    # Check for compound adverbs in the full text
    for compound, components in compound_adverbs.items():
        # Count occurrences of the full compound phrase
        compound_count = len(
            re.findall(
                r"\b" + re.escape(compound) + r"\b", question_text, re.IGNORECASE
            )
        )
        if compound_count > 0:
            word_counts[compound] = compound_count

    total_word_instances = sum(word_counts.values())

    # Find adverbs needing attention (below threshold)
    adverbs_needing_attention = []

    for i, adv_data in enumerate(adverbs_data):
        lemme = adv_data["lemme"]
        corpus_freq = adv_data["freq"]
        question_usage = word_counts.get(lemme, 0)

        # Calculate percentage weight
        if total_word_instances > 0:
            percentage = (question_usage / total_word_instances) * 100
        else:
            percentage = 0.0

        # Only include adverbs with weight below threshold
        if percentage < ATTENTION_THRESHOLD_ADVERBS:
            adverbs_needing_attention.append(
                {
                    "lemme": lemme,
                    "freq": corpus_freq,
                    "usage": question_usage,
                    "percentage": percentage,
                    "rank": i + 1,
                }
            )

            # Stop when we have enough
            if len(adverbs_needing_attention) >= limit:
                break

    return adverbs_needing_attention


def analyze_adverbs(paths, question_text, limit=50):
    """Analyze adverb coverage and return prioritized missing adverbs"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 ADVERB ANALYSIS{Colors.END}")
    print("=" * 60)

    # Load adverbs needing attention
    missing_adverbs = load_adverbs_from_csv(paths, limit, question_text)

    if not missing_adverbs:
        print(f"{Colors.FAIL} Cannot proceed without adverb data")
        return []

    print(
        f"{Colors.CYAN}📊 Analyzing adverbs needing attention (below {ATTENTION_THRESHOLD_ADVERBS}% threshold)...{Colors.END}"
    )

    # Display prioritized missing adverbs
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}🎯 PRIORITIZED MISSING ADVERBS:{Colors.END}")
    print(f"{Colors.CYAN}   (Sorted by Lexique frequency){Colors.END}")
    print("   " + "-" * 50)

    for i, adverb in enumerate(missing_adverbs[:30], 1):
        status = Colors.SUCCESS if adverb["usage"] > 0 else Colors.FAIL
        print(
            f"   {i:2d}. {adverb['lemme']:15} - freq: {adverb['freq']:6.1f} ({adverb['percentage']:6.4f}%) {status}"
        )

    return missing_adverbs


def load_adjectives_from_csv(paths, limit=50, questions=None):
    """Load top frequent adjectives from CSV file and return those needing attention.

    Uses the questions-containing-lemma approach instead of word percentage to avoid
    the expanding denominator problem. This method is more stable and pedagogically
    meaningful than traditional word frequency analysis.

    Traditional approach problems:
    - Denominator = total_words (grows ~25-50 words per question added)
    - Adding questions dilutes existing lemma percentages
    - Example: "normal" 3/50000 = 0.006% → 3/65000 = 0.005% (appears worse)

    Questions-containing-lemma approach benefits:
    - Denominator = total_questions (grows 1 per question added)
    - Much more stable coverage metrics
    - Pedagogically meaningful: "% of learning opportunities containing this word"
    - Example: "normal" in 5/200 = 2.5% → 5/300 = 1.67% (still meaningful)

    Args:
        paths: Dictionary containing file paths
        limit: Maximum number of adjectives to return
        questions: List of question objects to analyze

    Returns:
        List of adjective dictionaries with coverage data including:
        - lemme: The adjective lemma
        - freq: Corpus frequency from Lexique
        - questions_with_lemma: Number of questions containing this adjective
        - question_coverage: Percentage of questions containing this adjective
        - rank: Frequency rank in corpus
    """
    adj_file = paths["adj_csv"]

    if not os.path.exists(adj_file):
        print(f"{Colors.FAIL} Adjectives file not found at {adj_file}")
        return []

    adjectives_data = defaultdict(list)

    try:
        with open(adj_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lemme = row["lemme"]
                form = row["lemme"]  # The form is the same as lemme in this CSV
                genre = row["genre"]
                nombre = row["nombre"]
                overall_freq = float(row["overall_freq"]) if row["overall_freq"] else 0

                adjectives_data[lemme].append(
                    {
                        "form": form,
                        "genre": genre,
                        "nombre": nombre,
                        "freq": overall_freq,
                    }
                )

    except Exception as e:
        print(f"{Colors.FAIL} Error loading adjectives: {e}")
        return []

    # Get top adjectives by highest frequency form
    top_adjectives = {}
    for lemme, forms in adjectives_data.items():
        max_freq = max(form["freq"] for form in forms)
        top_adjectives[lemme] = {"max_freq": max_freq, "forms": forms}

    # Sort by max frequency
    sorted_adjectives = sorted(
        top_adjectives.items(), key=lambda x: x[1]["max_freq"], reverse=True
    )

    # Pre-extract text from all questions for efficient lookup (avoids O(adjectives × questions) complexity)
    total_questions = len(questions) if questions else 0
    question_word_sets = []

    if questions:
        for q in questions:
            question_text = ""
            # Extract text from all fields
            if "audioText" in q:
                question_text += " " + q["audioText"]
            if "question" in q:
                question_text += " " + q["question"]
            if "options" in q:
                for option in q["options"]:
                    question_text += " " + option
            if "explanation" in q:
                question_text += " " + q["explanation"]

            # Extract words and store as set for fast lookup
            words = re.findall(
                r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ]+\b", question_text.lower()
            )
            question_word_sets.append(set(words))

    # Find adjectives needing attention (below threshold)
    adjectives_needing_attention = []

    for i, (lemme, data) in enumerate(sorted_adjectives):
        corpus_freq = data["max_freq"]

        # Count questions containing this lemma (fast O(1) lookup per question)
        questions_with_lemma = 0
        if question_word_sets:
            for word_set in question_word_sets:
                if lemme.lower() in word_set:
                    questions_with_lemma += 1

        # Calculate question coverage percentage
        if total_questions > 0:
            question_coverage = (questions_with_lemma / total_questions) * 100
        else:
            question_coverage = 0.0

        # Only include adjectives with coverage below threshold
        # ATTENTION_THRESHOLD_ADJECTIVES is a fraction (e.g., 0.008), multiply by 100 to match percentage scale
        question_threshold = ATTENTION_THRESHOLD_ADJECTIVES * 100
        if question_coverage < question_threshold:
            adjectives_needing_attention.append(
                {
                    "lemme": lemme,
                    "freq": corpus_freq,
                    "questions_with_lemma": questions_with_lemma,
                    "question_coverage": question_coverage,
                    "rank": i + 1,
                }
            )

            # Stop when we have enough
            if len(adjectives_needing_attention) >= limit:
                break

    return adjectives_needing_attention


def analyze_adjectives(paths, questions, limit=50):
    """Analyze adjective coverage and return prioritized missing adjectives.

    This function implements the questions-containing-lemma methodology to solve
    the expanding denominator problem that affects traditional word frequency analysis.

    Methodology:
    - Counts how many questions contain each adjective (not word instances)
    - Calculates percentage based on total questions (not total words)
    - Uses ATTENTION_THRESHOLD_ADJECTIVES as question coverage threshold (configurable)
    - Provides both absolute counts and percentages for clarity

    Output format: "lemme - freq: X.X (N questions, P%) ✅/❌"
    This shows corpus frequency, absolute question count, and coverage percentage.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 ADJECTIVE ANALYSIS{Colors.END}")
    print("=" * 60)

    # Load adjectives needing attention
    missing_adjectives = load_adjectives_from_csv(paths, limit, questions)

    if not missing_adjectives:
        print(f"{Colors.FAIL} Cannot proceed without adjective data")
        return []

    print(
        f"{Colors.CYAN}📊 Analyzing adjectives needing attention (below {ATTENTION_THRESHOLD_ADJECTIVES * 100}% question coverage threshold)...{Colors.END}"
    )

    # Display prioritized missing adjectives
    print(
        f"\n{Colors.BOLD}{Colors.MAGENTA}🎯 PRIORITIZED MISSING ADJECTIVES:{Colors.END}"
    )
    print(
        f"{Colors.CYAN}   (Sorted by Lexique frequency, showing question coverage){Colors.END}"
    )
    print("   " + "-" * 65)

    for i, adjective in enumerate(missing_adjectives[:30], 1):
        status = (
            Colors.SUCCESS if adjective["questions_with_lemma"] > 0 else Colors.FAIL
        )
        print(
            f"   {i:2d}. {adjective['lemme']:15} - freq: {adjective['freq']:6.1f} ({adjective['questions_with_lemma']:2d} questions, {adjective['question_coverage']:6.4f}%) {status}"
        )

    return missing_adjectives


def load_nouns_from_csv(paths, limit=50, questions=None):
    """Load top frequent nouns from CSV file and return those needing attention.

    Uses the questions-containing-lemma approach instead of word percentage to avoid
    the expanding denominator problem. This method is more stable and pedagogically
    meaningful than traditional word frequency analysis.

    Traditional approach problems:
    - Denominator = total_words (grows ~25-50 words per question added)
    - Adding questions dilutes existing lemma percentages
    - Example: "main" 8/50000 = 0.016% → 8/65000 = 0.012% (appears worse)

    Questions-containing-lemma approach benefits:
    - Denominator = total_questions (grows 1 per question added)
    - Much more stable coverage metrics
    - Pedagogically meaningful: "% of learning opportunities containing this word"
    - Example: "main" in 5/200 = 2.5% → 5/300 = 1.67% (still meaningful)

    Args:
        paths: Dictionary containing file paths
        limit: Maximum number of nouns to return
        questions: List of question objects to analyze

    Returns:
        List of noun dictionaries with coverage data including:
        - lemme: The noun lemma
        - freq: Corpus frequency from Lexique
        - questions_with_lemma: Number of questions containing this noun
        - question_coverage: Percentage of questions containing this noun
        - rank: Frequency rank in corpus
    """
    nouns_file = paths["nouns_csv"]

    if not os.path.exists(nouns_file):
        print(f"{Colors.FAIL} Nouns file not found at {nouns_file}")
        return []

    nouns_data = []

    try:
        with open(nouns_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lemme = row["lemme"].strip('"')  # Remove quotes if present
                overall_freq = float(row["overall_freq"]) if row["overall_freq"] else 0

                # Skip blacklisted nouns with limited pedagogical value
                if lemme in NOUN_BLACKLIST:
                    continue

                nouns_data.append({"lemme": lemme, "freq": overall_freq})

    except Exception as e:
        print(f"{Colors.FAIL} Error loading nouns: {e}")
        return []

    # Add hyphenated compound nouns to the data if they're not already present
    for compound_noun in HYPHENATED_COMPOUND_NOUNS:
        # Check if already in data
        if not any(noun["lemme"] == compound_noun for noun in nouns_data):
            # Add with estimated frequency based on similar compound words
            estimated_freq = 50.0  # Conservative estimate for family relation terms
            nouns_data.append({"lemme": compound_noun, "freq": estimated_freq})

    # Sort by frequency
    nouns_data.sort(key=lambda x: x["freq"], reverse=True)

    # Pre-extract text from all questions for efficient lookup (avoids O(nouns × questions) complexity)
    total_questions = len(questions) if questions else 0
    question_word_sets = []

    if questions:
        for q in questions:
            question_text = ""
            # Extract text from all fields
            if "audioText" in q:
                question_text += " " + q["audioText"]
            if "question" in q:
                question_text += " " + q["question"]
            if "options" in q:
                for option in q["options"]:
                    question_text += " " + option
            if "explanation" in q:
                question_text += " " + q["explanation"]

            # Extract words and store as set for fast lookup
            words = re.findall(
                r"\b[a-záàâäéèêëíìîïóòôöúùûüýÿñçœ]+\b", question_text.lower()
            )

            # NOUN ANALYSIS ONLY: also check for hyphenated compound nouns
            question_text_lower = question_text.lower()
            for compound_noun in HYPHENATED_COMPOUND_NOUNS:
                if re.search(
                    r"\b" + re.escape(compound_noun) + r"\b", question_text_lower
                ):
                    words.append(compound_noun)

            question_word_sets.append(set(words))

    # Find nouns needing attention (below threshold)
    nouns_needing_attention = []

    for i, noun_data in enumerate(nouns_data):
        lemme = noun_data["lemme"]
        corpus_freq = noun_data["freq"]

        # Count questions containing this lemma (fast O(1) lookup per question)
        questions_with_lemma = 0
        if question_word_sets:
            for word_set in question_word_sets:
                if lemme.lower() in word_set:
                    questions_with_lemma += 1

        # Calculate question coverage percentage
        if total_questions > 0:
            question_coverage = (questions_with_lemma / total_questions) * 100
        else:
            question_coverage = 0.0

        # Only include nouns with coverage below threshold
        # ATTENTION_THRESHOLD_NOUNS is a fraction (e.g., 0.02), multiply by 100 to match percentage scale
        question_threshold = ATTENTION_THRESHOLD_NOUNS * 100
        if question_coverage < question_threshold:
            nouns_needing_attention.append(
                {
                    "lemme": lemme,
                    "freq": corpus_freq,
                    "questions_with_lemma": questions_with_lemma,
                    "question_coverage": question_coverage,
                    "rank": i + 1,
                }
            )

            # Stop when we have enough
            if len(nouns_needing_attention) >= limit:
                break

    return nouns_needing_attention


def analyze_nouns(paths, questions, limit=50):
    """Analyze noun coverage and return prioritized missing nouns.

    This function implements the questions-containing-lemma methodology to solve
    the expanding denominator problem that affects traditional word frequency analysis.

    Methodology:
    - Counts how many questions contain each noun (not word instances)
    - Calculates percentage based on total questions (not total words)
    - Uses ATTENTION_THRESHOLD_NOUNS as question coverage threshold (configurable)
    - Provides both absolute counts and percentages for clarity

    Output format: "lemme - freq: X.X (N questions, P%) ✅/❌"
    This shows corpus frequency, absolute question count, and coverage percentage.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 NOUN ANALYSIS{Colors.END}")
    print("=" * 60)

    # Load nouns needing attention
    missing_nouns = load_nouns_from_csv(paths, limit, questions)

    if not missing_nouns:
        print(f"{Colors.FAIL} Cannot proceed without noun data")
        return []

    print(
        f"{Colors.CYAN}📊 Analyzing nouns needing attention (below {ATTENTION_THRESHOLD_NOUNS * 100}% question coverage threshold)...{Colors.END}"
    )

    # Display prioritized missing nouns
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}🎯 PRIORITIZED MISSING NOUNS:{Colors.END}")
    print(
        f"{Colors.CYAN}   (Sorted by Lexique frequency, showing question coverage){Colors.END}"
    )
    print("   " + "-" * 65)

    for i, noun in enumerate(missing_nouns[:30], 1):
        status = Colors.SUCCESS if noun["questions_with_lemma"] > 0 else Colors.FAIL
        print(
            f"   {i:2d}. {noun['lemme']:15} - freq: {noun['freq']:6.1f} ({noun['questions_with_lemma']:2d} questions, {noun['question_coverage']:4.3f}%) {status}"
        )

    return missing_nouns


def analyze_tags(questions, limit=10):
    """Analyze tag usage and return top and bottom used tags"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 TAG ANALYSIS{Colors.END}")
    print("=" * 60)

    # Extract all tags from questions
    all_tags = []
    for q in questions:
        if "tags" in q and q["tags"]:
            all_tags.extend(q["tags"])

    if not all_tags:
        print(f"{Colors.FAIL} No tags found in questions")
        return []

    # Count tag frequency
    tag_counts = Counter(all_tags)
    total_question_count = len(questions)

    print(
        f"{Colors.CYAN}📊 Analyzing tag usage across {total_question_count} questions...{Colors.END}"
    )

    # Filter out tags with only 1 occurrence for bottom analysis
    filtered_tags = {tag: count for tag, count in tag_counts.items() if count > 1}

    # Get top used tags
    top_tags = tag_counts.most_common(limit)

    # Get bottom used tags (from filtered list)
    bottom_tags = sorted(filtered_tags.items(), key=lambda x: x[1])[:limit]

    # Display well-represented tags
    print(
        f"\n{Colors.BOLD}{Colors.MAGENTA}🎯 TOP {limit} WELL-REPRESENTED TOPICS:{Colors.END}"
    )
    print(f"{Colors.CYAN}   (Most frequently used content tags){Colors.END}")
    print("   " + "-" * 50)

    tag_data = []
    for i, (tag, count) in enumerate(top_tags, 1):
        percentage = (count / total_question_count) * 100
        print(f"   {i:2d}. {tag:20} - {count:3d} questions ({percentage:5.1f}%)")
        tag_data.append(
            {"tag": tag, "count": count, "percentage": percentage, "category": "top"}
        )

    # Display under-represented tags
    print(
        f"\n{Colors.BOLD}{Colors.YELLOW}🎯 BOTTOM {len(bottom_tags)} UNDER-REPRESENTED TOPICS:{Colors.END}"
    )
    print(f"{Colors.CYAN}   (Least used content tags with >1 occurrence){Colors.END}")
    print("   " + "-" * 50)

    for i, (tag, count) in enumerate(bottom_tags, 1):
        percentage = (count / total_question_count) * 100
        print(f"   {i:2d}. {tag:20} - {count:3d} questions ({percentage:5.1f}%)")
        tag_data.append(
            {"tag": tag, "count": count, "percentage": percentage, "category": "bottom"}
        )

    return tag_data


def analyze_question_stats(questions):
    """Analyze question types and difficulty level distribution"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 QUESTION STATISTICS{Colors.END}")
    print("=" * 60)

    # Analyze question types
    question_types = Counter()
    difficulty_levels = Counter()

    for q in questions:
        if "questionType" in q and q["questionType"]:
            question_types[q["questionType"]] += 1

        if "difficulty" in q and q["difficulty"]:
            difficulty_levels[q["difficulty"]] += 1

    total_questions = len(questions)

    # Display question types
    print(f"{Colors.CYAN}📊 Question Types:{Colors.END}")
    print("   " + "-" * 30)

    for question_type, count in question_types.most_common():
        percentage = (count / total_questions) * 100
        # Add description for each type
        if question_type == "comprehension":
            desc = "English comprehension"
        elif question_type == "listening":
            desc = "French listening"
        elif question_type == "fill-in-the-blank":
            desc = "Missing word completion"
        else:
            desc = "Other"

        print(
            f"   {question_type:15} - {count:3d} questions ({percentage:5.1f}%) - {desc}"
        )

    # Display difficulty levels (in CEFR order)
    print(f"\n{Colors.CYAN}📊 CEFR Difficulty Levels:{Colors.END}")
    print("   " + "-" * 30)

    # Define CEFR order and descriptions
    cefr_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    cefr_descriptions = {
        "A1": "Beginner",
        "A2": "Elementary",
        "B1": "Intermediate",
        "B2": "Upper-Intermediate",
        "C1": "Advanced",
        "C2": "Proficiency",
    }

    for level in cefr_order:
        count = difficulty_levels.get(level, 0)
        percentage = (count / total_questions) * 100 if total_questions > 0 else 0
        desc = cefr_descriptions.get(level, "Unknown")
        print(f"   {level:3} {desc:18} - {count:3d} questions ({percentage:5.1f}%)")

    # Show any levels not in standard CEFR
    other_levels = set(difficulty_levels.keys()) - set(cefr_order)
    for level in sorted(other_levels):
        count = difficulty_levels[level]
        percentage = (count / total_questions) * 100
        print(f"   {level:3} {'Other':18} - {count:3d} questions ({percentage:5.1f}%)")

    return {
        "question_types": dict(question_types),
        "difficulty_levels": dict(difficulty_levels),
        "total_questions": total_questions,
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified French Lemma Coverage Analyzer"
    )
    parser.add_argument(
        "--limit", type=int, default=50, help="Number of items to analyze (default: 50)"
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    args = parser.parse_args()

    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith("_"):
                setattr(Colors, attr, "")

    print(
        f"{Colors.BOLD}{Colors.CYAN}🔍 Unified French Lemma Coverage Analyzer{Colors.END}"
    )
    print("=" * 60)

    # Determine paths
    paths = determine_paths()

    # Load questions
    questions = load_question_files(paths)

    if not questions:
        print(f"{Colors.FAIL} No questions found")
        return 1

    # Extract text for word analysis (with blacklist only for verb analysis)
    question_text_with_blacklist = extract_text_from_questions(
        questions, respect_blacklist=True
    )
    question_text_simple = extract_text_from_questions(
        questions, respect_blacklist=False
    )

    # Run verb conjugation analysis
    missing_conjugates = analyze_verb_conjugations(
        paths, question_text_with_blacklist, args.limit
    )

    # Run adverb analysis
    missing_adverbs = analyze_adverbs(paths, question_text_simple, args.limit)

    # Run adjective analysis
    missing_adjectives = analyze_adjectives(paths, questions, args.limit)

    # Run noun analysis
    missing_nouns = analyze_nouns(paths, questions, args.limit)

    # Run tag analysis (uses original questions, not text)
    top_tags = analyze_tags(questions, 10)  # Fixed limit of 10 for tags

    # Run question statistics analysis
    question_stats = analyze_question_stats(questions)

    # Add verification analysis
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 VERIFICATION STATUS{Colors.END}")
    print("=" * 60)

    verified_count = 0
    total_count = len(questions)

    for q in questions:
        if "verified" in q and q["verified"]:
            verified_count += 1

    not_verified_count = total_count - verified_count
    verified_percentage = (verified_count / total_count) * 100 if total_count > 0 else 0
    not_verified_percentage = (
        (not_verified_count / total_count) * 100 if total_count > 0 else 0
    )

    print(f"{Colors.CYAN}📊 Question Verification Status:{Colors.END}")
    print("   " + "-" * 40)
    print(
        f"   {Colors.GREEN}Verified:{Colors.END}     {verified_count:4d} questions ({verified_percentage:5.1f}%)"
    )
    print(
        f"   {Colors.RED}Not Verified:{Colors.END} {not_verified_count:4d} questions ({not_verified_percentage:5.1f}%)"
    )
    print(f"   {Colors.BOLD}Total:{Colors.END}        {total_count:4d} questions")

    print(f"\n{Colors.SUCCESS} Analysis complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
