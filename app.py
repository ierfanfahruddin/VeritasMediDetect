from flask import Flask, request, jsonify
import pandas as pd
# import joblib # Uncomment this when you have a trained model

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model (example)
# try:
#     model = joblib.load('models/isolation_forest.joblib')
# except FileNotFoundError:
#     model = None
#     print("Warning: Model file not found. The /analyze endpoint will return dummy data.")

@app.route('/')
def index():
    return "Anomaly Detection Service is running."

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """
    Endpoint to receive data from the main application,
    analyze it for anomalies, and return the results.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if 'records' not in data or not isinstance(data['records'], list):
        return jsonify({"error": "JSON must contain a 'records' key with a list of data"}), 400

    # --- AI/ML Processing Happens Here ---
    # For now, we'll just implement a simple rule-based example.
    # In the future, this is where you would use the loaded 'model'.

    df = pd.DataFrame(data['records'])
    
    # --- Rule-Based Anomaly Detection ---
    
    # Create a dummy total_biaya for demonstration if not present
    if 'total_biaya' not in df.columns:
        df['total_biaya'] = df.filter(like='_qty').sum(axis=1) * 10000

    # --- Pre-computation for Peer Comparison ---
    # Calculate total doctor interactions (visites + konsuls) for each patient record
    action_cols = [col for col in df.columns if 'visite_' in col or 'konsul_' in col]
    df['total_doctor_interactions'] = df[action_cols].sum(axis=1)

    # Calculate the average interactions per location
    location_avg_interactions = df.groupby('lokasi_nm')['total_doctor_interactions'].mean().to_dict()

    def get_anomaly_reasons(row, avg_interactions_map):
        reasons = []
        # Rule 1: High Cost
        if row.get('total_biaya', 0) > 5000000:
            reasons.append('Biaya Sangat Tinggi')
        
        # Rule 2: Excessive EKG
        if row.get('ekg_qty', 0) > 5:
            reasons.append('Frekuensi EKG Tinggi (>5)')

        # Rule 3: Excessive USG
        if row.get('usg_qty', 0) > 5:
            reasons.append('Frekuensi USG Tinggi (>5)')
            
        # Rule 4: Unusually Long Stay
        if row.get('akomodasi_qty', 0) > 30:
            reasons.append('Lama Rawat Inap >30 Hari')
            
        # Rule 5: Missing Meal Charge for Inpatient
        if row.get('akomodasi_qty', 0) > 0 and row.get('makan_qty', 0) == 0:
            reasons.append('Pasien Rawat Inap Tanpa Biaya Makan')

        # Rule 6: High Doctor Interaction compared to peers in the same location
        lokasi = row.get('lokasi_nm')
        if lokasi and lokasi in avg_interactions_map:
            avg_for_loc = avg_interactions_map[lokasi]
            # Anomaly if interactions are > 2x the average AND above a minimum threshold of 5 to avoid noise
            if row['total_doctor_interactions'] > (avg_for_loc * 2) and row['total_doctor_interactions'] > 5:
                reasons.append(f"Interaksi Dokter Tinggi ({int(row['total_doctor_interactions'])} vs avg {avg_for_loc:.1f})")

        return '; '.join(reasons)

    df['anomaly_reason'] = df.apply(lambda row: get_anomaly_reasons(row, location_avg_interactions), axis=1)
    df['is_anomaly'] = df['anomaly_reason'] != ''

    # Convert DataFrame back to list of records
    results = df.to_dict('records')

    return jsonify({"analyzed_records": results})

if __name__ == '__main__':
    # Running on port 5000, accessible from other services on the same machine
    app.run(host='0.0.0.0', port=5000, debug=True)