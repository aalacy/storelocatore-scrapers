from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("codeninjas")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}
locator_domain = "https://www.codeninjas.com/"
base_url = "https://services.codeninjas.com/api/locations/queryarea?latitude=37.09024&longitude=-95.712891&includeUnOpened=false&miles=5117.825778587137"


def fetch_data():
    with SgRequests() as session:
        json_data = session.get(
            base_url,
            headers=_headers,
        ).json()
        for data in json_data:
            if data["status"] != "OPEN":
                continue
            street_address = data["address1"] or ""

            if data["address2"]:
                street_address += " " + data["address2"]

            page_url = locator_domain + data["cnSlug"]
            logger.info(page_url)

            soup1 = bs(
                session.get(
                    page_url,
                    headers=_headers,
                ).text,
                "lxml",
            )

            phone = data["phone"] or ""
            if not phone and soup1.find("a", href=re.compile(r"tel:")):
                phone = soup1.find("a", href=re.compile(r"tel:")).text.strip()

            hours = []
            if soup1.select_one("div#centerHours ul li"):
                for hh in soup1.select_one("div#centerHours ul li").stripped_strings:
                    if "Birthday" in hh:
                        break
                    hours.append(hh)
                if hours and (
                    hours[0].lower() == "by appointment only"
                    or hours[0].lower() == "by appointment"
                    or "Program hours may vary" in hours[0]
                ):
                    hours = []

            country_code = data["countryCode"]
            if data["postalCode"].replace("-", "").strip().isdigit():
                country_code = "US"

            yield SgRecord(
                page_url=page_url,
                location_name=data["name"],
                street_address=street_address,
                city=data["city"],
                state=data["state"]["code"],
                zip_postal=data["postalCode"]
                .replace("UK", "")
                .replace(",", "")
                .strip(),
                country_code=country_code,
                longitude=data["longitude"],
                latitude=data["latitude"],
                phone=phone.split("/")[0].split(",")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .split("or")[0]
                .split("To")[0]
                .split("#")[0]
                .split("*")[0]
                .split("(Note")[0]
                .replace("|", ";")
                .replace("//", ";")
                .replace("Imp", "")
                .replace("call f", "")
                .replace("By Appt", "")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
