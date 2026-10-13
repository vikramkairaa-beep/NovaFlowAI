NOVAFLOW AI — START GUIDE (Tanglish)
====================================

Indha ZIP-la complete local prototype irukku:
- Excel/CSV upload
- Duplicate row + missing cell analysis
- Column quality details
- Report period fields
- Downloadable text report
- Recent report history
- Dark responsive dashboard

IMPORTANT:
Idhu prototype. Production-ready multi-company SaaS illa.
Login, user accounts, billing, AI API integration, company data isolation,
automated scheduled jobs, production security innum implement pannala.
Real KYC / personal / bank data upload pannadheenga. Sample data use pannunga.

WINDOWS 10 / DELL LAPTOP-LA RUN PANNA:

1. ZIP file-ai right-click > Extract All...
2. Extract panna NovaFlowAI folder open pannu.
3. Folder address bar-la click panni cmd nu type panni Enter press pannu.
4. CMD-la indha commands one by one type pannu:

   py -3.11 -m venv venv
   venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python app.py

   Python 3.11 illa na, installed Python version use pannu:
   py -m venv venv
   venv\Scripts\activate
   python -m pip install -r requirements.txt
   python app.py

5. CMD-la Running on http://127.0.0.1:5000 nu varum.
6. Chrome open panni http://127.0.0.1:5000 enter pannu.
7. CSV / XLSX file choose panni Analyze file click pannu.
8. Report result page-la download pannalaam.
9. Stop panna CMD window-la Ctrl + C press pannu.

SAMPLE CSV:
sample_data.csv file-ai first test-ku use pannalaam.

REPORT DATE NOTE:
From/To fields report-la date range label-aa save aagum.
Current prototype uploaded file rows-ai date field base-la filter pannaadhu.

DATA STORAGE:
Report history data/history.json-la store aagum.
Generated text reports reports/ folder-la store aagum.
Uploaded source file analysis mudinja udane delete aagum.
Local development use-ku mattum; public internet-la deploy panna munnaadi
security review, authentication, company-wise access controls, HTTPS,
retention policy, backup and production server setup MUST add pannanum.

TROUBLESHOOT:
- 'py' command work aagala na Python install path / launcher check pannu.
- Excel support-ku openpyxl requirements-la irukku.
- Port 5000 busy na app.py-la port=5001 nu change panni run pannalaam.
- Error vandha CMD-la irukkura full error message copy panni share pannu.
