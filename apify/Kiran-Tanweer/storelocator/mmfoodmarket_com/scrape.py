from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import json


session = SgRequests()
website = "mmfoodmarket_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Cookie": "analytics_session=true; _gcl_au=1.1.327023937.1637854042; ABTasty=uid=yxtcpyram8vhsj47&fst=1637854042067&pst=1637860016399&cst=1643461523582&ns=3&pvt=26&pvis=7&th=795149.0.5.5.1.1.1643461574199.1643463931542.1; _ga_MHHPDZZE1M=GS1.1.1637881102.4.0.1637881102.0; _ga=GA1.2.375507378.1637854042; _mm_food_market_session=eGgyX7BCzi91xbFTVgyzuQdkJy7C0F5K7FSnc9jdobcpXAAwO7y7aH3cNOhvhUzLRvTZSdhxRDTQeuuLk%2FCcx7b0XyF%2FRX7xmiqkQOk6M8gq6mHRg4VpOVF2UCqoTgjKz3M8Mb8BS9Lox41vicvPeA99UkG3Jtf6TtR8dwWT7t%2Bc2aEpXMYjuqUhWoR%2BgpJF9WsMZb%2BD19zdhvluI8jNGbA25sI7UZHPCsyReGWTx7UR9lnXha5rjxPm68cdZK0XweSMywaSGPX5wGXULoHf1yJhO7Ybkyz7ag%3D%3D--YB8hsb%2Fp8Mo4%2BuIZ--mc57LK7r%2Br7tmEpeVu7Zqw%3D%3D; default_store_id=; price_region=; rsci_vid=e72c44b5-c622-5d52-c79d-23b341244701; _fbp=fb.1.1637854044673.1709124546; _hjSessionUser_2250455=eyJpZCI6IjU0NjAyYWIzLWEyYmEtNTg2NS05NjIyLTg2YTMxNGU1YmY4OCIsImNyZWF0ZWQiOjE2Mzc4NTQwNDQ0OTQsImV4aXN0aW5nIjp0cnVlfQ==; _uetvid=2fe24e104e0411ecb417b59e7542b23c; ABTastySession=mrasn=&sen=11&lp=https%253A%252F%252Fmmfoodmarket.com%252F; _mm_food_market_session=Gg%2F6G0OmfmLr0Gx1oJIl9FD5epP%2FyrazJcau3WlLpSQPjhf%2Frmg7OAqNy5FZo1I3KSS72gJh3XjV3VGN2pgAJDwFBECRPBLa%2BHsJgy6quMhtjwUOcOzcJEUZ8tMLYvdj6Tao0a6DwYBRt6sMEVQ8J7PQkPrQl9rTxqf1Czhu0eTGBJGrkxyWycB5it3WIPXV4StfmRozHES1MuwOo%2BFp4sEOa0U%2BKODVlu3wGw%2FYTr%2Bqup9Y4DAipoUj0ru7bDDz0J6vLo8kMtZo86KTW%2Fo3RUdmvpXr9SrYPA%3D%3D--9tyquG6KrQE7wFQC--%2FwKuq02pxCyVlYF6nbcGpQ%3D%3D; default_store_id=; price_region="
}
headers1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
DOMAIN = "https://mmfoodmarket.com/en/store-locator"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicZipSearch(
            country_codes=[
                SearchableCountries.CANADA,
            ]
        )
        for key in search:
            url = "https://mmfoodmarket.com/en/store_locations?address=" + key
            r = session.get(url, headers=headers)
            try:
                soup = BeautifulSoup(r.text, "html.parser")
            except AttributeError:
                continue
            loc_card = soup.find("div", {"class": "store-results"})
            if len(loc_card) != 3:
                type_check = loc_card.find("h3", {"class": "store-results__heading"})
                if type_check.find("traditional") != -1:
                    store_list = loc_card.find(
                        "ul", {"class": "store-results__list"}
                    ).findAll("li", {"class": "store-results__list-item"})
                    for stores in store_list:
                        script = stores.find("script")
                        script = str(script)
                        script = script.lstrip('<script type="application/ld+json">')
                        script = script.rstrip("</script>")
                        script = script.strip()
                        script = json.loads(script)
                        title = script["name"]
                        link = script["url"]
                        address = script["address"]
                        phone = script["telephone"]
                        city = address["addressLocality"]
                        state = address["addressRegion"]
                        street = (
                            script["hasMap"]
                            .split("dir//")[1]
                            .split(city)[0]
                            .replace("+", " ")
                            .strip()
                        )
                        street = street.replace("%2C", ",")
                        storeid = link.split("store_id=")[1].strip()
                        link = "https://mmfoodmarket.com/en/store_locations/" + storeid
                        pcode = (
                            script["hasMap"].split(state)[1].replace("+", "").strip()
                        )
                        req = session.get(link, headers=headers1)
                        try:
                            bs = BeautifulSoup(req.text, "html.parser")
                        except AttributeError:
                            continue
                        address = bs.find(
                            "p", {"class": "store__detail store__detail--address"}
                        )
                        address = str(address)
                        address = address.replace(
                            '<p class="store__detail store__detail--address">', ""
                        ).strip()
                        address = address.replace("</p>", "").strip()
                        strt = address.split("<br/>", 2)[1]
                        hours = bs.findAll("p", {"class": "store-hours__day"})
                        hoo = ""
                        for hr in hours:
                            hoo = hr.text.replace("day", "day ") + " " + hoo
                        hoo = hoo.replace("\n", "").strip()

                        coords = bs.find(
                            "div",
                            {
                                "class": "store-results__map store-results__map--location"
                            },
                        )["data-google-map"]
                        coords = json.loads(coords)
                        coords = coords["points"][0]["coordinates"]
                        lat = coords[0]
                        lng = coords[1]

                        street = street.replace("%23", "#")

                        pcode = pcode.replace("-2A%231Lacombe", "T4L1Y8")

                        title = title.strip()

                        if (
                            title == "Core-Mark-Powell River-Joyce Ave"
                            or title == "Core-Mark-Ardmore-AB-892"
                            or title == "Core-Mark-Grand Bend-Bluewater Hwy"
                            or title == "Capital Foodservice-Parrsboro-Main Street"
                            or title == "Core-Mark-Keremeos-Hwy 3A"
                            or title == "Core-Mark-Lone Butte-BC-24"
                        ):

                            loc_type = "Express"
                        else:
                            loc_type = "Traditioal"
                            yield SgRecord(
                                locator_domain=DOMAIN,
                                page_url=link,
                                location_name=title,
                                street_address=strt,
                                city=city,
                                state=state,
                                zip_postal=pcode,
                                country_code="CAN",
                                store_number=storeid,
                                phone=phone,
                                location_type=loc_type,
                                latitude=lat,
                                longitude=lng,
                                hours_of_operation=hoo,
                            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
