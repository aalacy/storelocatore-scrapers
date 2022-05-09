from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.pdsa.org.uk"
base_url = "https://www.pdsa.org.uk/near-me"
json_url = "https://www.pdsa.org.uk/Umbraco/api/NearMeApi/GetLocationsNearPostCode"

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.pdsa.org.uk",
    "referer": "https://www.pdsa.org.uk/near-me",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "x-csrf-token": "",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_records(session, search):
    for zip_code in search:
        data = f'postCode={zip_code.replace(" ", "+")}&distance=25&locationTypes%5B%5D=PAH&locationTypes%5B%5D=PAP&locationTypes%5B%5D=VOL&locationTypes%5B%5D=SHOP&locationTypes%5B%5D=OFFICE&requiresFreeWill=false'
        try:
            locations = session.post(json_url, data=data, headers=headers).json()[
                "Results"
            ]
        except:
            continue
        logger.info(f"[{zip_code}] {len(locations)}")
        for _ in locations:
            page_url = locator_domain + _["Url"]
            street_address = _["AddressLine1"]
            if _["AddressLine2"]:
                street_address += " " + _["AddressLine2"]
            if _["AddressLine3"]:
                street_address += " " + _["AddressLine3"]
            street_address = street_address.replace("PDSA SHOP", "").replace("PDSA", "")
            st = street_address.split(" ")
            street_address = " ".join([ss for ss in st if ss.strip()])
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=_["LocationName"],
                street_address=street_address,
                city=_["Town"],
                state=_["County"],
                zip_postal=_["PostCode"],
                country_code="UK",
                phone=_["TelephoneNumber"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                location_type=_["LocationType"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgRequests() as http:
        res = http.get(base_url)
        headers["x-csrf-token"] = bs(res.text, "lxml").select_one(
            'input[name="__RequestVerificationToken"]'
        )["value"]
        headers["cookie"] = res.headers["set-cookie"]
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.BRITAIN], granularity=Grain_4()
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
            )
        ) as writer:
            for rec in fetch_records(
                http,
                search,
            ):
                writer.write_row(rec)
