import csv
import sys

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("CsvDiffer")
        print(
            "Usage: python csv-differ.py new-data-file.csv old-data-file.csv <csv-identity-field> [--verbose]"
        )
        exit(1)

    file_new_path = sys.argv[1]
    file_old_path = sys.argv[2]
    csv_id_field = sys.argv[3]
    verbose = True if len(sys.argv) == 5 and sys.argv[4] == "--verbose" else False

    with open(file_new_path) as file_new:
        with open(file_old_path) as file_old:
            new_lines, old_lines = 0, 0

            reader_new = csv.DictReader(file_new)
            new_ids = set()
            for row in reader_new:
                new_lines += 1
                new_ids.add(row[csv_id_field])

            reader_old = csv.DictReader(file_old)
            old_ids = set()
            for row in reader_old:
                old_lines += 1
                old_ids.add(row[csv_id_field])

            common = old_ids.intersection(new_ids)
            not_in_new = old_ids.difference(new_ids)
            not_in_old = new_ids.difference(old_ids)

            divider = "-----------------------------------------------------------------------------------------------------"

            print(divider)
            print("Summary:")
            print(
                f"Common: {len(common)} | Missing in new: {len(not_in_new)} | Missing in old: {len(not_in_old)} | {file_new_path} records: {new_lines} | {file_old_path} records: {old_lines}"
            )

            if verbose:

                print(divider)
                for z in common:
                    print(f"Common >> {z}")

                print(divider)
                for z in not_in_new:
                    print(f"Missing in new >> {z}")

                print(divider)
                for z in not_in_old:
                    print(f"Missing in old >> {z}")

                print(divider)
