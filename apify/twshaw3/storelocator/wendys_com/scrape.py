from sgrequests import SgRequests
import csv
from typing import Set


class Wendys:
    csv_filename = "data.csv"
    domain_name = "wendys.com"
    url = "https://locationservices.wendys.com/LocationServices/rest/nearbyLocations"
    seen: Set[str] = set()
    csv_fieldnames = [
        "locator_domain",
        "page_url",
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
    ]

    def encode(self, string):
        return string

    def handle_missing(self, field):
        if field is None or (isinstance(field, str) and len(field.strip()) == 0):
            return "<MISSING>"
        return field

    def map_data(self, row):
        return {
            "locator_domain": self.domain_name,
            "page_url": "<MISSING>",
            "location_name": self.handle_missing(
                self.encode(row.get("name", "<MISSING>"))
            ),
            "street_address": self.handle_missing(
                self.encode(row.get("address1", "<MISSING>"))
            ),
            "city": self.handle_missing(self.encode(row.get("city", "<MISSING>"))),
            "state": self.handle_missing(self.encode(row.get("state", "<MISSING>"))),
            "zip": self.handle_missing(
                self.encode(row.get("postal", "<MISSING>"))
                if len(row.get("postal", "")) <= 6
                else None
            ),
            "country_code": self.handle_missing(
                self.encode(row.get("country", "<MISSING>"))
            ),
            "store_number": self.handle_missing(
                self.encode(row.get("id", "<MISSING>"))
            ),
            "phone": self.handle_missing(
                self.encode(row.get("phone", "<MISSING>"))
                if len(row.get("phone", "")) >= 10
                else None
            ),
            "location_type": "<MISSING>",
            "latitude": self.handle_missing(row.get("lat", "<MISSING>")),
            "longitude": self.handle_missing(row.get("lng", "<MISSING>")),
            "hours_of_operation": self.handle_missing(
                ", ".join(
                    "%s-%s; day %d"
                    % (d.get("openTime"), d.get("closeTime"), d.get("day"))
                    for d in row.get("daysOfWeek", "")
                )
            ),
        }

    def crawl(self):
        session = SgRequests()
        session.headers.update(
            {
                "Accept": "application/json",
                "cache-control": "no-cache",
                "path": "/LocationServices/rest/nearbyLocations?&lang=en&cntry=US&sourceCode=ORDER.WENDYS&version=5.31.3&address=94107&limit=10000&filterSearch=true&radius=5000",
                "Origin": "https://order.wendys.com",
                "Referer": "https://order.wendys.com/location?site=find",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            }
        )
        query_params = {
            "lang": "en",
            "cntry": "US",
            "sourceCode": "ORDER.WENDYS",
            "version": "5.31.3",
            "address": "94107",
            "limit": 10000,
            "radius": 5000,
            "filterSearch": True,
        }
        r = session.get(self.url, params=query_params)
        if r.status_code == 200:
            for row in r.json().get("data", []):
                if str(row["id"]) in self.seen:
                    continue
                else:
                    self.seen.add(str(row["id"]))
                yield row

    def write_to_csv(self, rows):
        output_file = self.csv_filename
        with open(output_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in rows:
                if hasattr(self, "map_data"):
                    row = self.map_data(row)
                writer.writerow(row)

    def run(self):
        rows = self.crawl()
        self.write_to_csv(rows)


if __name__ == "__main__":
    w = Wendys()
    w.run()
