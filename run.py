from dotenv import load_dotenv

from app import create_app

load_dotenv()  # ✅ Load environment variables

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)