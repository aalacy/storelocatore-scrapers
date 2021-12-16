from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("makro")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.nl/"
urls = {
    "Netherlands": "https://www.makro.nl//sxa/search/results/?l=nl-NL&s={0F3B38A3-7330-4544-B95B-81FC80A6BB6F}&itemid={8C6E428A-ECF3-4108-8A37-65D16E891E77}&sig=store-locator&g=&p=20&o=StoreName%2CAscending&v=%7BA0897F25-35F9-47F8-A28F-94814E5A0A78%7D",
    "Spain": "https://www.makro.es//sxa/search/results/?l=es-ES&itemid={6C3F44FA-FD60-4712-9094-141795AFFA2B}&sig=store-locator&g=&p=999&v=%7BA0897F25-35F9-47F8-A28F-94814E5A0A78%7D",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()["Results"]
            for _ in locations:
                info = bs(_["Html"], "lxml")
                raw_address = info.select_one("div.field-address").text.strip()
                street_address = city = state = zip_postal = ""
                addr = [aa.strip() for aa in raw_address.split(",")]
                zip_postal = addr[-1]

                page_url = _["Url"].split("/")[-1]
                if country == "Spain":
                    page_url = f"https://www.makro.es/tiendas/{page_url}"
                    city = addr[-2]
                    street_address = ", ".join(addr[:-2])
                else:
                    page_url = f"https://www.makro.nl/vestigingen/{page_url}"
                    c_idx = -3
                    if len(addr) > 3 and addr[-2] not in ["Utrecht", "Groningen"]:
                        state = addr[-2]
                    else:
                        c_idx += 1
                    city = addr[c_idx]
                    street_address = ", ".join(addr[:c_idx])

                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = []
                if sp1.select("div.store-opening-container > div"):
                    days = list(
                        sp1.select_one(
                            "div.store-opening-container div.days-container"
                        ).stripped_strings
                    )
                    times = list(
                        sp1.select_one(
                            "div.store-opening-container div.time-container"
                        ).stripped_strings
                    )
                    for x in range(len(days)):
                        hours.append(f"{days[x]}: {times[x]}")
                yield SgRecord(
                    page_url=page_url,
                    location_name=info.select_one("div.field-store-name").text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["Geospatial"]["Latitude"],
                    longitude=_["Geospatial"]["Longitude"],
                    country_code=country,
                    phone=list(sp1.select_one("a.store-phone").stripped_strings)[-1],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
