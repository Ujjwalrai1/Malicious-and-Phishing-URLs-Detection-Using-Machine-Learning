# Malicious-and-Phishing-URLs-Detection-Using-Machine-Learning
This project focuses on detecting malicious and phishing URLs using advanced Machine Learning techniques and feature engineering. With the rapid growth of cyber threats, identifying harmful URLs is crucial to protect users from phishing attacks, malware distribution, and data breaches.
📌 Project Overview

With the rapid increase in cyber attacks, detecting malicious URLs has become critical. This project builds a classification model that predicts whether a URL is Safe (Benign) or Malicious (Phishing).

The system uses multiple feature extraction techniques:

🔤 Lexical Features – URL length, digits, special characters, HTTPS usage
🌐 Host-based Features – Domain age, WHOIS information (extendable)
📡 Network-based Features – IP reputation, DNS signals (extendable)
⚙️ Tech Stack
Python 🐍
Pandas & NumPy
Scikit-learn
Flask (for deployment)
Matplotlib / Seaborn (for visualization)
🤖 Machine Learning Models
Logistic Regression
Decision Tree
Random Forest ⭐ (Best Performing)
Support Vector Machine (SVM)
📊 Workflow
Data Collection (Phishing & Legitimate URLs)
Data Cleaning & Preprocessing
Feature Engineering
Model Training
Model Evaluation
Deployment (Flask Web App)
📁 Project Structure
malicious-url-detection/
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── notebooks/
│   ├── eda.ipynb
│   ├── model_experiments.ipynb
│
├── src/
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   ├── predict.py
│
├── models/
│   ├── trained_model.pkl
│
├── app/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│
├── requirements.txt
├── main.py
└── README.md
🚀 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/malicious-url-detection.git
cd malicious-url-detection
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Run the Model Training
python main.py
4️⃣ Run the Web App
cd app
python app.py
🌐 Usage
Enter a URL in the web interface
The system predicts whether the URL is:
✅ Safe
⚠️ Malicious
📈 Model Performance
Metric	Score
Accuracy	~95%
Precision	High
Recall	High
F1-Score	Balanced

(Note: Scores may vary depending on dataset)

🎯 Key Features
Real-time URL classification
Feature-based ML prediction
Modular and scalable code structure
Easy deployment with Flask
🔐 Use Cases
Cybersecurity systems
Browser phishing detection
Email spam filtering
Enterprise security tools
🚀 Future Improvements
🔥 Deep Learning (LSTM / RNN models)
🌍 Real-time API integration
🧩 Browser Extension
📡 Live threat intelligence integration
🤝 Contribution

Contributions are welcome!

Fork the repo
Create your feature branch
Commit your changes
Open a Pull Request
📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Ujjwal Rai
B.Tech Student | Machine Learning Enthusiast
