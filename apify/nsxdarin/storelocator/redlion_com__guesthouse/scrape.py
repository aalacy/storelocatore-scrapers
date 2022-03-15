from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):
    url = "https://www.redlion.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line)
        if "<loc>https://www.redlion.com/guesthouse" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") > 3:
                locs.append(lurl)
    for loc in locs:
        loc2 = (
            loc.replace("www.redlion.com/", "www.redlion.com/page-data/")
            + "/page-data.json"
        )
        r2 = session.get(loc2, headers=headers)
        website = "https://www.redlion.com/"
        for line2 in r2.iter_lines():
            line2 = str(line2)
            if '{"hotel":{"name":"' in line2:
                name = line2.split('{"hotel":{"name":"')[1].split('"')[0]
                country = line2.split('"country_code":"')[1].split('"')[0]
                try:
                    store = line2.split('"crs_code":"')[1].split('"')[0]
                except:
                    store = ""
                phone = line2.split('"phone":"')[1].split('"')[0]
                add = line2.split('"address_line1":"')[1].split('"')[0]
                city = line2.split('"locality":"')[1].split('"')[0]
                state = line2.split('"administrative_area":"')[1].split('"')[0]
                zc = line2.split('"postal_code":"')[1].split('"')[0]
                lat = line2.split('{"lat":')[1].split(",")[0]
                lng = line2.split('"lon":')[1].split("}")[0]
                hours = ""
                typ = ""

                sgw.write_row(
                    SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        store_number=store,
                        phone=phone,
                        location_type=typ,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
