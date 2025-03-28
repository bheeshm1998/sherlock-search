
from config.pinecone_init import pc


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

def list_index_vectors():
    """
    Lists all indexes in Pinecone along with the number of stored vectors in each.
    """
    print("Listing all indexes present in Pinecone:")
    indexes = pc.list_indexes().names()

    if not indexes:
        print("No indexes found in Pinecone.")
        return

    for index_name in indexes:
        print(f"\n Index: {index_name}")

        # Connect to the index
        index = pc.Index(index_name)

        # Retrieve index statistics
        try:
            stats = index.describe_index_stats()
            vector_count = stats.get("total_vector_count")
            print(f"Total Vectors: {vector_count}")
        
        except Exception as e:
            print(f"   ⚠️ Error retrieving index stats: {e}")


if __name__ == "__main__":
    list_indexes()
    # list_index_vectors()
    # delete_index("project-30")
    delete_index("project-31")
    # delete_index("project-11")
    # delete_index("project-23")
    # delete_index("project-22")
    # list_indexes()