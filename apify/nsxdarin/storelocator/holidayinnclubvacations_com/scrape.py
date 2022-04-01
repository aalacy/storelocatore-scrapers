from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("holidayinnclubvacations_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    for x in range(1, 4):
        url = "https://holidayinnclub.com/api/resorts?page=" + str(x)
        r = session.get(url, headers=headers)
        website = "holidayinnclubvacations.com"
        country = "US"
        typ = "Hotel"
        hours = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        for line in r.iter_lines():
            if '"contentTypeUID":"' in line:
                items = line.split('"contentTypeUID":"')
                for item in items:
                    if ',"items":[' not in item:
                        name = item.split('"displayTitle":"')[1].split('"')[0]
                        loc = (
                            "https://holidayinnclub.com/explore-resorts/"
                            + item.split(',"resortSlugs":"')[1].split('"')[0]
                        )
                        phone = item.split('{"phoneNumber":"')[1].split('"')[0]
                        add = item.split('"address":"')[1].split("\\n")[0]
                        city = item.split('"destination":{"displayTitle":"')[1].split(
                            ","
                        )[0]
                        state = (
                            item.split('"destination":{"displayTitle":"')[1]
                            .split(",")[1]
                            .split('"')[0]
                            .strip()
                        )
                        zc = (
                            item.split('"address":"')[1].split('"')[0].rsplit(" ", 1)[1]
                        )
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split("}")[0]
                        store = "<MISSING>"
                        if "Apple Mountain Resort" in name:
                            city = "Clarkesville"
                            state = "Georgia"
                        if "Coming Soon" not in item:
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
