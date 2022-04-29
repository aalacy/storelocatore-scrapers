from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("michaelkors_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):
    locs = []
    found = []
    url = "https://locations.michaelkors.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://locations.michaelkors.com/" in line and "/fr_ca/" not in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 6:
                locs.append(lurl)
    url = "https://locations.michaelkors.ca/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://locations.michaelkors.ca/" in line and "/fr_ca/" not in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 5:
                locs.append(lurl)
    url = "https://locations.michaelkors.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://locations.michaelkors.co.uk/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") > 3:
                locs.append(lurl)
    logger.info(len(locs))
    for loc in locs:
        print(loc)
        website = "michaelkors.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        country = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        if "locations.michaelkors.ca" in loc:
            country = "CA"
        elif "locations.michaelkors.co.uk" in loc:
            country = "GB"
        else:
            country = loc.split("com/")[1].split("/")[0].replace("-", " ").upper()
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        store = "<MISSING>"
        HFound = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<span class="Heading-sub Heading--pre">' in line2:
                typ = line2.split('<span class="Heading-sub Heading--pre">')[1].split(
                    "<"
                )[0]
                name = (
                    typ
                    + " "
                    + line2.split('span class="Heading-main">')[1].split("<")[0]
                )
            if '"dimension4":"' in line2:
                try:
                    country = line2.split('temprop="address" data-country="')[1].split(
                        '"'
                    )[0]
                except:
                    pass
                add = (
                    line2.split('"dimension4":"')[1]
                    .split('"')[0]
                    .replace("\u0026", "&")
                    .replace("\\", "")
                    .split(". Santiago")[0]
                    .strip()
                )
                zc = line2.split('"dimension5":"')[1].split('"')[0]
                city = line2.split('"dimension3":"')[1].split('"')[0]
                state = line2.split('"dimension2":"')[1].split('"')[0]
            if 'data-ya-track="phonecall">' in line2:
                phone = line2.split('data-ya-track="phonecall">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if HFound is False and "data-days='[{" in line2:
                HFound = True
                days = line2.split("data-days='[{")[1].split("]}]")[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            try:
                                shr = day.split('"start":')[1].split("}")[0]
                                ehr = day.split('"end":')[1].split(",")[0]
                                if ehr == "0":
                                    ehr = "2400"
                                if len(shr) == 3:
                                    shr = "0" + shr
                                if len(ehr) == 3:
                                    ehr = "0" + ehr
                                shr = shr[0:2] + ":" + shr[-2:]
                                ehr = ehr[0:2] + ":" + ehr[-2:]
                                hrs = day.split('"')[0] + ": " + shr + "-" + ehr
                            except:
                                hrs = day.split('"')[0] + ": Closed"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if name + add in found:
            continue
        found.append(name + add)

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
