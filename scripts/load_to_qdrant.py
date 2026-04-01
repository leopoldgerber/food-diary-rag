from services.qdrant_ingest_service import load_records_into_qdrant


def main() -> None:
    result = load_records_into_qdrant(
        input_path="data/processed/records_with_embeddings.json",
        collection_name="food_diary_notes",
    )

    print("Qdrant load summary")
    print(f"- Collection: {result['collection_name']}")
    print(f"- Input records: {result['input_records']}")
    print(f"- Stored points: {result['stored_points']}")
    print(f"- Vector size: {result['vector_size']}")


if __name__ == "__main__":
    main()
