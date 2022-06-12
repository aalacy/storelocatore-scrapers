from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tiptop")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.tiptop.ca"
    base_url = "https://www.tiptop.ca/apps/store-finder"
    with SgRequests() as session:
        locations = (
            session.get(base_url, headers=_headers)
            .text.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#039;", '"')
            .replace("&quot;", '"')
            .split("markersCoords.push(")[1:-2]
        )
        for loc in locations:
            _ = json.loads(loc.split(");")[0])
            json_url = f"https://stores.boldapps.net/front-end/get_store_info.php?shop=tiptop-storefront.myshopify.com&data=detailed&store_id={_['id']}&tm=2021-07-05%2011:51:12-26"
            data = bs(session.get(json_url, headers=_headers).json()["data"], "lxml")
            logger.info(json_url)
            hours = []
            if data.select_one(".hours"):
                temp = data.select_one(".hours").stripped_strings
                for hh in temp:
                    if "christmas" in hh.lower() or "holiday" in hh.lower():
                        break
                    hours.append(hh.replace('"', ""))
            phone = ""
            if data.select_one(".phone"):
                phone = data.select_one(".phone").text.strip()
            state = ""
            if data.select_one(".prov_state"):
                state = data.select_one(".prov_state").text.strip()
            city = ""
            if data.select_one(".city"):
                city = data.select_one(".city").text.strip()
            zip_postal = ""
            if data.select_one(".postal_zip"):
                zip_postal = data.select_one(".postal_zip").text.strip()
            street_address = data.select_one(".address").text.strip()
            if data.select_one(".address2"):
                street_address += " " + data.select_one(".address2").text.strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=data.select_one(".name").text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                latitude=_["lat"],
                longitude=_["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
