from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.flanigans.net"
base_url = "https://www.flanigans.net/locations/"


def _hoo(hr):
    hours = []
    for hh in hr.find_next_siblings():
        _ho = hh.text.strip()
        if not _ho:
            continue
        if "seven days" in _ho.lower():
            continue
        hours.append(_ho)
    return hours


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        locations = json.loads(
            res.text.split('<script type="application/ld+json">')[1].split("</script>")[
                0
            ]
        )["subOrganization"]
        for _ in locations:
            addr = _["address"]
            logger.info(_["url"])
            sp1 = bs(session.get(_["url"], headers=_headers).text, "lxml")
            online_ordering = sp1.select_one("section#intro div.row").find(
                "", string=re.compile(r"Online Ordering")
            )
            if online_ordering:
                hr = (
                    online_ordering.find_parent()
                    .find_parent()
                    .find_parent()
                    .find_parent()
                )

                if hr:
                    hours = _hoo(hr)
                if not hours:
                    hours = _hoo(hr.find_parent())
            else:
                hr = sp1.select_one("section#intro").find(
                    "",
                    string=re.compile(
                        r"seven days a week",
                    ),
                )
                if hr:
                    hours = [hr.text.strip()]

            location_name = addr["name"]
            location_type = ""
            if "Temporarily  Closed" in location_name:
                location_type = "Temporarily  Closed"
            location_name = location_name.split("(")[0].strip()
            yield SgRecord(
                page_url=_["url"],
                location_name=location_name,
                street_address=addr["streetAddress"].split(",")[0],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                country_code="US",
                phone=_["telephone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
