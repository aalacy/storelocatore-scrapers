from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://docmj.com"
base_url = "https://docmj.com/states/florida/"


def fetch_data():
    with SgRequests() as session:
        states = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var serviceAreasLocations =")[1]
            .split(";</script>")[0]
            .strip()
        )
        for state in states:
            for _ in state["cities"]:
                page_url = _["city_page_permalink"]
                logger.info(page_url)
                try:
                    info = json.loads(
                        session.get(page_url, headers=_headers)
                        .text.split("var locationDetails =")[1]
                        .split("</script>")[0]
                        .strip()[:-1]
                    )["locations"][0]
                    raw_address = info["location_map"]["address"]
                    addr = raw_address.split(",")
                    street_address = ", ".join(addr[:-2])
                    zip_postal = addr[-1].strip().split()[-1]
                    if not zip_postal.replace("-", "").isdigit():
                        zip_postal = ""
                except:
                    raw_address = street_address = zip_postal = ""
                location_name = _["city_name"].replace("&#8211;", "-").strip()
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["locations"][0]["location_unique_id"],
                    location_name=location_name.split("(")[0],
                    street_address=street_address,
                    city=location_name.split("(")[0]
                    .split("-")[0]
                    .replace("II", "")
                    .replace("Orlando I", "Orlando")
                    .strip(),
                    state=state["state_name"],
                    zip_postal=zip_postal,
                    country_code="US",
                    latitude=_["locations"][0]["lat"],
                    longitude=_["locations"][0]["lng"],
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
