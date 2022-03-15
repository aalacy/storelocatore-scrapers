from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xae", " ")
        .replace("\\u2022", " ")
    )


def fetch_data():
    locator_domain = "https://www.poundstretcher.co.uk"
    base_url = "https://www.poundstretcher.co.uk/find-a-store"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        scripts = [
            script.contents[0] for script in soup.find_all("script") if script.contents
        ]
        items = []
        for script in scripts:
            if "initial_locations:" in script:
                items = json.loads(
                    script.split("initial_locations:")[1]
                    .strip()
                    .split("min_zoom: 10,")[0]
                    .strip()[:-1]
                )
                break

        for item in items:
            page_url = "http://www.poundstretcher.co.uk/" + item["website_url"]
            location_name = item["title"].strip()
            _address = [
                _.strip() for _ in item["address_display"].split("\n") if _.strip()
            ]
            if len(_address) == 1:
                _address = [
                    _.strip() for _ in item["address_display"].split(",") if _.strip()
                ]

            if _address[-1] == "UK":
                _address.pop()

            if _address[0] == location_name:
                _address = _address[1:]

            zip = _address[-1]
            if len(zip.split(",")) > 1:
                zip = zip.split(",")[1]
                _address.pop()
                _address.append(zip.split(",")[0])

            if len(zip.split(" ")) > 2:
                zip = " ".join(zip.split(" ")[1:])
                _address.pop()
                _address.append(zip.split(" ")[0])

            # missing city in address_display, location_name can be city
            city = location_name.split(" ")[0]
            street_address = " ".join(_address[:-1])
            if len(_address) > 2:
                city = _address[-2]
                street_address = " ".join(_address[:-2])
                if len(city.split("\\")) > 1:
                    city = city.split("\\")[1]
                    street_address += " " + city.split("\\")[0]

                location_type = "<MISSING>"
                soup1 = bs(session.get(page_url).text, "html.parser")
                if soup1.select("div#store-address"):
                    store = soup1.select("div#store-address")[-1]
                    if store:
                        _address = [_ for _ in store.stripped_strings]
                        if _address[-1].replace(" ", "").isdigit():
                            _address = _address[:-1]
                        if _address[0].strip() == "Address & Contact Details":
                            _address = _address[1:]
                        if _address[-1] == "UK":
                            _address.pop()

                        location_type = _address[0]

                soup2 = bs(item["notes"], "lxml")
                hours = []
                for _ in soup2.select("tr"):
                    if not _.td:
                        continue
                    hours.append(f"{_.th.text.strip()} {_.td.text.strip()}")

                yield SgRecord(
                    page_url=page_url,
                    store_number=item["location_id"],
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=zip,
                    phone=item.get("phone"),
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    location_type=location_type,
                    country_code=item["country"],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid("; ".join(hours)),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
