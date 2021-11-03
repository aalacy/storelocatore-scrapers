from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("levelonebank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .split(":")[-1]
        .replace("Phone", "")
    )


def fetch_data():
    locator_domain = "https://www.levelonebank.com"
    base_url = "https://www.levelonebank.com/Resources/Customer-Support/Locations-Hours"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-accord a.details")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("p.loc_addr").stripped_strings)
            hours = []
            days = []
            for dd in sp1.select("table.location-table tr.tbl-titles"):
                day = dd.text.strip()
                if "Drive" in day or "Lobby" in day:
                    break
                days.append(day)
            times = [tt.text.strip() for tt in sp1.findAll("tr", class_=None)]
            hours = [f"{k}:{v}" for k, v in dict(zip(days, times)).items()]
            script = json.loads(
                '{"options"'
                + sp1.select_one("div.edMaps_moduleWrapper script")
                .string.strip()
                .split('{"options"')[1][:-6]
            )["markers"][0]
            if addr[-1].startswith("Fax"):
                del addr[-1]
            phone = addr[-1].split(":")[-1].replace("Phone", "")
            if not _p(phone).isdigit():
                phone = sp1.select_one("p.contact-details").text
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.headerImageTitle").text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone.strip().split(":")[-1].replace("Phone", ""),
                locator_domain=locator_domain,
                latitude=script["position"]["latitude"],
                longitude=script["position"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
