from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("savidahealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday-Sunday"]


def fetch_data():
    locator_domain = "https://savidahealth.com"
    base_url = "https://savidahealth.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.vc_tta-panel table tbody tr")
        logger.info(f"{len(links)} found")
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

            yield SgRecord(
                page_url=page_url,
                location_name=ss["title"],
                street_address=ss["address"],
                city=td[0].text.strip(),
                state=ss["state"],
                zip_postal=ss["zip"],
                country_code="US",
                phone=td[1].text.strip(),
                locator_domain=locator_domain,
                latitude=ss["latitude"],
                longitude=ss["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
