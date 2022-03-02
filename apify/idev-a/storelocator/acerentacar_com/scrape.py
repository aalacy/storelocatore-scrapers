from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://www.acerentacar.com",
    "referer": "https://www.acerentacar.com/Locator.aspx",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.acerentacar.com"
base_url = "https://www.acerentacar.com/AceWebService.asmx/GetMapLocations"


def fetch_data():
    with SgRequests() as session:
        data = {"Location": ""}
        locations = session.post(base_url, headers=_headers, json=data).json()["d"]
        for _ in locations:
            page_url = locator_domain + _["PagePath"]
            street_address = _["Address1"]
            if _["Address2"]:
                street_address += " " + _["Address2"]
            if not street_address and not _["City"]:
                continue
            hours = []
            if _["Monday"]:
                hours.append(f"Monday: {_['Monday']}")
            if _["Tuesday"]:
                hours.append(f"Tuesday: {_['Tuesday']}")
            if _["Wednesday"]:
                hours.append(f"Wednesday: {_['Wednesday']}")
            if _["Thursday"]:
                hours.append(f"Thursday: {_['Thursday']}")
            if _["Friday"]:
                hours.append(f"Friday: {_['Friday']}")
            if _["Saturday"]:
                hours.append(f"Saturday: {_['Saturday']}")
            if _["Sunday"]:
                hours.append(f"Sunday: {_['Sunday']}")
            zip_postal = _["ZipCode"]
            if zip_postal == "0000":
                zip_postal = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_["Name"],
                street_address=street_address,
                city=_["City"],
                state=_["State"],
                zip_postal=zip_postal,
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=_["Country"],
                phone=_.get("ArrivalPhone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
