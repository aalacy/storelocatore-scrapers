from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.annastaqueria.com/"
    base_url = "https://www.annastaqueria.com/locations/"
    with SgRequests() as session:
        soup = bs(session.post(base_url, headers=_headers).text, "lxml")
        maps = [
            (mm["data-lat"], mm["data-lng"])
            for mm in soup.select(".location_links a.location_link")
        ]
        locations = soup.select("div.locations_wrapper div.location_item")
        for x, _ in enumerate(locations):
            location_name = list(_.select_one("div.location_title").stripped_strings)[0]
            addr = list(_.select_one("div.location-address").stripped_strings)
            hours = list(_.select_one("div.location-hours p").stripped_strings)
            coord = maps[x]
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0],
                state=addr[1].split(",")[1],
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=_.select_one("div.location-phone").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=" ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
