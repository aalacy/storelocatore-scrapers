from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cottonon")

_headers = {
    "accept": "text/plain, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://cottonon.com",
    "referer": "https://cottonon.com/US/store-finder/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _data(token):
    return {
        "dwfrm_storelocator_brandsInStore": "CottonOn,CottonOnBody,RubiShoes,CottonOnKids,Typo",
        "dwfrm_storelocator_country": "US",
        "dwfrm_storelocator_textfield": "",
        "csrf_token": token,
        "format": "ajax",
        "lat": "37.09024",
        "lng": "-95.712891",
        "dwfrm_storelocator_findByLocation": "x",
    }


def fetch_data():
    locator_domain = "https://cottonon.com/"
    base_url = "https://cottonon.com/US/store-finder/"
    store_url = "https://cottonon.com/on/demandware.store/Sites-cog-us-Site/en_US/Stores-FindStores"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        token = soup.select_one("input[name='csrf_token']")["value"]
        sp1 = bs(
            session.post(store_url, headers=_headers, data=_data(token)).text, "lxml"
        )
        locations = sp1.select("div.store-details")
        logger.info(f"[total] {len(locations)} found")
        for _ in locations:
            hours = []
            for hh in _.select("div.opening-hours .store-hours"):
                time = hh.select("div")[1].text.strip()
                if time == "-":
                    time = "Closed"
                hours.append(f"{hh.select('div')[0].text.strip()} {time}")
            coord = _.select_one("a.view-map-link")["href"].split("?q=")[1].split(",")
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-id"],
                location_name=_.select_one("h2.store-name").text.strip(),
                street_address=_.select_one("div.store-address1").text.strip(),
                city=_.select_one("div.store-city").text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=_.select_one("div.store-postalCode").text.strip(),
                country_code=_.select_one("div.store-countryCodeValue").text.strip(),
                phone=_.select_one("div.store-phone").text.split(":")[-1].strip(),
                locator_domain=locator_domain,
                location_type=_.select_one("div.store-brand").text.strip(),
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
