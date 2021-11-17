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
    "Netherlands": "https://www.makro.nl/sxa/search/results?s={0F3B38A3-7330-4544-B95B-81FC80A6BB6F}&sig=store-locator&o=Title%2CAscending&p=10&v=%7BBECE07BD-19B3-4E41-9C8F-E9D9EC85574F%7D&itemid=752b4b0d-8883-42d9-b50a-71c53db9b093&q=&g=",
    "Spain": "https://www.makro.es/sxa/search/results?s={0F3B38A3-7330-4544-B95B-81FC80A6BB6F}&sig=store-locator&o=Title%2CAscending&p=10&v=%7BBECE07BD-19B3-4E41-9C8F-E9D9EC85574F%7D&itemid=fe9e4172-0717-4da3-aa16-e516843fb14b&q=&g=",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()["Results"]
            for _ in locations:
                info = bs(_["Html"], "lxml")
                raw_address = info.select_one("div.field-address").text.strip()
                street_address = city = state = zip_postal = ""
                addr = raw_address.split(",")
                zip_postal = addr[-1]

                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in info.select("div.hours-details > div")[0].select(
                        "div.day"
                    )
                ]
                page_url = _["Url"].split("/")[-1]
                if country == "Spain":
                    page_url = f"https://www.makro.es/tiendas/{page_url}"
                    city = addr[-2]
                    street_address = ", ".join(addr[:-2])
                else:
                    page_url = f"https://www.makro.nl/vestigingen/{page_url}"
                    state = addr[-2]
                    city = addr[-3]
                    street_address = ", ".join(addr[:-3])

                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                yield SgRecord(
                    page_url=page_url,
                    location_name=info.select_one("span.field-store-name").text.strip(),
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
