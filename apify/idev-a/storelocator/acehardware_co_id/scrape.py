from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from webdriver_manager.chrome import ChromeDriverManager
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.acehardware.co.id"
base_url = "https://www.acehardware.co.id/store-locations"
json_url = "/store-locations/map-data"


def _p(val):
    return (
        val.split("Phone")[-1]
        .split("Telp")[-1]
        .split("WhatsApp")[-1]
        .split("WA:")[-1]
        .split("/")[0]
        .split(",")[0]
        .split("atau")[0]
        .replace(":", "")
        .strip()
    )


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    rr = driver.wait_for_request(json_url, timeout=20)
    locations = json.loads(rr.response.body)
    for loc in locations:
        for _ in loc["stores"]:
            raw_address = (
                _["address"]
                .split("Phone")[0]
                .split("Telp")[0]
                .split("WhatsApp")[0]
                .split("WA:")[0]
                .split("CBD")[0]
                .split(" UG")[0]
                .split(" LG")[0]
                .replace("Timu", "")
                .replace("Indah II", "Indah 2")
                .strip()
            )
            if "Timu" in raw_address and "Timur" not in raw_address:
                raw_address = "Timur"
            if raw_address.endswith(", S"):
                raw_address = raw_address.replace(", S", "")
            phone = ""
            if (
                "Phone" in _["address"]
                or "Telp" in _["address"]
                or "WhatsApp" in _["address"]
            ):
                phone = _p(_["address"])
            addr = parse_address_intl(raw_address + ", Indonesia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city:
                if "No " in city or "No." in city or "Km." in city or "Kec." in city:
                    street_address += " " + city
                    city = ""
                city = (
                    city.replace("Lt.", "")
                    .replace("/1", "")
                    .replace("Said.", "")
                    .replace("M-S", "")
                    .replace("Indonesia", "")
                    .replace("Ix", "")
                    .replace("Gf-A1.", "")
                )

                if city.isdigit() or city == "B" or city == "Ali" or city == "RS":
                    city = ""

            if "Kalibata City" in raw_address:
                city = "Kalibata City"

            state = addr.state
            if state:
                state = state.replace("Lt.", "")

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Indonesia",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
