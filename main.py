import uvicorn
from wah_sales_api.presentation.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
