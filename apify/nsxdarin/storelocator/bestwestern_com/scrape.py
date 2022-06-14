from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("bestwestern_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.bestwestern.com/etc/seo/bestwestern/hotels.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if (
            "<loc>https://www.bestwestern.com/en_US/book/" in line
            and "https://www.bestwestern.com/en_US/book/hotels-in-" not in line
            and "/propertyCode." in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl not in locs:
                locs.append(lurl)
    logger.info(("Found %s Locations..." % str(len(locs))))
    for loc in locs:
        PageFound = True
        time.sleep(1)
        logger.info("Pulling Location %s..." % loc)
        website = "bestwestern.com"
        typ = "<MISSING>"
        hours = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = ""
        store = loc.split("/propertyCode.")[1].split(".")[0]
        phone = ""
        lat = ""
        lng = ""
        while PageFound:
            try:
                PageFound = False
                r2 = session.get(loc, headers=headers)
                try:
                    for line2 in r2.iter_lines():
                        if "&#34;street1&#34;:&#34;" in line2:
                            add = line2.split("&#34;street1&#34;:&#34;")[1].split(
                                "&#34"
                            )[0]
                            city = line2.split("&#34;city&#34;:&#34;")[1].split("&#34")[
                                0
                            ]
                            try:
                                state = line2.split("&#34;state&#34;:&#34;")[1].split(
                                    "&#34"
                                )[0]
                            except:
                                state = "<MISSING>"
                            country = line2.split("&#34;country&#34;:&#34;")[1].split(
                                "&#34"
                            )[0]
                            try:
                                zc = line2.split("&#34;postalcode&#34;:&#34;")[1].split(
                                    "&#34"
                                )[0]
                            except:
                                zc = "<MISSING>"
                            try:
                                phone = line2.split("&#34;phoneNumber&#34;:&#34;")[
                                    1
                                ].split("&#34")[0]
                            except:
                                phone = "<MISSING>"
                            lat = line2.split("&#34;,&#34;latitude&#34;:&#34;")[
                                1
                            ].split("&#34")[0]
                            lng = line2.split("&#34;longitude&#34;:&#34;")[1].split(
                                "&#34"
                            )[0]
                            name = (
                                line2.split("&#34;name&#34;:&#34;")[1]
                                .split("&#34")[0]
                                .replace("\\u0026", "&")
                            )
                            if "United States" in country:
                                country = "US"
                            if "Canada" in country:
                                country = "CA"
                            if country == "US":
                                zc = zc[:5]
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
                except:
                    pass
            except:
                PageFound = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
