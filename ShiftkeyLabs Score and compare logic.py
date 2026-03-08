import pandas as pd
import json
import os
import sys
import io

class Patient:
    def __init__(self, **kwargs):
        self.pixel_size = kwargs.get('pixel_size')
        self.tissue_composition = kwargs.get('tissue_composition')
        self.age = kwargs.get('age')
        self.signs = kwargs.get('signs')
        self.symptoms = kwargs.get('symptoms')
        self.shape = kwargs.get('shape')
        self.margin = kwargs.get('margin')
        self.echogenicity = kwargs.get('echogenicity')
        self.posterior_features = kwargs.get('posterior_features')
        self.halo = kwargs.get('halo')
        self.calcifications = kwargs.get('calcifications')
        self.skin_thickening = kwargs.get('skin_thickening')
        self.interpretation = kwargs.get('interpretation')
        self.BIRADS = kwargs.get('BIRADS')
        self.verification = kwargs.get('verification')
        self.diagnosis = kwargs.get('diagnosis')
        self.classification = kwargs.get('classification')
        self.score = 0
        self.calculate_score()
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"Patient({self.signs}, {self.pixel_size}, {self.tissue_composition})"

    def calculate_score(self):        
        if self.margin:
            margin = str(self.margin)
            if 'circumscribed' in margin: self.score += -20
            elif 'not circumscribed' in margin: self.score += 10

        if self.shape and self.shape != 'not applicable':
            shape = str(self.shape)
            if 'irregular' in shape : self.score += 30
            if 'round' in shape : self.score += 5
            if 'oval' in shape : self.score += 5

        if self.echogenicity and self.echogenicity != 'not applicable':
            echogenicity = str(self.echogenicity)
            if 'isoechoic' in echogenicity : self.score += -5
            elif 'heterogeneous' in echogenicity : self.score += 5
            elif 'anechoic' in echogenicity : self.score += -20
            elif 'hyperechoic' in echogenicity : self.score += -5
            elif 'hypoechoic' in echogenicity : self.score += 20
            elif 'complex' in echogenicity : self.score += 15

        if self.symptoms and self.symptoms != 'not available':
            symptoms = str(self.symptoms)
            if 'no' in symptoms : self.score += 0
            elif 'family history' in symptoms : self.score += 10
            elif 'breast injury' in symptoms : self.score += -10
            elif 'nipple discharge' in symptoms : self.score += 15 # ASK AMYAH CAUSE ITS NOT LABLED AS BLOODY OR MILKY !!!!!!!!!!!!!!!!!!!!!
            

        if self.age and self.age != 'not available':
            age = float(self.age)
            if age < 40 : self.score += -5
            if age > 40 and age < 50 : self.score += 5
            if age > 50 : self.score += 15

        if self.signs or self.skin_thickening:
            signs = str(self.signs)
            skin_thickening = str(self.skin_thickening)
            if 'no' in skin_thickening : self.score += 0
            elif 'yes' in skin_thickening : self.score += 20
            if 'warmth' in signs : self.score += 15
            if 'redness' in signs : self.score += 15
            if 'orange' in signs : self.score += 25
            if 'skin retraction' in signs : self.score += 20
            if 'nipple retraction' in signs : self.score += 25

        #ASK AMAYH WHAT THE FUCK IS THE VALUES FOR THESE SCORES !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.posterior_features and self.posterior_features != 'not applicable':
            posterior_features = str(self.posterior_features)
            if 'no' in posterior_features : self.score += 0
            elif 'shadowing' in posterior_features : self.score += 5
            elif 'enhancement' in posterior_features : self.score += -15 # this one is good
            elif 'combined' in posterior_features : self.score += -5
            elif 'hypoechoic' in posterior_features : self.score += 20
            elif 'complex' in posterior_features : self.score += 15


        if self.halo and self.halo != 'not applicable':
            halo = str(self.halo)
            if 'yes' in halo : self.score += 25
            elif 'no' in halo : self.score += 0

        
        # comfermation score additive 25 points, USELESS delete, would like just mess up the averages!!!!!!!!!!!
        if self.classification:
            if 'malignant' in str(self.classification).lower():
                self.score += 25
        return self.score

