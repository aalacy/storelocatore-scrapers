from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lifestance")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://lifestance.com/"
    base_url = "https://lifestance.com/location/"
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#state option"
        )
        logger.info(f"{len(states)} states found")
        for state in states:
            if not state.get("data-permalink"):
                continue
            state_url = state["data-permalink"]
            locations = bs(
                session.get(state_url, headers=_headers).text, "lxml"
            ).select("div#locations-search-map div.marker")
            logger.info(f"[{state.text}] {len(locations)} locations found")
            for _ in locations:
                addr = _["data-address"].split("\n")[1].split(",")
                page_url = _["data-link"]
                logger.info(f"[{state.text}] {page_url}")
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = [
                    ":".join(hh.stripped_strings)
                    for hh in sp1.select("div.location__hours li")
                ]
                phone = ""
                if sp1.select_one("div.location__phone"):
                    phone = sp1.select_one("div.location__phone").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["data-id"],
                    location_name=_["data-title"],
                    street_address=_["data-address"].split("\n")[0].strip(),
                    city=addr[0].strip(),
                    state=addr[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=_["data-lat"],
                    longitude=_["data-lng"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
