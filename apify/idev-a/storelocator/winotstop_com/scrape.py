from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs

locator_domain = "http://www.winotstop.com/"
base_url = "https://www.google.com/maps/d/u/0/embed?mid=1bhjoPX9KjTp7NSJTRRGwoOPUYmA"
map_url = "https://www.google.com/maps/dir//{},{}/@{},{}z"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://ladiperie.com/",
    }


def _phone(val):
    return (
        val.replace("Phone", "")
        .replace("-", "")
        .replace(")", "")
        .replace("(", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    streets = []
    with SgChrome() as driver:
        with SgRequests() as session:
            res = session.get(base_url, headers=_headers())
            cleaned = (
                res.text.replace("\\t", " ")
                .replace("\t", " ")
                .replace("\\n]", "]")
                .replace("\n]", "]")
                .replace("\\n,", ",")
                .replace("\\n", "#")
                .replace('\\"', '"')
                .replace("\\u003d", "=")
                .replace("\\u0026", "&")
                .replace("\\", "")
                .replace("\xa0", " ")
            )
            locations = json.loads(
                cleaned.split('var _pageData = "')[1].split('";</script>')[0][:-1]
            )
            for _ in locations[1][6][0][12][0][13][0]:
                location_name = _[5][0][1][0]
                sharp = [
                    ss.strip()
                    for ss in _[5][1][1][0].replace("  ", "#").split("#")
                    if ss.strip()
                ]
                phone = ""
                for ss in sharp:
                    if _phone(ss):
                        phone = ss.replace("Phone", "")
                        break
                latitude = _[1][0][0][0]
                longitude = _[1][0][0][1]
                driver.get(map_url.format(latitude, longitude, latitude, longitude))
                sp1 = bs(driver.page_source, "lxml")
                addr = parse_address_intl(
                    sp1.select("input.tactile-searchbox-input")[-1]["aria-label"]
                    .replace("Destination", "")
                    .strip()
                )
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                if street_address in streets:
                    continue
                streets.append(street_address)
                yield SgRecord(
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
