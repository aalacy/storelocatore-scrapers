from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("gucci")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

urls = [
    "https://www.gucci.com/us/en/store",
    "https://www.gucci.com/ca/en/store",
    "https://www.gucci.com/uk/en_gb/store",
]


def fetch_data():
    locator_domain = "https://www.gucci.com"
    with SgRequests() as session:
        for base_url in urls:
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            locations = soup.select("ol.search-results li.store-item")
            logger.info(f"[********] {len(locations)} found in {base_url}")
            for _ in locations:
                page_url = locator_domain + _.h3.a["href"]
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                loc = json.loads(
                    sp1.find("script", type="application/ld+json").string.strip()
                )
                hours = []
                for hh in loc["openingHoursSpecification"]:
                    day = f"{hh['dayOfWeek'][0]}-{hh['dayOfWeek'][-1]}"
                    if len(hh["dayOfWeek"]) == 1:
                        day = hh["dayOfWeek"][0]
                    time = f"{hh['opens']}-{hh['closes']}"
                    if time == "-":
                        time = "Closed"
                    hours.append(f"{day}: {time}")
                aa = loc["address"]
                street_address = ", ".join(
                    bs(aa["streetAddress"], "lxml").stripped_strings
                )
                addr = parse_address_intl(
                    f'{street_address} {aa["addressLocality"]}, {aa["addressRegion"]} {aa["postalCode"]} {aa["addressCountry"]}'
                )
                phone = loc["telephone"].split("(x")[0]
                if phone == "n/a":
                    phone = ""
                logger.info(f"[{aa['addressCountry']}] {page_url}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["data-store-code"],
                    location_type=_["data-store-type"],
                    location_name=_["data-store-name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    latitude=_["data-latitude"],
                    longitude=_["data-longitude"],
                    zip_postal=addr.postcode,
                    country_code=aa["addressCountry"],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
