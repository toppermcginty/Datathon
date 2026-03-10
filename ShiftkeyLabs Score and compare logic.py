import pandas as pd
import json
import sys
from pathlib import Path


class Patient:
    def __init__(self, **kwargs):
        self.image_filename = kwargs.get('image_filename')
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

    def calculate_score(self):
        score = 0

        if self.margin:
            margin = str(self.margin).lower()
            if 'circumscribed' in margin and 'not' not in margin:
                score += -20
            elif 'not circumscribed' in margin:
                score += 10

        if self.shape and self.shape != 'not applicable':
            shape = str(self.shape).lower()
            if 'irregular' in shape:
                score += 30
            elif 'round' in shape:
                score += 5
            elif 'oval' in shape:
                score += 5

        if self.echogenicity and self.echogenicity != 'not applicable':
            echogenicity = str(self.echogenicity).lower()
            echo_map = {
                'isoechoic': -5,
                'heterogeneous': 5,
                'anechoic': -20,
                'hyperechoic': -5,
                'hypoechoic': 20,
                'complex': 15
            }
            for key, value in echo_map.items():
                if key in echogenicity:
                    score += value
                    break

        if self.symptoms and self.symptoms != 'not available':
            symptoms = str(self.symptoms).lower()
            if 'family history' in symptoms:
                score += 10
            if 'breast injury' in symptoms:
                score += -10
            if 'nipple discharge' in symptoms:
                score += 15

        if self.age and self.age != 'not available':
            try:
                age = float(self.age)
                if age < 40:
                    score += -5
                elif 40 <= age < 50:
                    score += 5
                elif age >= 50:
                    score += 15
            except Exception:
                pass

        if self.signs or self.skin_thickening:
            signs = str(self.signs).lower() if self.signs is not None else ""
            skin_thickening = str(self.skin_thickening).lower() if self.skin_thickening is not None else ""

            if 'yes' in skin_thickening:
                score += 20
            if 'warmth' in signs:
                score += 15
            if 'redness' in signs:
                score += 15
            if 'orange' in signs:
                score += 25
            if 'skin retraction' in signs:
                score += 20
            if 'nipple retraction' in signs:
                score += 25

        if self.posterior_features and self.posterior_features != 'not applicable':
            posterior_features = str(self.posterior_features).lower()
            posterior_map = {
                'shadowing': 5,
                'enhancement': -15,
                'combined': -5,
                'hypoechoic': 20,
                'complex': 15
            }
            for key, value in posterior_map.items():
                if key in posterior_features:
                    score += value
                    break

        if self.halo and self.halo != 'not applicable':
            halo = str(self.halo).lower()
            if 'yes' in halo:
                score += 25

        if self.classification and 'malignant' in str(self.classification).lower():
            score += 25

        self.score = score
        return self.score


def load_patients():
    patients = []
    df = pd.read_excel('BrEaST-Lesions-USG-clinical-data-Dec-15-2023.xlsx')

    for _, row in df.iterrows():
        if 'confirmed' in str(row['Verification']).lower():
            patient = Patient(
                image_filename=row.get('Image_filename'),
                pixel_size=row.get('Pixel_size'),
                age=row.get('Age'),
                tissue_composition=row.get('Tissue_composition'),
                signs=row.get('Signs'),
                symptoms=row.get('Symptoms'),
                shape=row.get('Shape'),
                margin=row.get('Margin'),
                echogenicity=row.get('Echogenicity'),
                posterior_features=row.get('Posterior_features'),
                halo=row.get('Halo'),
                calcifications=row.get('Calcifications'),
                skin_thickening=row.get('Skin_thickening'),
                interpretation=row.get('Interpretation'),
                BIRADS=row.get('BIRADS'),
                verification=row.get('Verification'),
                diagnosis=row.get('Diagnosis'),
                classification=row.get('Classification')
            )
            patients.append(patient)

    return patients


def calculate_form_score(form_data):
    score = 0

    margin = form_data.get('margin', '')
    if margin == 'circumscribed':
        score += -20
    elif margin == 'not circumscribed':
        score += 10

    shape = form_data.get('shape', '')
    if shape == 'irregular':
        score += 30
    elif shape in ['round', 'oval']:
        score += 5

    echogenicity = form_data.get('echogenicity', '')
    echo_map = {
        'isoechoic': -5,
        'heterogeneous': 5,
        'anechoic': -20,
        'hyperechoic': -5,
        'hypoechoic': 20,
        'complex': 15
    }
    score += echo_map.get(echogenicity, 0)

    try:
        age = float(form_data.get('age', ''))
        if age < 40:
            score += -5
        elif 40 <= age < 50:
            score += 5
        elif age >= 50:
            score += 15
    except Exception:
        pass

    symptoms = form_data.get('symptoms', [])
    if not isinstance(symptoms, list):
        symptoms = [symptoms]

    for symptom in symptoms:
        symptom = str(symptom).lower()
        if 'family history' in symptom:
            score += 10
        elif 'breast injury' in symptom:
            score += -10
        elif 'nipple discharge' in symptom:
            score += 15

    signs = form_data.get('signs', [])
    if not isinstance(signs, list):
        signs = [signs]

    for sign in signs:
        sign = str(sign).lower()
        if 'warmth' in sign:
            score += 15
        elif 'redness' in sign:
            score += 15
        elif 'orange' in sign:
            score += 25
        elif 'skin retraction' in sign:
            score += 20
        elif 'nipple retraction' in sign:
            score += 25

    if form_data.get('skin_thickening', '').lower() == 'yes':
        score += 20

    posterior_features = form_data.get('posterior_features', '')
    posterior_map = {
        'shadowing': 5,
        'enhancement': -15,
        'combined': -5,
        'hypoechoic': 20,
        'complex': 15
    }
    score += posterior_map.get(posterior_features, 0)

    if form_data.get('halo', '').lower() == 'yes':
        score += 25

    return score


