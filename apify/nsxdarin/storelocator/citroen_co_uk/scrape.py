from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("citroen_co_uk")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.citroen.co.uk/apps/atomic/DealersServlet?distance=300&latitude=55.378051&longitude=-3.435973&maxResults=500&path=L2NvbnRlbnQvY2l0cm9lbi93b3JsZHdpZGUvdWsvZW4%3D&searchType=latlong"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '{"siteGeo":"' in line:
            items = line.split('{"siteGeo":"')
            for item in items:
                if '"dealerUrl":"' in item:
                    stub = item.split('"dealerUrl":"')[1].split('"')[0]
                    locs.append(stub)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        website = "citroen.co.uk"
        city = ""
        state = ""
        zc = ""
        country = "GB"
        store = ""
        phone = ""
        typ = ""
        lat = ""
        lng = ""
        HFound = False
        hours = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"edealerName" : "' in line2:
                name = (
                    line2.split('"edealerName" : "')[1]
                    .split('"')[0]
                    .title()
                    .replace("&Amp;", "&")
                    .replace("&amp;", "&")
                )
            if '"brand" : "' in line2:
                typ = line2.split('"brand" : "')[1].split('"')[0].title()
            if '"edealerIDLocal" : "' in line2:
                store = line2.split('"edealerIDLocal" : "')[1].split('"')[0]
            if '"edealerCity" : "' in line2:
                city = line2.split('"edealerCity" : "')[1].split('"')[0].title()
            if '"edealerAddress" : "' in line2:
                add = (
                    line2.split('"edealerAddress" : "')[1]
                    .split('"')[0]
                    .title()
                    .replace("&Amp;", "&")
                    .replace("&amp;", "&")
                )
            if '"edealerPostalCode" : "' in line2:
                zc = line2.split('"edealerPostalCode" : "')[1].split('"')[0]
            if '"edealerRegion" : "' in line2:
                state = line2.split('"edealerRegion" : "')[1].split('"')[0].title()
            if '"edealerCountry" : "' in line2:
                country = line2.split('"edealerCountry" : "')[1].split('"')[0].upper()
            if 'retailer__phone_number" href="tel:' in line2:
                phone = line2.split('retailer__phone_number" href="tel:')[1].split('"')[
                    0
                ]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if "OPENING HOURS</div>" in line2:
                HFound = True
            if HFound and "</table>" in line2:
                HFound = False
            if HFound and "day</td>" in line2:
                hrs = (
                    line2.split(">")[1].split("<")[0]
                    + ": "
                    + next(lines).split(">")[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if add != "":
            name = name.replace("&#039;", "'")
            add = add.replace("&#039;", "'")
            city = city.replace("&#039;", "'")
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
