from flask import Flask, request, render_template, redirect, url_for, session, flash
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

# Load all three trained models
models = {}
model_info = {}

# Model file mapping - maps the actual pickle filenames to clean model keys
model_files = {
    'model_1_gradient_boosting_classifier': {
        'key': 'model_1_gradient_boosting_classifier',
        'file': r"pickle\model_1_gradient_boosting_classifier.pkl",
        'name': 'Gradient Boosting Classifier',
        'accuracy': 97.4,
        'description': 'Best overall performance'
    },
    'model_2_xgboost_classifier': {
        'key': 'model_2_xgboost_classifier',
        'file': r"pickle\model_2_xgboost_classifier.pkl",
        'name': 'XGBoost Classifier',
        'accuracy': 97.1,
        'description': 'Fast and efficient'
    },
    'model_3_multi-layer_perceptron': {
        'key': 'model_3_multi-layer_perceptron',
        'file': r"pickle\model_3_multi-layer_perceptron.pkl",
        'name': 'Multi-Layer Perceptron',
        'accuracy': 97.2,
        'description': 'Neural network based'
    }
}

# Load models
for model_id, info in model_files.items():
    try:
        with open(info['file'], "rb") as f:
            models[info['key']] = pickle.load(f)
            model_info[info['key']] = {
                'name': info['name'],
                'accuracy': info['accuracy'],
                'description': info['description']
            }
        print(f"✓ {info['name']} loaded successfully")
    except FileNotFoundError:
        print(f"✗ Warning: {info['name']} not found at {info['file']}")
    except Exception as e:
        print(f"✗ Error loading {info['name']}: {str(e)}")

