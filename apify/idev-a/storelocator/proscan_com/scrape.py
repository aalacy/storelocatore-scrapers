import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
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
        )
        # Body
        for row in data:
            writer.writerow(row)


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://proscan.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }


def fetch_data():
    start_url = "https://proscan.com/"
    session.get(start_url, headers=_headers())
    base_url = "https://proscan.com/for-patients/find-a-center/"
    r = session.get(base_url, headers=_headers())
    soup = bs(r.text, "html.parser")
    locations = soup.select("div#locations .location")
    data = []
    for location in locations:
        store_number = location["data-location_id"]
        location_name = location.select_one("h3").text
        page_url = location.select_one("h3 a")["href"]
        r1 = session.get(page_url, headers=_headers())
        soup1 = bs(r1.text, "lxml")
        block = [_ for _ in soup1.select_one(".entry-content div").stripped_strings]
        street_address = block[1]
        city = myutil._valid(block[2].split(",")[0])
        state = block[2].split(",")[1].strip().split(" ")[0]
        zip = myutil._strip_list(block[2].split(",")[1].strip().split(" "))[1].strip()
        country_code = myutil.get_country_by_code(state)
        idx = 3
        while True:
            if block[idx] == "Direct:":
                phone = block[idx + 1].replace("–", "-")
                idx += 2
                break
            idx += 1
        if block[idx] == "Fax:":
            idx += 2

        if block[idx] == "Toll Free:":
            idx += 2

        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        location_type = "<MISSING>"
        hours = []
        for _hour in block[idx:]:
            if _hour.strip() == "Hours of Operation":
                continue
            if _hour.strip() == "MRI":
                continue
            if _hour.strip() == "CT":
                break
            hours.append(_hour)
        hours_of_operation = (
            str("; ".join(hours).replace("–", "-").encode("utf-8"))[2:-1]
            .replace("\\xc2\\xa0", " ")
            .replace("\ufeff", "")
            .replace("\\xef\\xbb\\xbf", "")
            .strip()
        )
        if "THIS PROSCAN IMAGING CENTER IS PERMANENTLY CLOSED" in hours_of_operation:
            hours_of_operation = "CLOSED"

        _item = [
            base_url,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        data.append(_item)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
