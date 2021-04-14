from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("Â", "").replace("\xa0", "").strip()


def fetch_data():
    locator_domain = "http://www.villagemarketfoodcenters.com/"
    base_url = (
        "http://www.villagemarketfoodcenters.com/Additional-Company-Locations.html"
    )
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.find_all("div", id=re.compile(r"^element"))[2:]
        temp = []
        for x, location in enumerate(locations):
            if not location.img and location.text.strip() or location.iframe:
                temp.append(location)
        for x in range(0, len(temp), 4):
            block = list(temp[x + 1].stripped_strings)
            hours_of_operation = "; ".join(
                [_.text for _ in temp[x + 3].select("div") if _.text.strip()]
            ).replace("Hours:", "")
            iframe = session.get(temp[x + 2].iframe["src"]).text
            latitude = (
                iframe.split("var latitude =")[1]
                .split("var longitude =")[0]
                .strip()[1:-2]
            )
            longitude = (
                iframe.split("var longitude =")[1]
                .split("var mapWidth =")[0]
                .strip()[1:-2]
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_valid(temp[x].text.strip().split("(")[0]),
                street_address=_valid(block[0]),
                city=_valid(block[1].split(",")[0]),
                state=_valid(block[1].split(",")[1].strip().split(" ")[0]),
                zip_postal=_valid(block[1].split(",")[1].strip().split(" ")[-1]),
                country_code="US",
                phone=_valid(block[-1]),
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
