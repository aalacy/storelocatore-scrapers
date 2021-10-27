from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
import dirtyjson as json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("softrontax")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.softrontax.com/"
    base_url = "https://www.softrontax.com/_next/static/chunks/pages/location-aa24ab21981fa6e087fc.js"
    with SgRequests(verify_ssl=False) as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("),n=")[1]
            .split(",o=t(")[0]
            .strip()
        )
        for _ in locations:
            hours = []
            for x, hh in enumerate(_["times"]):
                hours.append(f"{days[x]}: {hh}")
            yield SgRecord(
                page_url="https://www.softrontax.com/location",
                street_address=_["address"],
                city=_["city"].split(",")[0].strip(),
                state=_["city"].split(",")[-1].strip(),
                zip_postal=_["pcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="CA",
                phone=_["pnumber"].split("/")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
