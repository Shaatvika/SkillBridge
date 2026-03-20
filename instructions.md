python3 --version
node --version
unzip skillbridge.zip
cd skillbridge
python3 -m venv venv

# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

pip install fastapi uvicorn pydantic anthropic httpx pytest python-dotenv

cp .env.example .env
```
Open `.env` and edit it:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
uvicorn app.main:app --reload
```
Expected output:
```
INFO: Uvicorn running on http://127.0.0.1:8000

cd frontend
npm install

npm run dev
```
Expected output:
```
VITE ready
➜  Local: http://localhost:5173/

pytest tests/ -v

