from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("resultspt")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.resultspt.com"


def _valid(val):
    val = val.strip()
    if val.endswith(","):
        val = val[:-1]

    return val


def parse(page_url, sp1):
    hours = []
    for hh in sp1.select("div.lmlw-hours-normal-wrap > div"):
        day = hh.select_one("span.lmlw-normal-hours__day").text
        time = ""
        if hh.select_one("span.lmlw-normal-hours-closed"):
            time = hh.select_one("span.lmlw-normal-hours-closed").text.strip()
        else:
            time = f"{hh.select_one('span.lmlw-normal-hours__openat').text.strip()}-{hh.select_one('span.lmlw-normal-hours__closeat').text.strip()}"
        hours.append(f"{day} {time}")

    return SgRecord(
        page_url=page_url,
        location_name=_valid(sp1.h1.text),
        street_address=_valid(sp1.select_one("span.lmlw-addr-wrap__address").text),
        city=_valid(sp1.select_one("span.lmlw-addr-wrap__city").text),
        state=_valid(sp1.select_one("span.lmlw-addr-wrap__state").text),
        zip_postal=_valid(sp1.select_one("span.lmlw-addr-wrap__zip").text),
        country_code="US",
        phone=_valid(sp1.select_one("span.lmlw-contact-phone__number").text),
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    base_url = "https://www.resultspt.com/locations"
    with SgRequests() as session:
        sp = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = sp.select("div.location-column li a")
        logger.info(f"{len(links)} locations found")
        for link in links:
            if not link.has_attr("href"):
                continue
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            if res.url != page_url:
                continue
            sp1 = bs(res.text, "lxml")
            sub_locations = sp1.select("div.location-meta ul li a")
            if sub_locations:
                for sub in sub_locations:
                    if not sub.has_attr("href"):
                        continue
                    page_url = locator_domain + sub["href"]
                    res = session.get(page_url, headers=_headers)
                    if res.status_code != 200:
                        continue
                    if res.url != page_url:
                        continue
                    sp1 = bs(res.text, "lxml")
                    yield parse(page_url, sp1)
            else:
                yield parse(page_url, sp1)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
