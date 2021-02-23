from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgFirefox
import json

locator_domain = "https://www.carshop.co.uk/"
base_url = "https://www.carshop.co.uk/our-stores"


def _headers():
    return {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "referer": "https://www.carshop.co.uk/used-automatic-cars",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    }


def fetch_data():
    with SgFirefox() as driver:
        driver.get(base_url)
        json_data = (
            driver.page_source.split("StoresSimple:")[1]
            .strip()
            .split("})(CarShop.Properties);")[0]
            .strip()[:-2]
            .strip()
        )
        locations = json.loads(json_data)
        for key, _ in locations.items():
            page_url = locator_domain + key
            addr = parse_address_intl(_["addressString"])
            hours = []
            if "weekday" in _:
                hours.append(f"Monday-Friday: {_['weekday']}")
            if "saturday" in _:
                hours.append(f"Saturday: {_['saturday']}")
            if "sunday" in _:
                hours.append(f"Sunday: {_['sunday']}")

            hours_of_operation = "; ".join(hours)
            record = SgRecord(
                page_url=page_url,
                location_name=_["displayName"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=_["postcode"],
                country_code="UK",
                phone=_["phone"],
                latitude=_["geoCodes"].split(",")[0].strip(),
                longitude=_["geoCodes"].split(",")[1].strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
