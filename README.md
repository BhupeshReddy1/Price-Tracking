# Price-Tracking System
Overview
This project is an automated price alert system that helps users track the price of a product on an e-commerce website. Users provide a product link and a threshold price. The system checks the price of the product daily, and if the price falls below or equals the threshold value, it sends an alert to the user via email.

The system is deployed on PythonAnywhere and runs every 24 hours.

Features
Automated price tracking: Monitors product price on a daily basis.
Threshold-based alerts: Sends an email alert if the price drops below or equals the specified threshold.
Email notifications: Alerts sent using SMTP via the user's email account.
Technologies Used
Python 3.11
Requests library for web scraping
BeautifulSoup for HTML parsing
SMTP for email alerts
PythonAnywhere for cloud deployment and scheduling
How It Works
User Input: The user provides a product link from an e-commerce website and sets a threshold price.
Daily Check: The system checks the price of the product every 24 hours.
Price Alert: If the product price is less than or equal to the threshold, an alert is sent via email.
Deployment: The script is deployed on PythonAnywhere, which automatically triggers the daily check.
Setup Instructions
Prerequisites
Python 3.11
PythonAnywhere account for cloud deployment
Email account for SMTP (e.g., Gmail)
Local Setup
Clone the repository:

bash
Copy code
git clone https://github.com/BhupeshReddy1/Price-Tracking.git
cd price-alert-system
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up SMTP settings: Modify the script with your email settings (e.g., SMTP server, port, and login credentials).

Run the script:

bash
Copy code
python price_alert.py
Deploy on PythonAnywhere
Create a PythonAnywhere account: https://www.pythonanywhere.com
Upload the script: Use the file manager to upload the project files.
Set up a scheduled task: Schedule the price_alert.py to run every 24 hours in the PythonAnywhere tasks section.
Usage Example
Input a product link:
Example: [https://www..com/product
](https://www.amazon.com/COMAX-Fireside-Lounger-Oversized-Bedroom/dp/B0D9H7GQFV/ref=sr_1_1_sspa?adgrpid=1331510991303393&dib=eyJ2IjoiMSJ9.txYcFyVVOuqxz1l9urCl5H2DPWPAo2amoG--MSEJlvB4aNROr592a_UvQjBYdBLzDt-VOMz__0qpODENZ0YV9-ZrDhcxqVuUYx2T0NprcdoP2ts-B0KaylxsbatR7i5BGdHR3r2DCdyHIS7B2L-dm1y-UQhvprSVYyT9RN1OpuCPb9JYJ5MQi12cKf_PdIv9-neuD9TcFt7ksTpuO1g17QpnsbuA5hg27KX2EQj-jIqj9Ur3i2W3IWNlrLE5ZjQWvDNUtsA5i4pD8iKXSd1m1-m44ax5OeGRebzFhgo9b5E.23T6SGWR7YsJeqvnk2rRvAXmUgPMpZdwWdosePZ16rI&dib_tag=se&hvadid=83219702052472&hvbmt=bb&hvdev=c&hvlocphy=116074&hvnetw=o&hvqmt=b&hvtargid=kwd-83220496665482&hydadcr=9222_13502271&keywords=big%2Bcomfy%2Boversized%2Bchair&msclkid=ac274a9b52dc1a9a033b2d96dfb5d003&qid=1728941422&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1)
Set a threshold price:
Example: 2000

Wait for the email notification if the price drops below or equals 2000.
