from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from final import main as scrape_main
from model import IAModel, convert_model_to_dict
from mongo import MongoCRUD,serialize_mongo_document

app = FastAPI(
    title="Nailib IB Samples API",
    description="API for scraping and managing IB Internal Assessment and Extended Essay samples",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_crud = MongoCRUD()

@app.post("/scrape", response_model=dict)
async def trigger_scraping(background_tasks: BackgroundTasks):
    """
    Trigger background scraping process and store results in MongoDB
    """
    try:
        # Run scraping in background
        background_tasks.add_task(scrape_and_store)
        return {"status": "Scraping initiated", "message": "Scraping process started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_and_store():
    """
    Async function to scrape samples and store in MongoDB
    """
    try:
        # Directly await the async main function from final.py
        result = await scrape_main()
        return result
    except Exception as e:
        print(f"Scraping error: {e}")
        raise

@app.get("/samples", response_model=List[IAModel])
async def get_samples(
    subject: Optional[str] = None, 
    limit: int = 10
):
    """
    Retrieve IA/EE samples with optional filtering
    """
    try:
        if subject:
            print(f"Retrieving samples for subject: {subject}")
            samples = await mongo_crud.get_samples_by_subject(subject, limit)
        else:
            samples = await mongo_crud.collection.find().to_list(length=limit)
        
        return [IAModel(
            id=str(sample['_id']),  
            **{k: v for k, v in sample.items() if k != '_id'}
        ) for sample in samples]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/samples/count", response_model=dict)
async def count_samples(subject: Optional[str] = None):
    """
    Count the number of samples, optionally filtered by subject
    """
    try:
        filter_criteria = {'subject': subject} if subject else None
        count = await mongo_crud.count_samples(filter_criteria)
        return {"total_samples": count, "subject": subject}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/samples/{sample_id}", response_model=IAModel)
async def get_sample_by_id(sample_id: str):
    """
    Retrieve a specific sample by its MongoDB ID
    """
    try:
        sample = await mongo_crud.get_sample_by_id(sample_id)
        if not sample:
            raise HTTPException(status_code=404, detail="Sample not found")
        return IAModel(**sample)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)