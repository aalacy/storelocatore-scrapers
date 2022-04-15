from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("roomstogokids_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.roomstogo.com/stores"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<div class="link-container"><a href="' in line:
            items = line.split('<div class="link-container"><a href="')
            for item in items:
                if "Rooms To Go Store Locator" not in item:
                    locs.append(
                        "https://www.roomstogo.com"
                        + item.split('"')[0]
                        .replace("&amp;hyphen;", "-")
                        .replace("&amp;", "&")
                    )
    for loc in locs:
        try:
            logger.info(("Pulling Location %s..." % loc))
            rs = session.get(loc, headers=headers)
            website = "roomstogo.com"
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            hours = ""
            country = "US"
            store = ""
            lat = ""
            lng = ""
            for line2 in rs.iter_lines():
                if '<link as="fetch" rel="preload" href="' in line2:
                    link = (
                        "https://www.roomstogo.com"
                        + line2.split('<link as="fetch" rel="preload" href="')[1].split(
                            '"'
                        )[0]
                    )
                    rl = session.get(link, headers=headers)
                    for line3 in rl.iter_lines():
                        if ',"StoreNumber":' in line3:
                            store = line3.split(',"StoreNumber":')[1].split(",")[0]
                            name = line3.split('"PageTitle":"')[1].split('"')[0]
                            phone = line3.split('"PhoneNumber":"')[1].split('"')[0]
                            typ = line3.split('"StoreType":"')[1].split('"')[0]
                            try:
                                lat = line3.split('"latitude\\": \\"')[1].split("\\")[0]
                            except:
                                try:
                                    lat = line3.split('"latitude":')[1].split(",")[0]
                                except:
                                    lat = "<MISSING>"
                            try:
                                lng = line3.split('"longitude\\": \\"')[1].split("\\")[
                                    0
                                ]
                            except:
                                try:
                                    lng = line3.split('"longitude":')[1].split("}")[0]
                                except:
                                    lng = "<MISSING>"
                            try:
                                add = line3.split('"streetAddress\\": \\"')[1].split(
                                    "\\"
                                )[0]
                            except:
                                add = line3.split('"Address1":"')[1].split('"')[0]
                            try:
                                city = line3.split('"addressLocality\\": \\"')[1].split(
                                    "\\"
                                )[0]
                            except:
                                city = line3.split('"City":"')[1].split('"')[0]
                            try:
                                state = line3.split('"addressRegion\\": \\"')[1].split(
                                    "\\"
                                )[0]
                            except:
                                state = line3.split('"State":"')[1].split('"')[0]
                            try:
                                zc = line3.split('"postalCode\\": \\"')[1].split("\\")[
                                    0
                                ]
                            except:
                                zc = line3.split('"Zip":"')[1].split('"')[0]
                            hours = (
                                "Mon: "
                                + line3.split('"mondayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"mondayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Tue: "
                                + line3.split('"tuesdayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"tuesdayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Wed: "
                                + line3.split('"wednesdayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"wednesdayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Thu: "
                                + line3.split('"thursdayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"thursdayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Fri: "
                                + line3.split('"fridayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"fridayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sat: "
                                + line3.split('"saturdayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"saturdayClosed":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sun: "
                                + line3.split('"sundayOpen":"')[1].split('"')[0]
                                + "-"
                                + line3.split('"sundayClosed":"')[1].split('"')[0]
                            )
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


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
