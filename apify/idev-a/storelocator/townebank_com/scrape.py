from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.townebank.com"
base_url = "https://www.townebank.com/api/search/searchlocations?latitude=0&longitude=0&locationType=Office+Locations"


def fetch_data(writer):
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["Locations"]:
            hours = []
            if _["LobbyHours"]:
                temp = [
                    hh.strip()
                    for hh in _["LobbyHours"].strip().split("\n")
                    if hh.strip()
                ]
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]}: {temp[x+1]}")
            page_url = locator_domain + _["Url"]
            zip_postal = bs(_["Zip"], "lxml").text.strip()
            if zip_postal and "coming soon" in zip_postal.lower():
                continue
            rec = SgRecord(
                page_url=page_url,
                location_name=_["LocationTitle"],
                street_address=_["Address"],
                city=_["City"],
                state=_["StateCode"],
                zip_postal=zip_postal,
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="US",
                phone=_["Telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )
            writer.write_row(rec)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
