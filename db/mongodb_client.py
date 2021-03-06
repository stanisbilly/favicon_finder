import pymongo
from datetime import datetime


class MongoDbClient:
    '''
    Simple PyMongo wrapper with operations targeting onlg single documents.
    '''

    conn = None
    host = None
    port = -1
    db_name = None

    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.init()

    def init(self):
        '''
        Helper method initalize the Mongo client.
        '''
        db_client = pymongo.MongoClient(self.host, self.port)
        self.conn = db_client[self.db_name]
        
    def find_one(self, coll_name, search_terms):
        '''
        Helper method to find a document.

        Arguments:
        coll_name -- name of the Mongo collection
        search_terms -- dictionary containing the search terms/filters

        Returns: 
        A document with the Mongo '_id' field omitted.
        '''
        coll = self.conn[coll_name]
        return coll.find_one(search_terms, { '_id': 0 })

    def insert_one(self, coll_name, doc):
        '''
        Helper method to insert a document.

        Arguments:
        coll_name -- name of the Mongo collection
        doc -- a dictionary representing the object to be inserted

        Returns: 
        The MongoDB-generated document ID
        '''
        coll = self.conn[coll_name]
        doc['last_modified'] = datetime.utcnow()
        return coll.insert_one(doc).inserted_id

    def update_one(self, coll_name, filter_terms, updates):
        '''
        Helper method to insert a document.

        Arguments:
        coll_name -- name of the Mongo collection
        filter_terms -- dictionary containing filters to search for the document
        updates -- a dictionary representing new values for the document

        Returns: 
        The MongoDB-generated document ID
        '''
        coll = self.conn[coll_name]
        updates['last_modified'] = datetime.utcnow()
        return coll.update_one(filter_terms, {'$set': updates})
        
    def drop(self, coll_name):
        '''
        Helper method to drop a collection.

        Arguments:
        coll_name -- name of the Mongo collection be dropped
        '''
        coll = self.conn[coll_name]
        coll.drop()

    def get_max_id(self, coll_name):
        '''
        Helper method to get the max value of the 'id' field of all 
        documents in a collection.

        Arguments:
        coll_name -- name of the Mongo collection to be searched

        Returns:
        Max value (int) of the 'id' field among all documents in collection
        '''
        coll = self.conn[coll_name]
        result = coll.find().sort('id', pymongo.DESCENDING).limit(1)
        max_id = -1
        for doc in result:
            max_id = doc['id']
            break
        return max_id