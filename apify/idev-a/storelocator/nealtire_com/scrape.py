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
        "referer": "https://www.nealtire.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # accept-encoding: gzip, deflate, br
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    }


def fetch_data():
    locator_domain = "https://www.nealtire.com/"
    session.get("https://www.nealtire.com/", headers=_headers())
    base_url = "https://www.nealtire.com/Tires"
    r = session.get(base_url, headers=_headers())
    soup = bs(r.text, "lxml")
    locations = soup.select("div.locwidgetlisting")
    data = []
    for location in locations:
        page_url = location.select_one(".locwidget-name a")["href"]
        location_name = location.select_one(".locwidget-name").text
        street_address = location.select_one(".locwidget-addr").text.replace(",", "")
        city = location.select_one(".locwidget-csz").text.split(",")[0]
        state = (
            location.select_one(".locwidget-csz")
            .text.split(",")[1]
            .strip()
            .split(" ")[0]
        )
        zip = (
            location.select_one(".locwidget-csz")
            .text.split(",")[1]
            .strip()
            .split(" ")[1]
        )
        country_code = "US"
        store_number = location["id"].replace("locWidget", "")
        location_type = "<MISSING>"
        phone = location.select_one(".locwidget-phone a").text
        latitude = location.select_one(".locwidget-latlong").text.split(",")[0]
        longitude = location.select_one(".locwidget-latlong").text.split(",")[1]
        r1 = session.get(page_url, headers=_headers())
        soup1 = bs(r1.text, "lxml")
        hours = soup1.select("#ndau-mobile #ndauhours li.ndauday")
        _hours = []
        for hour in hours:
            text = [_ for _ in hour.stripped_strings]
            _hours.append(f'{text[0]}: {"-".join(text[1:])}')
        hours_of_operation = "; ".join(_hours)

        _item = [
            locator_domain,
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
