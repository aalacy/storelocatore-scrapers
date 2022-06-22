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
loc_url = "https://bitcoindepot.com/get-map-points/"


def fetch_records(http):
    res = http.get(base_url)
    header1["x-csrftoken"] = res.cookies.get("csrftoken")
    locations = http.post(loc_url, headers=header1).json()["set_locations"]
    for _ in locations:
        hours_of_operation = ""
        if _.get("hours"):
            hours_of_operation = (
                _["hours"]
                .replace("\n", "; ")
                .replace("\r", "")
                .replace("\t", " ")
                .replace("–", "-")
                .strip()
                .replace(",", "; ")
                .replace("Unknown", "")
                .strip()
            )
        else:
            hours_of_operation = _.get("hours_of_operation")

        country_code = "US"
        if _["state"] in ca_provinces_codes:
            country_code = "CA"
        if hours_of_operation and hours_of_operation.strip().endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        zip_postal = _.get("zip")
        if zip_postal:
            zip_postal = zip_postal.replace("Canada", "").replace(",", "").strip()
        street_address = _["address"].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        if street_address.endswith("USA"):
            addr = street_address.split(",")
            street_address = ", ".join(addr[:-3])
        yield SgRecord(
            page_url=base_url,
            location_name=_["name"],
            street_address=street_address,
            city=_["city"],
            state=_["state"],
            zip_postal=zip_postal,
            location_type=_.get("type"),
            latitude=_.get("lat"),
            longitude=_.get("lng"),
            country_code=country_code,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=_["address"],
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
