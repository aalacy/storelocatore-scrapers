from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("providence_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def fetch_data():
    country = "US"
    url = "https://www.providence.org/locations"
    payload = "scController=LocationSearch&scAction=PerformLocationSearch&site=socal"
    website = "providence.org"
    typ = "<MISSING>"
    store = "<MISSING>"
    for x in range(1, 300):
        logger.info(x)
        querystring = querystring = {
            "postal": "",
            "latlng": "45.49,-122.77",
            "page": str(x),
            "radius": 20000,
        }
        r = session.post(url, data=payload, headers=headers, params=querystring)
        for line in r.iter_lines():
            if "data-lat=" in line:
                items = line.split("data-lat=")
                for item in items:
                    if "data-lng=\\" in item:
                        lat = item.split('\\"')[1].split("\\")[0]
                        lng = item.split('data-lng=\\"')[1].split("\\")[0]
                        name = item.split('data-name=\\"')[1].split("\\")[0]
                        add = item.split('data-address=\\"')[1].split("\\")[0]
                        phone = item.split('data-main-phone=\\"')[1].split("\\")[0]
                        lurl = (
                            "https://www.providence.org"
                            + item.split("ocation-index")[1]
                            .split('href=\\"')[1]
                            .split("\\")[0]
                        )
                        try:
                            csz = item.split("\\u003cdiv\\u003e")[2].split("\\")[0]
                            city = csz.split(",")[0]
                            zc = csz.rsplit(" ", 1)[1]
                            state = csz.split(",")[1].strip().rsplit(" ", 1)[0]
                        except:
                            city = "<MISSING>"
                            state = "<MISSING>"
                            zc = "<MISSING>"
                        hours = "<INACCESSIBLE>"
                        lurl = lurl.replace(
                            "https://www.providence.orghttps://www.swedish.org/",
                            "https://www.swedish.org/",
                        )
                        lurl = lurl.replace("https://www.providence.orghttps", "https")
                        yield SgRecord(
                            locator_domain=website,
                            page_url=lurl,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
