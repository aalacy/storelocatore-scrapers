from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "partsauthority.com",
    "Origin": "https://partsauthority.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://partsauthority.com"
base_url = "https://partsauthority.com/locations/"
state_url = "https://partsauthority.com/branchloc/GetBranchesByState"


def fetch_records(http):
    res = http.get(base_url, headers=_headers).text
    locs = bs(res, "lxml").select("div.mul_location > a")
    header1["apikey"] = (
        res.split("var _paapiwebaddresskey =")[1].split("var")[0].strip()[1:-1]
    )
    for loc in locs:
        url = locator_domain + "/" + loc["href"]
        header1["Referer"] = url
        state_id = (
            http.get(url, headers=_headers)
            .text.split("var _paramStateId =")[1]
            .split(";")[0]
            .strip()[1:-1]
        )
        payload = {
            "BranchId": "null",
            "StateId": state_id,
            "StateName": "null",
            "ZipCode": "null",
            "RediusMile": "null",
        }
        locations = http.post(state_url, headers=header1, json=payload).json()["Result"]
        logger.info(f"{state_id}, {len(locations)}")
        for _ in locations:
            hours = []
            for hh in _["BranchTimingList"]:
                hours.append(f"{hh['WeekDay']}: {hh['TimingText']}")
            page_url = url + "/" + _["BranchLinkUrl"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["BranchId"],
                location_name=_["BranchName"],
                street_address=_["BranchAddress"],
                city=_["BranchCity"],
                state=_["StateName"],
                zip_postal=_["BranchZipCode"],
                country_code="US",
                latitude=_["BranchLat"],
                longitude=_["BranchLong"],
                phone=_["BranchPhone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests(verify_ssl=False) as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
