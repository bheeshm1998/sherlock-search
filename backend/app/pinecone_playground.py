
from app.config.pinecone_init import pc

def list_indexes():
    # List all indexes
    print("Listing down the indexes present in pinecone")
    indexes = pc.list_indexes()
    print("Indexes in Pinecone:", indexes)

def delete_index(index_name):
    # List all indexes
    print("Deleting the index ", index_name)
    indexes = pc.delete_index(index_name)
    print("Index deleted successfully")


if __name__ == "__main__":
    list_indexes()
    delete_index("payoda-index-1")
    list_indexes()