def closest_patients(form_score, patients, n=3):
    ranked = []
    for patient in patients:
        diff = abs(patient.score - form_score)
        ranked.append((patient, diff))

    ranked.sort(key=lambda x: x[1])
    return [item[0] for item in ranked[:n]]


def format_patient_as_simple_dict(patient):
    symptoms_list = []
    if patient.symptoms and patient.symptoms not in ['not available', 'no', '']:
        if '&' in str(patient.symptoms):
            symptoms_list = [s.strip() for s in str(patient.symptoms).split('&')]
        else:
            symptoms_list = [str(patient.symptoms).strip()]

    signs_list = []
    if patient.signs and patient.signs not in ['not available', 'no', '']:
        if '&' in str(patient.signs):
            signs_list = [s.strip() for s in str(patient.signs).split('&')]
        else:
            signs_list = [str(patient.signs).strip()]

    return {
        'image_filename': patient.image_filename,
        'score': patient.score,
        'age': patient.age,
        'birads': patient.BIRADS,
        'diagnosis': patient.diagnosis,
        'classification': patient.classification,
        'margin': patient.margin if patient.margin and patient.margin != 'not applicable' else '',
        'shape': patient.shape if patient.shape and patient.shape != 'not applicable' else '',
        'echogenicity': patient.echogenicity if patient.echogenicity and patient.echogenicity != 'not applicable' else '',
        'symptoms': symptoms_list,
        'signs': signs_list,
        'skin_thickening': patient.skin_thickening if patient.skin_thickening and patient.skin_thickening != 'not applicable' else '',
        'posterior_features': patient.posterior_features if patient.posterior_features and patient.posterior_features != 'not applicable' else '',
        'halo': patient.halo if patient.halo and patient.halo != 'not applicable' else ''
    }


def ai_compare(ai_json_path, top_patients):
    ai_path = Path(ai_json_path)
    if not ai_path.exists():
        return {
            "ai_classification": "",
            "comparisons": [],
            "best_match": None,
            "matches_exist": False
        }

    with open(ai_path, 'r', encoding='utf-8') as f:
        ai_data = json.load(f)

    ai_classification = str(
        ai_data.get('classification', ai_data.get('class', ai_data.get('prediction', '')))
    ).lower()

    comparison_results = []

    for i, patient in enumerate(top_patients, 1):
        patient_class = str(patient.classification or '').lower()
        matches = (
            ai_classification == patient_class or
            ai_classification in patient_class or
            patient_class in ai_classification
        )

        comparison_results.append({
            'rank': i,
            'patient': patient,
            'image_filename': patient.image_filename,
            'patient_classification': patient.classification,
            'ai_classification': ai_classification,
            'matches': matches,
            'score': patient.score
        })

    matches_exist = any(item['matches'] for item in comparison_results)
    matches_list = [item for item in comparison_results if item['matches']]
    non_matches_list = [item for item in comparison_results if not item['matches']]

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


def main():
    patients = load_patients()
    if not patients:
        print(json.dumps({"error": "No patients loaded from database"}))
        sys.exit(1)

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

    form_score = calculate_form_score(form_data)
    top_3_patients = closest_patients(form_score, patients, n=3)

    ai_json_path = form_data.get('ai_json_path', 'ai_output.json')
    ai_results = ai_compare(ai_json_path, top_3_patients)

    ranked_matches = []
    if ai_results.get('comparisons'):
        for comp in ai_results['comparisons']:
            patient = comp['patient']
            item = format_patient_as_simple_dict(patient)
            item['rank'] = comp['new_rank']
            item['ai_match'] = comp['matches']
            ranked_matches.append(item)
    else:
        for idx, patient in enumerate(top_3_patients, 1):
            item = format_patient_as_simple_dict(patient)
            item['rank'] = idx
            item['ai_match'] = False
            ranked_matches.append(item)

    output = {
        "form_score": form_score,
        "ai_classification": ai_results.get("ai_classification", ""),
        "matches_exist": ai_results.get("matches_exist", False),
        "top_matches": ranked_matches
    }

    with open("match_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(json.dumps({"message": "Results written to match_results.json"}))


if __name__ == "__main__":
    main()
