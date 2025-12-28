import os
from flask import Flask, request, jsonify, render_template_string
import pandas as pd
from PyPDF2 import PdfReader

app = Flask(__name__)

# --- EMBEDDED WEBSITE CODE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoInternship - AI-Powered</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 100px 0; }
        .upload-section { padding: 50px 0; background-color: #f8fafc; }
    </style>
</head>
<body>
    <section class="hero-section">
        <div class="container">
            <h1 class="display-4 fw-bold">Automate Your Internship Applications</h1>
            <p class="lead">Upload your CV and company list below.</p>
        </div>
    </section>

    <section class="upload-section">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-body p-5">
                            <h2 class="text-center mb-4">Start Process</h2>
                            <form id="applicationForm">
                                <div class="mb-4">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" id="name" required>
                                </div>
                                <div class="mb-4">
                                    <label class="form-label">Upload CV (PDF)</label>
                                    <input type="file" class="form-control" id="cv" accept=".pdf" required>
                                </div>
                                <div class="mb-4">
                                    <label class="form-label">Company List (CSV)</label>
                                    <input type="file" class="form-control" id="companyList" accept=".csv" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Generate Applications</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
        document.getElementById('applicationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerText;
            submitBtn.innerText = "Processing...";
            submitBtn.disabled = true;

            const formData = new FormData();
            formData.append('name', document.getElementById('name').value);
            formData.append('cv', document.getElementById('cv').files[0]);
            formData.append('companyList', document.getElementById('companyList').files[0]);

            try {
                const response = await fetch('/generate', { method: 'POST', body: formData });
                const result = await response.json();

                if (result.status === 'success') {
                    alert(`Success! Generated ${result.count} cover letters. Check the browser Console to see them.`);
                    console.log("--- GENERATED LETTERS ---");
                    console.log(result.applications); 
                } else {
                    alert('Error: ' + (result.error || 'Unknown error occurred'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to connect to server.');
            } finally {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

def generate_ai_cover_letter(candidate_name, company_name, cv_text):
    return f"""
    Dear Hiring Manager at {company_name},
    
    My name is {candidate_name}. Based on my CV text: 
    "{cv_text[:50]}..." 
    I believe I am a great fit for your team.
    
    Sincerely, {candidate_name}
    """

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        name = request.form.get('name')
        cv_file = request.files.get('cv')
        company_file = request.files.get('companyList')

        if not cv_file or not company_file:
            return jsonify({'error': 'Missing files'}), 400

        # 1. Read PDF
        try:
            reader = PdfReader(cv_file)
            cv_text = ""
            for page in reader.pages:
                cv_text += page.extract_text()
        except Exception as e:
            return jsonify({'error': f'PDF Error: {str(e)}'}), 400

        # 2. Read CSV (Bulletproof Method)
        try:
            # Try 1: Standard UTF-8
            df = pd.read_csv(company_file)
        except UnicodeDecodeError:
            company_file.seek(0)
            try:
                # Try 2: Windows Standard (CP1252)
                df = pd.read_csv(company_file, encoding='cp1252')
            except UnicodeDecodeError:
                company_file.seek(0)
                # Try 3: Latin1 (Accepts ALL bytes - The "Nuclear" Fix)
                df = pd.read_csv(company_file, encoding='latin1')

        company_names = df.iloc[:, 0].tolist()

        generated_applications = []
        for company in company_names:
            # Clean company name of weird characters just in case
            safe_company_name = str(company).strip()
            cover_letter = generate_ai_cover_letter(name, safe_company_name, cv_text)
            generated_applications.append({ "company": safe_company_name, "letter": cover_letter })

        return jsonify({ 'status': 'success', 'count': len(generated_applications), 'applications': generated_applications })

    except Exception as e:
        # We use 'repr' here to safely print even weird characters to the console
        print(f"Server Error: {repr(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)