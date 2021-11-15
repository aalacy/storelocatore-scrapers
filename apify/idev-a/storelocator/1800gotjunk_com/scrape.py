from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("1800gotjunk")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

base_url = [
    {
        "locator_domain": "https://www.1800gotjunk.com",
        "country": "USA",
        "url": "https://www.1800gotjunk.com/us_en/locations",
    },
    {
        "locator_domain": "https://www.1800gotjunk.com",
        "country": "CA",
        "url": "https://www.1800gotjunk.com/ca_en/locations",
    },
    {
        "locator_domain": "https://www.1800gotjunk.com.au",
        "country": "AU",
        "url": "https://www.1800gotjunk.com.au/au_en/locations",
    },
]


def _d(page_url, locator_domain, _, city, country):
    addr = _["address"]
    hours = []
    for hh in _["openingHoursSpecification"]:
        hours.append(f"{hh['dayOfWeek']}: {hh['opens']} - {hh['closes']}")
    return SgRecord(
        page_url=page_url,
        store_number=page_url.split("/")[-1],
        location_name=_["name"],
        street_address=addr["streetAddress"],
        city=city,
        state=addr["addressRegion"],
        zip_postal=addr["postalCode"],
        country_code=country,
        phone=_["telephone"],
        latitude=_["geo"].get("latitude"),
        longitude=_["geo"].get("longitude"),
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    with SgRequests() as session:
        for _url in base_url:
            soup = bs(session.get(_url["url"], headers=_headers).text, "lxml")
            locations = soup.select("div.location-menus ul li ul li a")
            for link in locations:
                page_url = link["href"]
                if not page_url.startswith("http"):
                    page_url = _url["locator_domain"] + link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                if sp1.find("script", type="application/ld+json"):
                    try:
                        city = list(
                            sp1.select_one(
                                "p.group-local-page-address"
                            ).stripped_strings
                        )[1].split(",")[0]
                    except:
                        continue
                    for _ in json.loads(
                        sp1.find("script", type="application/ld+json").string
                    )["@graph"]:
                        yield _d(
                            page_url, _url["locator_domain"], _, city, _url["country"]
                        )
                else:
                    locs = sp1.select("div.section-local-item a")
                    for url in locs:
                        page_url = url["href"]
                        if not page_url.startswith("http"):
                            _page_url = _url["locator_domain"] + url["href"]
                            logger.info(_page_url)
                            sp2 = bs(
                                session.get(_page_url, headers=_headers).text, "lxml"
                            )
                            try:
                                city = list(
                                    sp2.select_one(
                                        "p.group-local-page-address"
                                    ).stripped_strings
                                )[1].split(",")[0]
                            except:
                                continue
                            if sp2.find("script", type="application/ld+json"):
                                for loc in json.loads(
                                    sp2.find(
                                        "script", type="application/ld+json"
                                    ).string
                                )["@graph"]:
                                    yield _d(
                                        _page_url,
                                        _url["locator_domain"],
                                        loc,
                                        city,
                                        _url["country"],
                                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
