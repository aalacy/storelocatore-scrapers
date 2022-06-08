from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


@retry(stop=stop_after_attempt(7))
def fetch_loc(loc):
    return session.get(loc, headers=headers)


def fetch_data():
    locs = []
    url = "https://www.costco.ca/sitemap_l_001.xml"
    r = session.get(url, headers=headers)
    for raw_line in r.iter_lines():
        line = str(raw_line)
        if "<loc>https://www.costco.ca/warehouse-locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        website = "costco.ca/gasoline.html"
        typ = "Gas"
        hours = ""
        phone = "<MISSING>"
        add = "<MISSING>"
        city = "<MISSING>"
        zc = "<MISSING>"
        state = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        store = "<MISSING>"
        name = "<MISSING>"
        country = "CA"
        HFound = False
        IsGas = False
        r2 = fetch_loc(loc)
        lines = r2.iter_lines()
        for raw_line2 in lines:
            line2 = str(raw_line2)
            if "Gas Hours</span>" in line2:
                IsGas = True
                HFound = True
            if HFound and '<div class="panel panel-default">' in line2:
                HFound = False
            if HFound and 'itemprop="openingHours" datetime="' in line2:
                hrs = line2.split('itemprop="openingHours" datetime="')[1].split('"')[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'data-identifier="' in line2:
                store = line2.split('data-identifier="')[1].split('"')[0]
            if '<h1 itemprop="name">' in line2:
                name = (
                    line2.split('<h1 itemprop="name">')[1]
                    .split("<")[0]
                    .replace("&nbsp;", " ")
                )
            if 'itemprop="streetAddress"' in line2:
                add = (
                    line2.split('itemprop="streetAddress"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if 'itemprop="addressLocality"' in line2:
                city = (
                    line2.split('itemprop="addressLocality"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if 'itemprop="addressRegion"' in line2:
                state = (
                    line2.split('itemprop="addressRegion"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if 'itemprop="postalCode"' in line2:
                zc = line2.split('itemprop="postalCode"')[1].split(">")[1].split("<")[0]
            if phone == "<MISSING>" and 'itemprop="telephone">' in line2:
                phone = (
                    line2.split('itemprop="telephone">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("\t", "")
                )
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if add != "" and IsGas is True:
            if "; Lab" in hours:
                hours = hours.split("; Lab")[0].strip()
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
