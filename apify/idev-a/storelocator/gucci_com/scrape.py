from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("gucci")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.gucci.com"
base_url = "https://www.gucci.com/int/en/store"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ol.search-results li.store-item")
        logger.info(f"[********] {len(locations)} found")

        for _ in locations:
            page_url = locator_domain + _.h3.a["href"]
            logger.info(f"{page_url}")
            res = session.get(page_url, headers=_headers)
            if res.url == "https://www.gucci.com/int/en/store":
                continue
            sp1 = bs(res.text, "lxml")
            try:
                loc = json.loads(
                    sp1.find("script", type="application/ld+json").string.strip()
                )
            except:
                loc = json.loads(
                    sp1.find("script", type="application/ld+json")
                    .string.replace('""Shop', '"Shop')
                    .replace('Shanghai"', "Shanghai")
                    .strip()
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
            state = sp1.select_one('span[itemprop="addressRegion"]').text
            if state.isdigit():
                state = ""
            country_code = aa["addressCountry"]
            if country_code.isdigit():
                country_code = ""
            zip_postal = aa["postalCode"]
            if zip_postal == "00000":
                zip_postal = ""
            street_address = (
                ", ".join(bs(aa["streetAddress"], "lxml").stripped_strings)
                .split("T:")[0]
                .strip()
            )
            addr = parse_address_intl(f'{aa["addressLocality"]} {state} {zip_postal}')
            state = addr.state
            if state:
                state = " ".join(list(set(state.split(" "))))

            if addr.country:
                country_code = addr.country

            if (
                "korea" in street_address.lower()
                or "china" in street_address.lower()
                or "UAE" in street_address
            ):
                addr = parse_address_intl(street_address)
                street_address = addr.street_address_1 or ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if addr.country:
                    country_code = addr.country

            raw_address = " ".join(_.select_one("p.address").stripped_strings)
            addr = parse_address_intl(raw_address)
            if addr.country:
                country_code = addr.country

            city = aa["addressLocality"]
            if city and not country_code:
                if city in ["London"]:
                    country_code = "UK"
                elif city in ["Paris"]:
                    country_code = "FR"
                elif city in ["Seoul"]:
                    country_code = "KR"
                elif city in ["Dalian"]:
                    country_code = "CN"
            zip_postal = addr.postcode
            phone = loc["telephone"].split("(x")[0]
            if phone == "n/a" or phone == "N/A":
                phone = ""

            yield SgRecord(
                page_url=page_url,
                store_number=_["data-store-code"],
                location_type=_["data-store-type"],
                location_name=_["data-store-name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
