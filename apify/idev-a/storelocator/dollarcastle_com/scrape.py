from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
import dirtyjson

logger = SgLogSetup().get_logger("dollarcastle")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_header1 = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "origin": "https://dollarcastle.com",
    "referer": "https://dollarcastle.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _coord(locations, name):
    for loc in locations:
        if bs(loc["address"], "lxml").select_one(".name").text.strip() == name:
            return loc["lat"], loc["lng"]
    return ("", "")


def fetch_data():
    locator_domain = "https://dollarcastle.com/"
    base_url = "https://dollarcastle.com/apps/store-locator"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#addresses_list ul li")
        logger.info(f"{len(links)} links found")
        script = soup.find(
            "script", string=re.compile(r"var markersCoords")
        ).string.strip()
        locations = []
        for ss in script.split("markersCoords.push(")[1:-2]:
            locations.append(
                dirtyjson.loads(
                    ss.split(");")[0]
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&#039;", '"')
                )
            )
        logger.info(f"{len(locations)} locations found")
        for link in links:
            store_number = link["onmouseover"].split("(")[1].split(")")[0]
            json_url = f"https://stores.boldapps.net/front-end/get_store_info.php?shop=dollar-castle.myshopify.com&data=detailed&store_id={store_number}&tm=2017-10-24%2009:51:27-25"
            _ = bs(session.get(json_url, headers=_header1).json()["data"], "lxml")
            location_name = _.select_one(".name").text.strip()
            coord = _coord(locations, location_name)
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=_.select_one(".address").text.strip(),
                city=_.select_one(".city").text.strip(),
                state=_.select_one(".prov_state").text.strip(),
                zip_postal=_.select_one(".postal_zip").text.strip(),
                country_code=_.select_one(".country").text.strip(),
                phone=_.select_one(".phone").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(
                    _.select_one(".hours").stripped_strings
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
