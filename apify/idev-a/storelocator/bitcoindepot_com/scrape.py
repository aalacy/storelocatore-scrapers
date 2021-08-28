from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bitcoindepot")

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://bitcoindepot.com",
    "referer": "https://bitcoindepot.com/locations/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bitcoindepot.com"
base_url = "https://bitcoindepot.com/locations/"
map_url = "https://bitcoindepot.com/get-map-points/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        header1["x-csrftoken"] = res.cookies.get_dict()["csrftoken"]

        locations = session.post(map_url, headers=header1).json()["set_locations"]
        for _ in locations:
            hours_of_operation = ""
            if _.get("hours"):
                hours_of_operation = (
                    _["hours"]
                    .replace("\n", "; ")
                    .replace("\r", "")
                    .replace("–", "-")
                    .strip()
                    .replace(",", "; ")
                    .replace("Unknown", "")
                )

            country_code = "US"
            if _["state"] in ca_provinces_codes:
                country_code = "CA"
            yield SgRecord(
                page_url="https://bitcoindepot.com/locations/",
                location_name=_["name"],
                street_address=_["address"].replace(",", ""),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                location_type=_["type"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=country_code,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
