from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import List, Optional, Dict, Any
from bson import ObjectId
import os
from dotenv import load_dotenv
from pymongo import UpdateOne  # Import UpdateOne explicitly

# Load environment variables
load_dotenv()

class MongoCRUD:
    def __init__(self, collection_name: str = 'ib_samples'):
        """
        Initialize MongoDB connection and collection
        
        :param collection_name: Name of the MongoDB collection
        """
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(os.getenv('MONGO_URI'))
        self.db: AsyncIOMotorDatabase = self.client.nailib_samples
        self.collection: AsyncIOMotorCollection = self.db[collection_name]

    async def create_sample(self, sample_data: Dict[str, Any]):
        """
        Insert a new IA/EE sample into the database
        
        :param sample_data: Dictionary containing sample details
        :return: Inserted document's ID
        """
        # Upsert based on source URL to prevent duplicates
        result = await self.collection.update_one(
            {'source_url': sample_data.get('source_url')},
            {'$set': sample_data},
            upsert=True
        )
        
        # Return the inserted or updated document's ID
        return result.upserted_id or sample_data.get('_id')

    async def bulk_create_samples(self, samples_data: List[Dict[str, Any]]):
        """
        Bulk insert or update multiple IA/EE samples
        
        :param samples_data: List of sample dictionaries
        :return: List of inserted/updated document IDs
        """
        bulk_operations = []
        for sample in samples_data:
            bulk_operations.append(
                UpdateOne(
                    {'source_url': sample.get('source_url')},
                    {'$set': sample},
                    upsert=True
                )
            )
        
        if bulk_operations:
            result = await self.collection.bulk_write(bulk_operations)
            return result.upserted_ids
        return []

    async def get_sample_by_id(self, sample_id: str):
        """
        Retrieve a single IA/EE sample by its MongoDB ID
        
        :param sample_id: MongoDB document ID
        :return: Sample document or None
        """
        return await self.collection.find_one({'_id': ObjectId(sample_id)})

    async def get_samples_by_subject(self, subject: str, limit: int = 10):
        """
        Retrieve IA/EE samples by subject
        
        :param subject: IB Subject (e.g., 'Math AI SL')
        :param limit: Maximum number of samples to retrieve
        :return: List of sample documents
        """
        return await self.collection.find({'subject': subject}).to_list(length=limit)

    async def update_sample(self, sample_id: str, update_data: dict):
        """
        Update an existing IA/EE sample
        
        :param sample_id: MongoDB document ID
        :param update_data: Dictionary of fields to update
        :return: Updated document
        """
        await self.collection.update_one(
            {'_id': ObjectId(sample_id)}, 
            {'$set': update_data}
        )
        return await self.get_sample_by_id(sample_id)

    async def delete_sample(self, sample_id: str):
        """
        Delete an IA/EE sample by its ID
        
        :param sample_id: MongoDB document ID
        :return: Deletion result
        """
        return await self.collection.delete_one({'_id': ObjectId(sample_id)})

    async def count_samples(self, filter_criteria: Optional[dict] = None):
        """
        Count the number of samples matching given criteria
        
        :param filter_criteria: Optional dictionary of filter conditions
        :return: Number of matching samples
        """
        return await self.collection.count_documents(filter_criteria or {})


def serialize_mongo_document(document):
    """Converts MongoDB ObjectId to string in a document."""
    if isinstance(document, dict):
        # Convert ObjectId to string if it exists
        if '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
    return document