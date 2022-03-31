from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")


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
base_url = "https://www.acerentacar.com/AceWebService.asmx/GetNearbyLocations"
urls = [
    "https://www.acerentacar.com/LocationsUs.aspx",
    "https://www.acerentacar.com/LocationsIntl.aspx",
]


def fetch_data():
    with SgRequests() as session:
        for url in urls:
            us_locs = bs(session.get(url, headers=_headers).text, "lxml").select(
                "div.divLocation"
            )
            for us_loc in us_locs:
                loc_id = bs(
                    session.get(us_loc.a["href"], headers=_headers).text, "lxml"
                ).select_one("select#bookingBox_ddlReturnLocation option")["value"]
                logger.info("loc_id")
                data = {"Location": loc_id}
                locations = session.post(base_url, headers=_headers, json=data).json()[
                    "d"
                ]
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
