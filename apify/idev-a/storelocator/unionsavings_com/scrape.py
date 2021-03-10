from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
import re


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.unionsavings.com/"
        base_url = "https://www.unionsavings.com/locations/"
        r = session.get(base_url)
        soup = bs(r.text, "lxml")
        locations = soup.select("div#locations-wrapper div.item")
        for _location in locations:
            location = json.loads(_location["data-info"])
            page_url = location["permalink"]
            location_name = location["name"]
            city = location["city"]
            street_address = location["address"]
            state = location["state"]
            zip = location["zip"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            hours_of_operation = soup1.select_one("span.status").text
            phone = "<MISSING>"
            if hours_of_operation != "Closed":
                phone = (
                    soup1.select_one(".subcolumn", string=re.compile("Phone"))
                    .select("span")[-1]
                    .text
                )
                hours = soup1.select_one(
                    ".column", string=re.compile("Lobby Hours")
                ).select("span")[1:]
                _hours = []
                for hour in hours:
                    _hours.append(": ".join([_ for _ in hour.stripped_strings][::-1]))
                hours_of_operation = "; ".join(_hours)

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
