import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.mcdonalds.at"
base_url = "https://www.mcdonalds.at/restaurants"
json_url = r"https://www.mcdonalds.at/\?wpgb-ajax=render"
detail_url = "https://www.mcdonalds.at/wp-admin/admin-ajax.php?action=wpgb_map_facet_tooltip&id={}&source=post_type"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as http:
            driver.get(base_url)
            rr = driver.wait_for_request(json_url)
            data = json.loads(rr.response.body)
            locations = data["facets"]["19"]["geoJSON"]["features"]
            for _ in locations:
                sp1 = bs(
                    http.get(
                        detail_url.format(_["properties"]["id"]), headers=_headers
                    ).json()["content"],
                    "lxml",
                )
                page_url = sp1.select_one("a.wso-to-restaurant-button")["href"]
                logger.info(page_url)
                sp2 = bs(http.get(page_url, headers=_headers).text, "lxml")
                note = sp2.select_one("div.wso-restaurant-excerpt p")
                if note and "Restaurant wird im" in note.text:
                    continue

                addr = list(sp2.h1.stripped_strings)
                hours = []
                for hh in sp2.select("div#restaurants p"):
                    if not hh.text.strip():
                        continue
                    if "Drive" in hh.text:
                        break
                    hr = list(hh.stripped_strings)
                    if len(hr) > 2:
                        hr = hr[:-1]
                    hours.append(": ".join(hr))

                yield SgRecord(
                    page_url=page_url,
                    store_number=_["properties"]["id"],
                    street_address=addr[0].replace("\n", " "),
                    zip_postal=addr[1].split()[0],
                    city=addr[1].split()[-1],
                    country_code="Austria",
                    locator_domain=locator_domain,
                    latitude=_["geometry"]["coordinates"][1],
                    longitude=_["geometry"]["coordinates"][0],
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr).replace("\n", " "),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
