
# Routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import chat_router
from routers.user import user_router
from mangum import Mangum 


app = FastAPI()

# Allow CORS for extension and frontend
# origins = ["http://localhost:3000", "chrome-extension://*", "*"].

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel!"}

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://insight-chat.vercel.app", "http://localhost:3000", "chrome-extension://*"],
     allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(user_router)
app.include_router(chat_router)

handler = Mangum(app)

