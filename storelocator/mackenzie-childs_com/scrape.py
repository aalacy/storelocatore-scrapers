from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("mackenzie")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.mackenzie-childs.com",
    "referer": "https://www.mackenzie-childs.com/stores",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mackenzie-childs.com"
base_url = "https://www.mackenzie-childs.com/stores"


def _p(val):
    return (
        val.split("x")[0]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        url = soup.select_one("form#dwfrm_storelocator_int")["action"]
        countries = [
            cc["value"]
            for cc in soup.select("select#dwfrm_storelocator_country option")
        ][1:]
        logger.info(f"{len(countries)} countries found")
        for country in countries:
            data = {
                "dwfrm_storelocator_country": country,
                "dwfrm_storelocator_findbycountry": "Search",
            }
            sp1 = bs(session.post(url, headers=header1, data=data).text, "lxml")
            locations = sp1.select("table#store-location-results tbody tr")
            logger.info(f"[{country}] {len(locations)} locations found")
            for _ in locations:
                td = _.select("td")
                page_url = locator_domain + td[0].a["href"]
                _addr = list(td[1].stripped_strings)
                addr = parse_address_intl(", ".join(_addr[:2]))
                phone = _addr[-1]
                if not _p(phone):
                    phone = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=td[0].text.split("(")[0].strip(),
                    street_address=_addr[0].replace(
                        "Papeles Telas y Accesorios SRL", ""
                    ),
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
