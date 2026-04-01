from services.ingest_service import run_ingestion


def main() -> None:
    result = run_ingestion(
        notes_dir="data/raw",
        output_path="data/processed/parsed_records.json",
    )

    print("Ingestion summary")
    print(f"- Total files: {result['total_files']}")
    print(f"- Successfully parsed: {result['parsed_count']}")
    print(f"- Failed: {result['failed_count']}")
    print(f"- Output file: {result['output_path']}")

    if result["failed_files"]:
        print()
        print("Failed files")
        for item in result["failed_files"]:
            print(f"- {item['filename']}: {item['error']}")


if __name__ == "__main__":
    main()
