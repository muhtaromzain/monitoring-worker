from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from process_data import ProcessData
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

API_HOST = os.getenv('API_HOST')
API_PORT = int(os.getenv('API_PORT'))

app = FastAPI(
    title="EPO Worker Queue",
    description="EPO Worker queue services",
    version="1.0.0"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReturnException(BaseModel):
    detail: str

class Return201(BaseModel):
    status: str
    dt_code: str
    timestamps: str

class Order(BaseModel):
    dt_code: str
    timestamps: str

@app.post("/order/send_to_cp", status_code=201, responses={
    201: {
        "model": Return201,
        "description": "Send to Customer Portal successful"
    },
    409: {
        "model": ReturnException,
        "description": "Send to Customer Portal failed",
    }
})
async def sendToCp(order: Order):
    dtCode = order.dt_code
    timestamps = order.timestamps

    try:
        ProcessData.sendToCp(dtCode, timestamps)
        result = Return201(status='Sent', dt_code=dtCode, timestamps=timestamps)
        return result
    except: 
        raise HTTPException(
            status_code=409, detail='Failed to sent'
        )

@app.post("/order/send_txt_to_cp", status_code=201, responses={
    201: {
        "model": Return201,
        "description": "Send to Customer Portal successful"
    },
    409: {
        "model": ReturnException,
        "description": "Send to Customer Portal failed",
    }
})
async def sendTxtToCp(order: Order):
    dtCode = order.dt_code
    timestamps = order.timestamps

    data = {
        'existDtCodeOrder': '("")',
        'dtCode': '("' + dtCode + '")',
        'timestamps': timestamps,
        'basename': dtCode + '_' + timestamps
    }

    try:
        ProcessData.export(data, isAuto=False)
        result = Return201(status='Sent', dt_code=dtCode, timestamps=timestamps)
        return result
    except: 
        raise HTTPException(
            status_code=409, detail='Failed to sent'
        )

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)