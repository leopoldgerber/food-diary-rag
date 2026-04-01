from services.embedding_service import generate_embeddings_for_records


def main() -> None:
    result = generate_embeddings_for_records(
        input_path="data/processed/parsed_records.json",
        output_path="data/processed/records_with_embeddings.json",
    )

    print("Embedding summary")
    print(f"- Total records: {result['total_records']}")
    print(f"- Successfully embedded: {result['embedded_count']}")
    print(f"- Failed: {result['failed_count']}")
    print(f"- Output file: {result['output_path']}")

    if result["failed_records"]:
        print()
        print("Failed records")
        for item in result["failed_records"]:
            print(f"- {item['id']}: {item['error']}")


if __name__ == "__main__":
    main()
