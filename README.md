PDF Reader Backend
Welcome to the PDF Reader Backend! This backend service provides functionality to upload PDF files, extract text from them, and answer questions based on the extracted text using the Gemini API.

Installation
Clone this repository to your local machine:

bash
Copy code
git clone https://github.com/your-username/pdf-reader-backend.git
Navigate to the project directory:

bash
Copy code
cd pdf-reader-backend
Install dependencies using pip:

bash
Copy code
pip install -r requirements.txt
Configuration
Before running the backend, you need to configure the following:

Database URL:

Open the config.py file.
Set the DATABASE_URL variable to your PostgreSQL database URL.
Gemini API Key:

Obtain an API key for the Gemini API.
Set the GEMINI_API_KEY variable in the config.py file to your API key.
Running the Server
Start the backend server using the following command:

bash
Copy code
uvicorn app.main:app --reload
The server will start on http://localhost:8000. You can now make requests to the backend endpoints.

API Endpoints
POST /upload_pdf: Upload a PDF file and extract text from it.
POST /ask_question: Ask a question based on the extracted text from a PDF file.
For detailed documentation on each endpoint, refer to the API documentation or the codebase.

Frontend (PDF Reader Web)
The frontend allows users to interact with the PDF Reader application by uploading PDF files and viewing the extracted text.

Installation
Clone the frontend repository to your local machine:

bash
Copy code
git clone https://github.com/your-username/pdf-reader-web.git
Navigate to the project directory:

bash
Copy code
cd pdf-reader-web
Install dependencies using npm:

bash
Copy code
npm install
Configuration
Before running the frontend, you may need to configure the backend URL in the proxy setting.

Open the package.json file.

Update the proxy target to match the backend URL:

json
Copy code
"proxy": {
    "/api": {
        "target": "http://localhost:8000",
        "changeOrigin": true,
        "pathRewrite": {
            "^/api": ""
        }
    }
}
Running the Application
Start the frontend development server using the following command:

bash
Copy code
npm start
The application will be accessible at http://localhost:3000.

Contributing
We welcome contributions from the community! If you find any issues or have ideas for improvements, please open an issue or submit a pull request.
