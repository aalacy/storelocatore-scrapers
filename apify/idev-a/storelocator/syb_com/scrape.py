from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("syb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://syb.com"
    base_url = "https://syb.com/locations/?ext=."
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.locations-view div.location-container")
        logger.info(f"{len(links)} found")
        for _ in links:
            addr = []
            for aa in list(_.select_one("div.address-contact").stripped_strings)[1:]:
                if "Get Directions" in aa:
                    break
                addr.append(
                    " ".join(
                        [
                            dd.strip()
                            for dd in aa.replace("\n", "").split()
                            if dd.strip()
                        ]
                    )
                )
            phone = ""
            if _.select_one("div.phone"):
                phone = list(_.select_one("div.phone").stripped_strings)[-1]
            location_type = "branch"
            for ll in _.select("div.services ul li"):
                if ll.text.strip() == "atm":
                    location_type += ", atm"
            coord = (
                _.select_one("div.directions a")["href"].split("?daddr=")[1].split(",")
            )
            hours = []
            for hh in _.select("div.hours table tbody tr"):
                td = list(hh.stripped_strings)
                hours.append(f"{td[0]}: {td[1]}")

            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one("div.location-title").text.strip(),
                street_address=addr[0],
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                location_type=location_type,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
