from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("medievaltimes")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

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


def fetch_data():
    locator_domain = "https://www.medievaltimes.com/"
    base_url = "https://www.medievaltimes.com/locations"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("castles:")[1]
            .split("current_castle:")[0]
            .strip()[1:-2]
        )
        for key, _ in locations.items():
            if key.isdigit():
                continue
            page_url = locator_domain + _["full_uri"]
            logger.info(page_url)
            ss = json.loads(
                bs(session.get(page_url, headers=_headers).text, "lxml")
                .find("script", type="application/ld+json")
                .string
            )
            country_code = "US"
            if _["state"] in ca_provinces_codes:
                country_code = "CA"
            hours_of_operation = f"{ss['openingHoursSpecification']['name']}: {ss['openingHoursSpecification']['opens']}-{ss['openingHoursSpecification']['closes']}".replace(
                "Opening Hours", ""
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=ss["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=country_code,
                phone=_["phone_number"],
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
