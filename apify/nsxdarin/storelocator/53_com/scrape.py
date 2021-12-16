from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):
    locs = []
    url = "https://locations.53.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://locations.53.com/" in line:
            lurl = line.split(">")[1].split("<")[0]
            count = lurl.count("/")
            if count >= 5:
                locs.append(lurl)
    for loc in locs:
        website = "53.com"
        typ = "Branch"
        name = ""
        add = ""
        city = ""
        state = ""
        phone = ""
        zc = ""
        lat = ""
        lng = ""
        country = "US"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<span class="LocationName"' in line2:
                name = (
                    line2.split('<span class="LocationName-brand">')[1]
                    .split("</span></span>")[0]
                    .replace('</span> <span class="LocationName-geo">', " ")
                )
                if "<" in name:
                    name = name.split("<")[0]
                typ = line2.split('<div class="CoreHero-type Text--bold">')[1].split(
                    "<"
                )[0]
                add = line2.split("c-address-street-1")[1].split('">')[1].split("<")[0]
                city = (
                    line2.split('class="c-address-city')[1].split('">')[1].split("<")[0]
                )
                state = line2.split('"c-address-state')[1].split(">")[1].split("<")[0]
                zc = (
                    line2.split(' class="c-address-postal-code')[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
                phone = (
                    line2.split('href="tel:')[1]
                    .split('">')[1]
                    .split("<")[0]
                    .replace("Call", "")
                    .strip()
                )
                days = (
                    line2.split("data-days='")[1].split("}]' data")[0].split('"day":"')
                )
                if '"intervals"' not in line2.split("data-days='")[1].split("}]' data")[
                    0
                ].split('"day":"'):
                    days = (
                        line2.split("data-days='")[2]
                        .split("}]' data")[0]
                        .split('"day":"')
                    )
                for day in days:
                    if '"intervals"' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                lat = line2.split('latitude" content')[1].split('"')[1].split('"')[0]
                lng = line2.split('longitude" content')[1].split('"')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        store = "<MISSING>"
        add = add.replace("[{: Closed;", "").strip()

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
