# RecipeClinch

🌟 StarClinch - Backend System
A robust Django-based backend system supporting advanced user role management, cloud storage (AWS S3, Cloudinary), Celery task scheduling, PostgreSQL/MySQL/SQLite3 databases, Redis as a message broker, and a fully documented API with Swagger.


🚀 Project Setup Instructions
1. 📥 Clone the Repository
https://github.com/Aman-786-Jha/RecipeClinch/


2. 📁 Navigate to Project Directory
cd starclinch

3. 🐍 Create & Activate Virtual Environment
For macOS/Linux:

python3 -m venv env
source env/bin/activate
For Windows:

python -m venv env
env\Scripts\activate

4. 📦 Install Dependencies

pip install -r requirements.txt


🛠️ Configuration Steps
5. ⚙️ Database Setup
You can use PostgreSQL, MySQL, or SQLite3.

6. 🖼️ Cloudinary Setup (for Image Uploads)
Cloudinary handles image uploads efficiently. Make sure your credentials are correctly

7. ☁️ AWS S3 Setup (for File Storage)
Ensure your bucket is properly configured with the right region and permissions. The uploaded CSV reports from scheduled tasks will be saved here.

8. Mail configuration

9.run python manage.py makemigrations
python manage.py migrate
these command will run in the directory where the manage.py file exists.


🧠 Running the Application
9. 🌐 Run the Django Development Server
python manage.py runserver


⚙️ Celery Configuration (Background Tasks)
We are using Celery for scheduled background jobs 
10. 🧵 Start Celery Worker
In a new terminal, run:

celery -A starclinch worker --pool=threads --loglevel=info
celery -A starclinch beat --loglevel=info



📄 API Documentation
Visit:

http://127.0.0.1:8000/swagger/

You will see all available API endpoints documented using Swagger (drf-yasg).

Use your Bearer Token to authorize and explore protected routes.

UUIDs are used as IDs in detail views and will be provided in API responses.

📧 Contact
If you have questions, feel free to reach out at: amanjha5889@gmail.com



