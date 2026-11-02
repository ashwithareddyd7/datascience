# Student Academic Risk Prediction (Data Science Internship Project)

Run in this order, inside this folder:

    pip install -r requirements.txt
    python generate_data.py       # creates data/student_data_raw.csv (simulated data)
    python train_models.py        # cleans, trains 3 models, saves charts + best model
    streamlit run dashboard.py    # opens the dashboard in the browser

Other files:
- diagrams.py      draws the architecture and UML diagrams used in the report
- render_views.py  renders the two dashboard views as images (for the report)
- outputs/         charts (figures/), model_results.csv, test_predictions.csv, run_log.json
