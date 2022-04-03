from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lavieenrose")

locator_domain = "https://www.lavieenrose.com"
base_url = "https://www.lavieenrose.com/en/our-stores"
search_url = "https://www.lavieenrose.com/en/our-stores/SearchStores"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.lavieenrose.com",
    "referer": "https://www.lavieenrose.com/en/our-stores?searchByAddress=9001%20Boulevard%20de%20l%27Acadie,%20Montreal,%20QC,%20Canada&lat=45.5328668&lng=-73.65399359999999&cntry=Canada",
    "request-context": "appId=cid-v1:62b7f8c6-4228-486f-98ac-18fc26135294",
    "request-id": "|wV7Jw.8LJM2",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as http:
        sp0 = bs(http.get(base_url, headers=_headers).text, "lxml")
        data = {
            "searchByAddress": "9001 Boulevard de l'Acadie, Montreal, QC, Canada",
            "userLat": "",
            "userLng": "",
            "addressModel[Country]": "Canada",
            "addressModel[Latitude]": "45.5328668",
            "addressModel[Longitude]": "-73.65399359999999",
        }
        data["__RequestVerificationToken"] = sp0.select_one(
            'input[name="__RequestVerificationToken"]'
        )["value"]
        locations = bs(
            http.post(search_url, headers=header1, data=data).text, "lxml"
        ).select("div.js-store-tile")
        for _ in locations:
            location_type = "outlets"
            if (
                "boutique"
                in _.select_one("div.tmx-store-tile-index img")["data-src"].lower()
            ):
                location_type = "boutique"
            page_url = _.select_one("div.direction-container div a")["href"]
            logger.info(page_url)
            sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select("div.js-container-details-0")[0].select("div.row"):
                div = list(hh.stripped_strings)
                hours.append(f"{div[0]}: {div[1]} - {div[2]}")
            _addr = list(sp1.select_one("div.tmx-store-address span").stripped_strings)
            info = _.select_one("div.favorite-store-icon-container div")
            raw_address = _.select_one("div.direction-container a.store-link")[
                "data-address"
            ].replace("+", ",")
            addr = raw_address.split(",")
            yield SgRecord(
                page_url=page_url,
                store_number=info["id"],
                location_name=_.select_one("div.store-title").text.strip(),
                street_address=" ".join(addr[:-3]),
                city=addr[-3],
                state=addr[-2],
                zip_postal=_addr[1].split()[-1],
                latitude=info["data-lat"],
                longitude=info["data-lng"],
                country_code=addr[-1],
                phone=_p(_.select_one("a.store-link").text.strip()),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                location_type=location_type,
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
