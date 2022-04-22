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
    url = "https://www.anytimefitness.com/wp-content/uploads/locations.json"
    r = session.get(url, headers=headers, stream=True)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"latitude":"' in line:
            items = line.split('"latitude":"')
            for item in items:
                if (
                    '"country":"US"' in item
                    or '"country":"CA"' in item
                    or '"country":"GB"' in item
                ):
                    if '"status":"3"' in item:
                        lat = item.split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        website = "anytimefitness.com"
                        hours = "Open 24 Hours"
                        name = item.split('"title":"')[1].split('"')[0]
                        typ = "<MISSING>"
                        loc = item.split('"url":"')[1].split('"')[0].replace("\\/", "/")
                        add = item.split('"address":"')[1].split('"')[0]
                        if '"address2":"' in item:
                            add = (
                                add + " " + item.split('"address2":"')[1].split('"')[0]
                            )
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state_abbr":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phone":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        store = item.split('"number":"')[1].split('"')[0]
                        if country == "US" or country == "CA" or country == "GB":
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
