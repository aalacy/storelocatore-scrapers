from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://eurochange.es"
base_url = "https://eurochange.es/en/currency-exchange-offices"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def _d(page_url, sp1, city, state):
    raw_address = (
        list(sp1.select_one("div.localesmapa p.bcol1").stripped_strings)[0]
        .replace("   ", "")
        .replace("\n", "")
    )
    coord = (
        sp1.select_one("div.localesmapa p.bcol1 a")["href"].split("/")[-1].split(",")
    )
    addr = raw_address.split("·")
    temp = list(sp1.select_one("ul.geofull li span").stripped_strings)
    hours = []
    day = ""
    times = []
    for x, hh in enumerate(temp):
        if hh.startswith(">"):
            if day and times:
                hours.append(f"{day} {' '.join(times)}")
                times = []
                day = ""
            day = hh
        else:
            times.append(hh)

        if x == len(temp) - 1:
            hours.append(f"{day} {' '.join(times)}")

    return SgRecord(
        page_url=page_url,
        location_name=sp1.h1.text.strip(),
        street_address=addr[0],
        city=city,
        state=state,
        zip_postal=addr[-1].strip().split()[0].strip(),
        country_code="Spain",
        phone=_p(sp1.select("ul.geofull li")[-1].text.strip()),
        latitude=coord[0],
        longitude=coord[1],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours)
        .replace(">", "")
        .replace("  ", "")
        .replace("\n", " "),
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.oficinas-cambio ul li")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            city = _.a.text.strip()
            state = _.find_parent("ul").find_previous_sibling().text.strip()
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            locales = sp1.select("ul.locales li")
            if locales:
                for loc in locales:
                    url = locator_domain + loc["onclick"].split("=")[-1][1:-2]
                    logger.info(url)
                    sp2 = bs(session.get(url, headers=_headers).text, "lxml")
                    yield _d(url, sp2, city, state)

            else:
                yield _d(page_url, sp1, city, state)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
