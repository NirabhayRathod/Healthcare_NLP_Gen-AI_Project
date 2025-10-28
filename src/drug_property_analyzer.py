import pandas as pd
import sys , os
# Add the src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from logger import logging
from exception import CustomException

logging.info("data reading started for 'drug property analyzer'")
try:
    data = pd.read_csv(r'D:\HEALTHCARE_NLP_GEN-AI_PROJECT\data\final_drug_review_data.csv')
    logging.info("data reading completed for 'drug property analyzer'")
except Exception as e:
    raise CustomException(e ,sys)
 
medical_properties = {
    # Side Effects - EXPANDED
    'causes_drowsiness': [
        'drowsy', 'sleepy', 'tired', 'fatigue', 'fatigued', 'sedation', 'sedated', 
        'lethargic', 'lethargy', 'sleepiness', 'drowsiness', 'makes me sleep', 
        'can\'t stay awake', 'falling asleep', 'heavy eyes', 'exhausted', 'worn out',
        'need to nap', 'daytime sleepiness', 'hard to stay awake', 'zombie', 'zoned out'
    ],
    
    'causes_nausea': [
        'nausea', 'nauseous', 'sick to stomach', 'queasy', 'queasiness', 'vomiting', 
        'throw up', 'throwing up', 'puking', 'sick', 'feel sick', 'stomach sick',
        'upset stomach', 'sick feeling', 'gag', 'gagging', 'retch', 'dry heaves'
    ],
    
    'causes_headache': [
        'headache', 'migraine', 'head pain', 'head pounding', 'head hurts', 
        'head throbbing', 'head ache', 'head pressure', 'head splitting',
        'tension headache', 'cluster headache', 'head pain', 'head discomfort',
        'head sore', 'head pounding', 'head throbs'
    ],
    
    'causes_dizziness': [
        'dizzy', 'dizziness', 'lightheaded', 'light-headed', 'vertigo', 'woozy',
        'unsteady', 'off balance', 'balance problems', 'room spinning',
        'feel faint', 'faintness', 'dizzy spells', 'vertigo', 'spinning sensation'
    ],
    
    'causes_digestive_issues': [
        'stomach pain', 'stomach ache', 'abdominal pain', 'diarrhea', 'diarrhoea',
        'constipation', 'upset stomach', 'indigestion', 'heartburn', 'acid reflux',
        'bloating', 'bloated', 'gas', 'gassy', 'stomach cramps', 'cramping',
        'bowel problems', 'digestive issues', 'stomach issues', 'GI problems'
    ],
    
    # Effectiveness - EXPANDED
    'effective_pain_relief': [
        'pain relief', 'relieves pain', 'pain gone', 'helps pain', 'eases pain',
        'pain free', 'no pain', 'pain disappeared', 'pain reduced', 'pain better',
        'manages pain', 'controls pain', 'pain subsided', 'pain went away',
        'alleviates pain', 'reduces pain', 'pain diminishing', 'pain decreasing'
    ],
    
    'quick_acting': [
        'works fast', 'quick relief', 'within minutes', 'immediate', 'fast acting',
        'acts quickly', 'rapid relief', 'fast working', 'quick results', 'soon after',
        'minutes later', 'fast effect', 'quick acting', 'speedy relief', 'prompt relief',
        'almost instantly', 'right away', 'within half hour', '30 minutes'
    ],
    
    'long_lasting': [
        'lasts long', 'all day', '24 hour', 'extended relief', 'long lasting',
        'all night', 'through the night', 'lasts hours', 'long duration',
        'sustained relief', 'continuous relief', 'lasts all day', 'works all day',
        'extended release', 'time released', 'slow release', 'prolonged effect'
    ],
    
    'highly_effective': [
        'very effective', 'extremely effective', 'works great', 'excellent results',
        'amazing results', 'fantastic', 'wonderful', 'outstanding', 'superb',
        'highly effective', 'very good', 'excellent', 'great results', 'works perfectly',
        'does the job', 'exactly what I needed', 'perfect solution', 'best ever'
    ],
    
    # Practical Aspects - EXPANDED
    'easy_to_use': [
        'easy to take', 'convenient', 'simple', 'user friendly', 'easy to use',
        'easy administration', 'simple to take', 'no hassle', 'straightforward',
        'convenient dosing', 'easy dosage', 'simple instructions', 'user-friendly',
        'easy to swallow', 'easy to remember', 'convenient packaging'
    ],
    
    'cost_issues': [
        'expensive', 'costly', 'pricey', 'insurance won\'t cover', 'too expensive',
        'high cost', 'price is high', 'cost too much', 'expensive medication',
        'can\'t afford', 'pricey prescription', 'cost burden', 'financial strain',
        'insurance denied', 'co-pay high', 'out of pocket', 'not covered'
    ],
    
    'tolerable': [
        'well tolerated', 'gentle', 'no side effects', 'smooth', 'easy on stomach',
        'no problems', 'no issues', 'well tolerated', 'no adverse effects',
        'no reaction', 'handled well', 'no complications', 'smooth experience',
        'comfortable', 'no discomfort', 'easy transition'
    ],
    
    # Specific Conditions - EXPANDED
    'helps_sleep': [
        'helps sleep', 'sleep better', 'fall asleep', 'improved sleep', 'sleep well',
        'better sleep', 'sleep through night', 'restful sleep', 'deep sleep',
        'sleep quality', 'sleep improved', 'easier to sleep', 'sleep aid',
        'promotes sleep', 'induces sleep', 'sleep enhancement', 'sleep pattern',
        'no insomnia', 'sleep disturbance gone'
    ],
    
    'reduces_anxiety': [
        'calms anxiety', 'less anxious', 'reduces stress', 'relaxing', 'calming',
        'anxiety relief', 'panic attacks reduced', 'anxiousness gone', 'calm feeling',
        'reduces worry', 'less stressed', 'stress relief', 'anxiety better',
        'nervousness reduced', 'peaceful', 'serene', 'tranquil', 'at ease'
    ],
    
    'improves_mood': [
        'improves mood', 'feel better', 'happier', 'mood lift', 'better mood',
        'mood enhancement', 'depression better', 'less depressed', 'mood improved',
        'emotional balance', 'stable mood', 'mood elevation', 'positive mood',
        'outlook improved', 'happier feelings', 'emotional well-being'
    ],
    
    'increases_energy': [
        'more energy', 'energetic', 'less fatigued', 'pep', 'energy boost',
        'increased energy', 'less tired', 'vitality', 'energized', 'revitalized',
        'energy levels up', 'no fatigue', 'renewed energy', 'active again',
        'productivity improved', 'mental energy', 'physical energy'
    ]
}

