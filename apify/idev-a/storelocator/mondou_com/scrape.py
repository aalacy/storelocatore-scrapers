from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("mondou")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mondou.com/"
    base_url = (
        "https://www.mondou.com/fr-CA/trouver-un-magasin/repertoire-magasin?page={}"
    )
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.group-items div.group-item")
            logger.info(f"[page {page}] {len(links)} found")
            if not links:
                break
            page += 1
            for link in links:
                page_url = link.select_one("a.btn")["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = list(sp1.select_one("address").stripped_strings)[:-1]
                street_address = " ".join(addr[:-1])
                hours = []
                for hh in sp1.select("div.store-open-hour"):
                    hours.append(
                        f"{hh.select('div')[0].text.strip()}: {hh.select_one('div.open-times').text.strip()}"
                    )
                data = json.loads(
                    sp1.select_one('div[data-oc-controller="Store.Details"]')[
                        "data-context"
                    ]
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=page_url.split("/")[-1],
                    location_name=link.h6.strong.text.strip(),
                    street_address=street_address,
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip(),
                    zip_postal=addr[-1].split(",")[2].strip(),
                    country_code="CA",
                    phone=link.select_one("span.store-phone").text.strip(),
                    locator_domain=locator_domain,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
