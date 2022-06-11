import csv


class Scrape:
    def __init__(self, url):
        self.url = url

    def write_output(self, data):
        with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
            writer = csv.writer(
                output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )

            # Header
            writer.writerow(
                [
                    "locator_domain",
                    "location_name",
                    "street_address",
                    "city",
                    "state",
                    "zip",
                    "country_code",
                    "store_number",
                    "phone",
                    "location_type",
                    "latitude",
                    "longitude",
                    "hours_of_operation",
                    "page_url",
                ]
            )
            # Body
            for row in data:
                writer.writerow(row)

    def fetch_data(self):
        pass

    def scrape(self):
        self.fetch_data()
        self.write_output(self.data)