def get_drug_property_percentages(drug_name):
    logging.info(' get_drug_property_percentages function called for getting percentage of drug property mainsion by people')
    # 1. Filter reviews for specific drug
    drug_reviews = data[data['drugName'] == drug_name]
    
    if len(drug_reviews) == 0:
        return f"No reviews found for {drug_name}"
    
    # 2. Calculate percentages for specific drug
    results = {}
    for property_name, keywords in medical_properties.items():
        pattern = '|'.join(keywords)
        matches = drug_reviews['review'].str.contains(pattern, case=False, na=False)
        percentage = (matches.sum() / len(drug_reviews)) * 100
        results[property_name] = round(percentage, 1)
    
    # 3. top conditions for this drug
    condition_counts = drug_reviews['condition'].value_counts()
    top_conditions = condition_counts.head(3)  # Top 3 conditions
    
    # 4. Format output
    output_lines = []
    
    # Add condition insights first
    output_lines.append(f" **Most Common Conditions for {drug_name}:**")
    for condition, count in top_conditions.items():
        percentage = (count / len(drug_reviews)) * 100
        output_lines.append(f"- {condition}: {count} reviews ({percentage:.1f}%)")
    
    output_lines.append("")
    
    # Add medical properties
    output_lines.append(" **Medical Properties Analysis:**")
    for prop, pct in results.items():
        readable_name = prop.replace('_', ' ').title()
        output_lines.append(f"- \"{pct}% of reviews mention {readable_name}\"")
    
    # Add overall stats
    output_lines.append("")
    output_lines.append(f" **Overall Stats:** {len(drug_reviews)} total reviews, Avg rating: {drug_reviews['rating'].mean():.1f}/10")
    
    return output_lines

# Example usage:
print("\n".join(get_drug_property_percentages("Integra")))