print(f"\nTotal models loaded: {len(models)}")
print(f"Available model keys: {list(models.keys())}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple user storage (in production, use a proper database)
users = {
    'admin': 'admin',
    
}

# History storage
scan_history = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('upload_dataset'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_dataset():
    if request.method == "POST":
        # Check if file was uploaded
        if 'dataset' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['dataset']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read the dataset
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                # Store dataset info in session
                session['dataset_filename'] = filename
                session['dataset_shape'] = df.shape
                session['dataset_columns'] = list(df.columns)
                
                flash('Dataset uploaded successfully!', 'success')
                return redirect(url_for('view_dataset'))
            except Exception as e:
                flash(f'Error reading dataset: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload CSV or Excel files only.', 'error')
            return redirect(request.url)
    
    return render_template("upload.html")

@app.route("/dataset")
@login_required
def view_dataset():
    if 'dataset_filename' not in session:
        flash('No dataset uploaded yet', 'warning')
        return redirect(url_for('upload_dataset'))
    
    filename = session['dataset_filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Convert dataframe to HTML
        dataset_html = df.head(100).to_html(classes='dataset-table', index=False)
        
        return render_template("dataset.html", 
                             dataset_html=dataset_html,
                             filename=filename,
                             rows=df.shape[0],
                             columns=df.shape[1])
    except Exception as e:
        flash(f'Error loading dataset: {str(e)}', 'error')
        return redirect(url_for('upload_dataset'))

@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        url = request.form["url"]
        selected_model = request.form.get("model", list(models.keys())[0] if models else None)
        
        # Debug logging
        print(f"Selected model from form: {selected_model}")
        print(f"Available models: {list(models.keys())}")
        
        # Check if any models are loaded
        if not models:
            flash('No models are currently loaded. Please check your model files.', 'error')
            return render_template('index.html', 
                                 history=scan_history[:5], 
                                 models=model_info,
                                 available_models=list(models.keys()))
        
        # Validate selected model
        if selected_model not in models:
            flash(f'Selected model "{selected_model}" not available. Using default model.', 'warning')
            selected_model = list(models.keys())[0]
            print(f"Defaulting to: {selected_model}")
        
        try:
            # Extract features from URL
            obj = FeatureExtraction(url)
            x = np.array(obj.getFeaturesList()).reshape(1, 30)
            
            # Get the selected model
            model = models[selected_model]
            print(f"Using model: {selected_model}")
            
            # Make prediction
            y_pred = model.predict(x)[0]
            print(f"Prediction: {y_pred}")
            
            # Handle different prediction formats
            # XGBoost might return 0/1 instead of -1/1
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(x)[0]
                print(f"Probabilities: {y_proba}")
                
                # Check if we have 2 classes
                if len(y_proba) == 2:
                    # For models trained with -1/1 labels
                    if y_pred == -1:
                        y_pro_phishing = y_proba[0]
                        y_pro_non_phishing = y_proba[1]
                    else:
                        # For models like XGBoost with 0/1 labels
                        y_pro_phishing = y_proba[0]
                        y_pro_non_phishing = y_proba[1]
                else:
                    y_pro_phishing = 0.5
                    y_pro_non_phishing = 0.5
            else:
                # If model doesn't have predict_proba
                if y_pred in [-1, 0]:
                    y_pro_phishing = 0.9
                    y_pro_non_phishing = 0.1
                else:
                    y_pro_phishing = 0.1
                    y_pro_non_phishing = 0.9
            
            # Determine final result
            is_safe = y_pred == 1 or y_pred > 0
            
            # Store in history
            scan_result = {
                'url': url,
                'safe_percentage': round(y_pro_non_phishing * 100, 2),
                'unsafe_percentage': round(y_pro_phishing * 100, 2),
                'is_safe': is_safe,
                'model': model_info[selected_model]['name'],
                'model_key': selected_model,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'username': session['username']
            }
            scan_history.insert(0, scan_result)
            
            # Keep only last 50 scans
            if len(scan_history) > 50:
                scan_history.pop()
            
            print(f"Scan result: {scan_result}")
            
            return render_template('index.html', 
                                 result=scan_result,
                                 history=scan_history[:5],
                                 models=model_info,
                                 available_models=list(models.keys()),
                                 selected_model=selected_model)
        except Exception as e:
            flash(f'Error analyzing URL: {str(e)}', 'error')
            print(f"Error details: {e}")  # For debugging
            import traceback
            traceback.print_exc()  # Print full traceback
            return render_template('index.html', 
                                 history=scan_history[:5],
                                 models=model_info,
                                 available_models=list(models.keys()))
    
    # Default model selection for GET request
    default_model = list(models.keys())[0] if models else None
    
    return render_template("index.html", 
                         history=scan_history[:5],
                         models=model_info,
                         available_models=list(models.keys()),
                         selected_model=default_model)
    
@app.route("/performance")
@login_required
def performance():
    return render_template("performance.html", models=model_info)

@app.route("/graphs")
@login_required
def graphs():
    return render_template("graphs.html")

@app.route("/history")
@login_required
def history():
    user_history = [scan for scan in scan_history if scan['username'] == session['username']]
    return render_template("history.html", history=user_history)

@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    """Compare all three models on a single URL"""
    if request.method == "POST":
        url = request.form["url"]
        
        if not models:
            flash('No models are currently loaded.', 'error')
            return redirect(url_for('index'))
        
        try:
            # Extract features
            obj = FeatureExtraction(url)
            x = np.array(obj.getFeaturesList()).reshape(1, 30)
            
            # Get predictions from all models
            comparison_results = []
            for model_key, model in models.items():
                y_pred = model.predict(x)[0]
                
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(x)[0]
                    if len(y_proba) == 2:
                        y_pro_phishing = y_proba[0]
                        y_pro_non_phishing = y_proba[1]
                    else:
                        y_pro_phishing = 0.5
                        y_pro_non_phishing = 0.5
                else:
                    if y_pred in [-1, 0]:
                        y_pro_phishing = 0.9
                        y_pro_non_phishing = 0.1
                    else:
                        y_pro_phishing = 0.1
                        y_pro_non_phishing = 0.9
                
                comparison_results.append({
                    'model_name': model_info[model_key]['name'],
                    'safe_percentage': round(y_pro_non_phishing * 100, 2),
                    'unsafe_percentage': round(y_pro_phishing * 100, 2),
                    'is_safe': y_pred == 1 or y_pred > 0,
                    'accuracy': model_info[model_key]['accuracy']
                })
            
            return render_template('compare.html', 
                                 url=url,
                                 results=comparison_results)
        except Exception as e:
            flash(f'Error comparing models: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)