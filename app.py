import uvicorn as uvicorn
from src.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=5,timeout_keep_alive=600, reload=False)  # here the number of workers specified should be number of cores * 2 +1 
 
