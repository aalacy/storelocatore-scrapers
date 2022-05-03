from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
import re


logger = SgLogSetup().get_logger("savidahealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday-Sunday"]

locator_domain = "https://savidahealth.com"
base_url = "https://savidahealth.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = (
            soup.find("a", string=re.compile(r"^Locations$"))
            .find_next_sibling()
            .select("ul li a")
        )
        logger.info(f"{len(states)} found")
        for state in states:
            state_url = state["href"]
            logger.info(state_url)
            sp0 = bs(session.get(state_url, headers=_headers).text, "lxml")
            if "locations-2" in state_url:
                links = sp0.select("table.tablepress tbody tr")
                for link in links:
                    td = link.select("td")
                    if "Coming Soon" in td[1].text or not td[3].text.strip():
                        continue
                    page_url = td[2].a["href"]
                    times = [hh.text for hh in td[4:]]
                    hours = []
                    for x in range(6):
                        hours.append(f"{days[x]}: {times[x]}")
                    logger.info(page_url)
                    ss = json.loads(
                        session.get(page_url, headers=_headers)
                        .text.split("var wpsl_locator_single =")[1]
                        .split("var wpsl_locator_single =")[0]
                        .split("/* ]]")[0]
                        .strip()[:-1]
                    )

                    street_address = ss["address"].strip()
                    if street_address.endswith(","):
                        street_address = street_address[:-1]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=ss["title"],
                        street_address=street_address,
                        city=td[0].text.split(",")[0].strip(),
                        state=ss["state"],
                        zip_postal=ss["zip"],
                        country_code="US",
                        phone=td[1].text.strip(),
                        locator_domain=locator_domain,
                        latitude=ss["latitude"],
                        longitude=ss["longitude"],
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                    )
            else:
                links = sp0.select("div.vc-ihe-panel")
                for link in links:
                    if "Coming Soon" in link.text:
                        continue
                    hours = []
                    for hh in link.select("table.tablepress tr"):
                        hours.append(f"{': '.join(hh.stripped_strings)}")

                    page_url = link.find_next_sibling("div").a["href"]
                    logger.info(page_url)
                    ss = json.loads(
                        session.get(page_url, headers=_headers)
                        .text.split("var wpsl_locator_single =")[1]
                        .split("var wpsl_locator_single =")[0]
                        .split("/* ]]")[0]
                        .strip()[:-1]
                    )

                    street_address = ss["address"].strip()
                    if street_address.endswith(","):
                        street_address = street_address[:-1]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=ss["title"],
                        street_address=street_address,
                        city=ss["city"].split(",")[0],
                        state=ss["state"],
                        zip_postal=ss["zip"],
                        country_code="US",
                        phone=ss["phone"]
                        or link.find_next_sibling("div")
                        .find("a", href=re.compile(r"tel:"))
                        .text.strip(),
                        locator_domain=locator_domain,
                        latitude=ss["latitude"],
                        longitude=ss["longitude"],
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
