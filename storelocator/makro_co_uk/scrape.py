from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("makro")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.co.uk"
base_url = "https://www.makro.co.uk/stores.html"
locator_url = "https://www.makro.co.uk/locator.html?thetowncity=london&thepostcode=&country=GB&distance=500&locate=x&csrf_token=336b23cb4ebc5f6bb9c3d1f726cf0491"


def _coord(locs, name):
    for loc in locs:
        _ = loc.split("google.maps.event.addListener(")[0]
        if name.replace("Store", "").strip() in _:
            return _.split(" new google.maps.LatLng(")[-1].split(")")[0].split(",")


def fetch_data():
    with SgRequests() as session:
        locs = session.get(locator_url, headers=_headers).text.split(
            "new google.maps.Marker("
        )[1:]
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#cb_id_CONTENT table td a")
        for link in locations:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            hours = list(sp1.select("div#cb_id_CONTENT ul")[0].stripped_strings)
            raw_address = ", ".join(
                list(sp1.select("div#cb_id_CONTENT ul")[-1].stripped_strings)
            )
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city:
                if "Manchester" in city:
                    city = "Manchester"

            location_name = sp1.select_one("div#cb_id_CONTENT h1").text.strip()
            latlng = _coord(locs, location_name)
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=raw_address.split(",")[-1],
                country_code="UK",
                phone=list(sp1.select("div#cb_id_CONTENT ul")[1].stripped_strings)[0]
                .split(":")[-1]
                .strip(),
                latitude=latlng[0],
                longitude=latlng[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
