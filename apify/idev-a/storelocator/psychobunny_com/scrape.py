from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("psychobunny")
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.psychobunny.com"
    base_url = "https://www.psychobunny.com/apps/store-locator?gclid=CjwKCAjwnPOEBhA0EiwA609ReUyQ0DPxR3Ab2dk3t_bjLpoRIyzAgymt9uxTCFk5Iw-KDai_MuVkhBoCRh0QAvD_BwE&gclsrc=aw.ds"
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
            json_url = f"https://stores.boldapps.net/front-end/get_store_info.php?shop=psychobunny-com.myshopify.com&data=detailed&store_id={_['id']}&tm=2021-04-30%2010:13:06-17"
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
            country_code = ""
            if data.select_one(".country"):
                country_code = data.select_one(".country").text.strip()
            elif phone.startswith("+82"):
                country_code = "Korea"
            street = data.select_one(".address").text.strip()
            addr = parse_address_intl(data.select_one(".address").text.strip())
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.isdigit():
                street_address = street
            if not state and addr.state:
                state = addr.state
            if not zip_postal and addr.postcode:
                zip_postal = addr.postcode
            location_type = ""
            if _["marker_colour"] == "map-pin-pink":
                location_type = "store"
            elif _["marker_colour"] == "map-pin-black":
                location_type = "outlet"
            elif _["marker_colour"] == "map-pin-grey":
                location_type = "retailer"
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=data.select_one(".name").text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                latitude=_["lat"],
                longitude=_["lng"],
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
