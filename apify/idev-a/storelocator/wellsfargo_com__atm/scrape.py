from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("wellsfargo")

locator_domain = "https://www.wellsfargo.com/"
base_url = "https://www.wellsfargo.com/locator/"
payload_url = "https://www.wellsfargo.com/locator/as/getpayload"
sitemap1 = "https://www.wellsfargo.com/locator/sitemap1"
sitemap2 = "https://www.wellsfargo.com/locator/sitemap2"

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.wellsfargo.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        total = 0
        streets = []
        # sitemap1
        links = bs(session.get(sitemap1).text, "lxml").text.strip().split("\n")
        for link in links:
            session.get(link, headers=_headers)
            locations = session.post(payload_url, headers=_headers).json()[
                "searchResults"
            ]
            total += len(locations)
            logger.info(f"[total {total}] {len(locations)} locations")
            for _ in locations:
                if _["locationLine1Address"] in streets:
                    continue
                streets.append(_["locationLine1Address"])

                page_url = (
                    f"https://www.wellsfargo.com/locator/bank/?slindex={_['index']}"
                )
                hours_of_operation = "; ".join(_.get("arrDailyEvents", []))
                if (
                    "incidentMessage" in _
                    and _["incidentMessage"].get("incidentDesc", "").lower()
                    == "temporary closure"
                    and _["incidentMessage"].get("outletStatusDesc", "").lower()
                    == "closed"
                ):
                    hours_of_operation = "Temporary closed"
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["branchName"],
                    street_address=_["locationLine1Address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["postalcode"],
                    country_code="US",
                    latitude=_["latitude"],
                    location_type=_["locationType"],
                    longitude=_["longitude"],
                    phone=_["phone"].strip(),
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

        # sitemap2
        links = (
            bs(session.get(sitemap2, headers=_headers).text, "lxml")
            .text.strip()
            .split("\n")
        )
        for link in links:
            res = session.get(link, headers=_headers)
            if "error.html" in res.url:
                continue
            sp1 = bs(res.text, "lxml")
            location_type = sp1.select_one("div.fn.heading").text.strip()
            if "ATM" not in location_type:
                continue
            if sp1.find("", string=re.compile(r"could not find")):
                continue
            logger.info(link)
            try:
                coord = (
                    sp1.select_one("div.mapView img")["src"]
                    .split("Road/")[1]
                    .split("/")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            hours = []
            _hr = sp1.find("h2", string=re.compile(r"Lobby Hours", re.IGNORECASE))
            if _hr:
                hours = list(_hr.find_next_sibling().stripped_strings)
            addr = [
                aa for aa in list(sp1.address.stripped_strings) if aa.strip() != ","
            ]
            street_address = " ".join(addr[1].split(",")[:-1])
            if street_address in streets:
                continue
            streets.append(street_address)
            yield SgRecord(
                page_url=link,
                location_name=addr[0],
                street_address=street_address,
                city=addr[1].split(",")[-1],
                state=addr[2],
                zip_postal=addr[3],
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