def load_patients():
    patients = []

    df = pd.read_excel('BrEaST-Lesions-USG-clinical-data-Dec-15-2023.xlsx')

    for index, row in df.iterrows():
        if 'confirmed' in str(row['Verification']).lower():
            patient = Patient(
                image_filename = row['Image_filename'],
                pixel_size = row['Pixel_size'],
                age = row['Age'],
                tissue_composition = row['Tissue_composition'],
                signs = row['Signs'],
                symptoms = row['Symptoms'],
                shape = row['Shape'],
                margin = row['Margin'],
                echogenicity = row['Echogenicity'],
                posterior_features = row['Posterior_features'],
                halo = row['Halo'],
                calcifications = row['Calcifications'],
                skin_thickening = row['Skin_thickening'],
                interpretation = row['Interpretation'],
                BIRADS = row['BIRADS'],
                verification = row['Verification'],
                diagnosis = row['Diagnosis'],
                classification = row['Classification']
            )
            patients.append(patient)
    return patients


#FROM GABBY

def calculate_form_score(form_data):
    """
    Calculate score from HTML form submission
    form_data should be a dictionary with keys matching patient attributes
    """
    score = 0
    
    # Margin from form
    if 'margin' in form_data:
        if form_data['margin'] == 'circumscribed': score += -20
        elif form_data['margin'] == 'not_circumscribed': score += 10
    
    # Shape from form
    if 'shape' in form_data:
        if form_data['shape'] == 'irregular':
            score += 30
        elif form_data['shape'] in ['round', 'oval']:
            score += 5
    
    # Echogenicity from form
    if 'echogenicity' in form_data:
        echo_map = {
            'isoechoic': -5,
            'heterogeneous': 5,
            'anechoic': -20,
            'hyperechoic': -5,
            'hypoechoic': 20,
            'complex': 15
        }
        score += echo_map.get(form_data['echogenicity'], 0)
    
    # Age from form
    if 'age' in form_data:
        try:
            age = float(form_data['age'])
            if age < 40:
                score += -5
            elif 40 <= age < 50:
                score += 5
            elif age >= 50:
                score += 15
        except:
            pass
    
    # Symptoms from form (checkboxes/multiple selections)
    if 'symptoms' in form_data:
        symptoms = form_data['symptoms']
        if isinstance(symptoms, list):
            for symptom in symptoms:
                if symptom == 'family_history':
                    score += 10
                elif symptom == 'breast_injury':
                    score += -10
                elif symptom == 'nipple_discharge':
                    score += 15
        else:
            # Single symptom
            if symptoms == 'family_history':
                score += 10
            elif symptoms == 'breast_injury':
                score += -10
            elif symptoms == 'nipple_discharge':
                score += 15
    
    # Signs from form
    if 'signs' in form_data:
        signs = form_data['signs']
        if isinstance(signs, list):
            for sign in signs:
                if sign == 'warmth':
                    score += 15
                elif sign == 'redness':
                    score += 15
                elif sign == 'orange_peel':
                    score += 25
                elif sign == 'skin_retraction':
                    score += 20
                elif sign == 'nipple_retraction':
                    score += 25
        else:
            # Single sign
            if signs == 'warmth':
                score += 15
            elif signs == 'redness':
                score += 15
            elif signs == 'orange_peel':
                score += 25
            elif signs == 'skin_retraction':
                score += 20
            elif signs == 'nipple_retraction':
                score += 25
    
    # Skin thickening from form
    if 'skin_thickening' in form_data:
        if form_data['skin_thickening'] == 'yes':
            score += 20
    
    # Posterior features from form
    if 'posterior_features' in form_data:
        posterior_map = {
            'shadowing': 5,
            'enhancement': -15,
            'combined': -5,
            'hypoechoic': 20,
            'complex': 15
        }
        score += posterior_map.get(form_data['posterior_features'], 0)
    
    # Halo from form
    if 'halo' in form_data:
        if form_data['halo'] == 'yes':
            score += 25
    
    return score

    

def closest_patients(form_score, patients, n=3):
    patients_diff = []

    for patient in patients:
        diff = abs(patient.score - form_score)
        patients_diff.append((patient, diff))
    
    # NO CLUE IF THIS WORKS CORRECTLY
    patients_diff.sort(key=lambda x: x[1])
    

    #Best option, p[1], p[2] are second and third closest
    return [p[0] for p in patients_diff[:n]]




def format_patient_for_json(patient):
    #Format a patient object as JSON-serializable dictionary
    return {
        'image_filename': getattr(patient, 'image_filename', ''),
        'score': patient.score,
        'age': patient.age,
        'birads': patient.BIRADS,
        'diagnosis': patient.diagnosis,
        'classification': patient.classification,
        'margin': patient.margin,
        'shape': patient.shape,
        'echogenicity': patient.echogenicity,
        'symptoms': patient.symptoms,
        'signs': patient.signs,
        'posterior_features': patient.posterior_features,
        'halo': patient.halo,
        'skin_thickening': patient.skin_thickening
    }

