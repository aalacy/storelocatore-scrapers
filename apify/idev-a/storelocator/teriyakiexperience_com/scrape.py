from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("teriyakiexperience")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.teriyakiexperience.com/"
base_url = "https://www.teriyakiexperience.com/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.home-location-store-info")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            street_address = city = state = zip_postal = ""
            country_code = "CA"
            for aa in sp1.select("div.location-container ul.list-unstyled li"):
                addr = aa.text.split(":")[-1].strip()
                if "Address" in aa.text:
                    street_address = addr
                if "City" in aa.text:
                    city = addr.split(",")[0].strip()
                    zip_postal = addr.split(",")[1].strip()
                if "Province" in aa.text:
                    state = addr
                if "Country" in aa.text:
                    country_code = addr
            ss = json.loads(
                sp1.select_one("div.google-map-object")["data-data"].replace(
                    "&quot;", '"'
                )
            )[0]
            hours = []
            _hr = sp1.select_one("div.contact-container ul.list-unstyled > strong")
            if _hr and _hr.text.strip() == "Hours":
                temp = list(
                    sp1.select_one(
                        "div.contact-container ul.list-unstyled"
                    ).stripped_strings
                )
                for x, hh in enumerate(temp):
                    if hh == "Hours":
                        hours = temp[x + 1 :]
                        if "Order Online" in hours[-1]:
                            del hours[-1]
                        break

            location_name = link.h5.text.strip()
            location_type = ""
            if "temporarily closed" in location_name.lower():
                location_type = "Temporarily Closed"
                location_name = location_name.split("-")[0].strip()
            phone = ""
            if sp1.select_one("div.contact-container ul.list-unstyled a"):
                phone = sp1.select_one(
                    "div.contact-container ul.list-unstyled a"
                ).text.strip()
                if not _p(phone):
                    phone = ""
            yield SgRecord(
                page_url=page_url,
                store_number=ss["info"]["ID"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=ss["position"]["lat"],
                longitude=ss["position"]["lng"],
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=ss["info"]["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
