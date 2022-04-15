from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.vw.ca/app/dccsearch/vw-ca/en/Volkswagen%20Dealer%20Search/+/49.87951181643615/-97.1759382/12/+/+/+/+"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "%5C%22address%5C%22:" in line:
            items = line.split("%5C%22address%5C%22:")
            for item in items:
                if "%5C%22city%5C%22:%5C%22" in item:
                    website = "vw.ca"
                    typ = "<MISSING>"
                    country = "CA"
                    store = "<MISSING>"
                    name = (
                        item.split("5C%22name%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    add = (
                        item.split("%5C%22street%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    city = (
                        item.split("%5C%22city%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    state = (
                        item.split("%5C%22province%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    zc = (
                        item.split("%5C%22postalCode%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    phone = (
                        item.split("%5C%22phoneNumber%5C%22:%5C%22")[1]
                        .split("%5C")[0]
                        .replace("%20", " ")
                    )
                    lat = item.split("%5C%22coordinates%5C%22:%5B")[1].split(",")[0]
                    lng = (
                        item.split("%5C%22coordinates%5C%22:%5B")[1]
                        .split(",")[1]
                        .split("%")[0]
                    )
                    hours = "<MISSING>"
                    loc = "https://www.vw.ca/app/dccsearch/vw-ca/en/Volkswagen%20Dealer%20Search/+/54.44073635000004/-93.75185435/3/+/+/+/+"
                    add = (
                        add.replace("%C3%A8", "e")
                        .replace("%C3%A9", "e")
                        .replace("%C3%B4", "o")
                    )
                    city = (
                        city.replace("%C3%A8", "e")
                        .replace("%C3%A9", "e")
                        .replace("%C3%B4", "o")
                    )
                    name = (
                        name.replace("%C3%A8", "e")
                        .replace("%C3%A9", "e")
                        .replace("%C3%B4", "o")
                    )
                    if "x-store/consumer-configs" not in name:
                        yield SgRecord(
                            locator_domain=website,
                            page_url=loc,
                            location_name=name,
                            street_address=add,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code=country,
                            phone=phone,
                            location_type=typ,
                            store_number=store,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