#                                                                                          topper git bash here???
def ai_compare(ai_json_path, top_3_patients):
    with open(ai_json_path, 'r') as f:
        ai_data = json.load(f)

    ai_classification = ai_data.get('classification', ai_data.get('class', ai_data.get('prediction', ''))).lower()

    comparison_results = []

    for i, patient in enumerate(top_3_patients, 1):
            patient_class = patient.classification.lower() if patient.classification else ''
            
            # Check if classifications match
            matches = (ai_classification in patient_class or 
                      patient_class in ai_classification or
                      ai_classification == patient_class)
            
            comparison_results.append({
                'rank': i,
                'patient': patient,
                'image_filename': patient.image_filename,
                'patient_classification': patient.classification,
                'ai_classification': ai_classification,
                'matches': matches,
                'score': patient.score
            })

    matches_exist = any(r['matches'] for r in comparison_results)
    matches_list = [r for r in comparison_results if r['matches']]
    non_matches_list = [r for r in comparison_results if not r['matches']]
    matches_list.sort(key=lambda x: x['rank'])
    non_matches_list.sort(key=lambda x: x['rank'])

    sorted_results = matches_list + non_matches_list

    for new_rank, result in enumerate(sorted_results, 1):
        result['new_rank'] = new_rank
    
    best_match = sorted_results[0] if sorted_results else None

    return {
            'ai_classification': ai_classification,
            'comparisons': sorted_results,
            'best_match': best_match,
            'matches_exist': matches_exist
    }
        

def format_patient_as_simple_dict(patient):                                                       #ALL CHAT HOPEFULY IT WORKS!!!!!!!!!!!!!!!!!1
    """Format patient exactly like the input JSON example - simple key-value pairs"""
    # Handle symptoms - convert to list
    symptoms_list = []
    if patient.symptoms and patient.symptoms not in ['not available', 'no', '']:
        if '&' in patient.symptoms:
            symptoms_list = [s.strip() for s in patient.symptoms.split('&')]
        else:
            symptoms_list = [patient.symptoms]
    
    # Handle signs - convert to list
    signs_list = []
    if patient.signs and patient.signs not in ['not available', 'no', '']:
        if '&' in patient.signs:
            signs_list = [s.strip() for s in patient.signs.split('&')]
        else:
            signs_list = [patient.signs]
    
    return {
        'margin': patient.margin if patient.margin and patient.margin != 'not applicable' else '',
        'shape': patient.shape if patient.shape and patient.shape != 'not applicable' else '',
        'echogenicity': patient.echogenicity if patient.echogenicity and patient.echogenicity != 'not applicable' else '',
        'age': str(patient.age) if patient.age and patient.age != 'not available' else '',
        'symptoms': symptoms_list,
        'signs': signs_list,
        'skin_thickening': patient.skin_thickening if patient.skin_thickening and patient.skin_thickening != 'not applicable' else '',
        'posterior_features': patient.posterior_features if patient.posterior_features and patient.posterior_features != 'not applicable' else '',
        'halo': patient.halo if patient.halo and patient.halo != 'not applicable' else ''
    }

def main():
    patients = load_patients()
    if not patients:
        print(json.dumps({"error": "No patients loaded from database"}))
        sys.exit(1)

    # Read JSON from stdin                                 git bash for gabby
    try:
        json_input = sys.stdin.read()
        if not json_input:
            print(json.dumps({"error": "No JSON input provided"}))
            sys.exit(1)
    
        form_data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Error reading input: {str(e)}"}))
        sys.exit(1)

    # Calculate score from form data
    form_score = calculate_form_score(form_data)

    # Find top 3 closest patients
    top_3_patients = closest_patients(form_score, patients, n=3)
    

    ai_json_path = form_data.get('ai_json_path', 'ai_output.json')
    ai_results = ai_compare(ai_json_path, top_3_patients)


    simple_matches = []

    if ai_results and ai_results.get('comparisons'):
        # Use the AI-sorted order
        for comp in ai_results['comparisons']:
            patient = comp['patient']
            patient_dict = format_patient_as_simple_dict(patient)
            simple_matches.append(patient_dict)

    else:
        for patient in top_3_patients:
            patient_dict = format_patient_as_simple_dict(patient)
            simple_matches.append(patient_dict)

    # Print JSON result
    output_filename = "match_results.json"  # You can change this name
    with open(output_filename, 'w') as f:
        json.dump(simple_matches, f, indent=2)
    print(f"Results written to {output_filename}")  # Optional confirmation

if __name__ == "__main__":
    main()