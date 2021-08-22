from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("weightwatchers_com")


def fetch_data():
    urls = [
        "https://www.weightwatchers.com/us/sitemap-location.xml",
        "https://www.weightwatchers.com/ca/en/sitemap-location.xml",
        "https://www.weightwatchers.com/uk/sitemap-location.xml",
        "https://www.weightwatchers.com/de/sitemap-location.xml",
        "https://www.weightwatchers.com/au/sitemap-location.xml",
        "https://www.weightwatchers.com/nz/sitemap-location.xml",
        "https://www.weightwatchers.com/br/sitemap-location.xml",
        "https://www.weightwatchers.com/fr/sitemap-location.xml",
        "https://www.weightwatchers.com/nl/sitemap-location.xml",
        "https://www.weightwatchers.com/se/sitemap-location.xml",
        "https://www.weightwatchers.com/be/fr/sitemap-location.xml",
        "https://www.weightwatchers.com/ch/fr/sitemap-location.xml",
    ]
    locs = []
    locinfo = []
    for url in urls:
        r = session.get(url, headers=headers, stream=True)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if (
                "<loc>https://www.weightwatchers.com" in line
                and "/locations" not in line
            ):
                lurl = line.split("<loc>")[1].split("<")[0]
                if lurl not in locs:
                    locs.append(lurl)
    website = "weightwatchers.com"
    for loc in locs:
        country = loc.split(".com/")[1].split("/")[0].upper()
        logger.info(loc)
        name = ""
        typ = "<MISSING>"
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"locationInfo":' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                store = line2.split('"id":')[1].split(",")[0]
                add = (
                    line2.split('"address":{"address1":"')[1].split('"')[0]
                    + " "
                    + line2.split('"address2":"')[1].split('"')[0]
                )
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zipCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
                phone = "<MISSING>"
            if '<div class="dayName' in line2:
                days = line2.split('<div class="dayName')
                for day in days:
                    if '<div class="times' in day:
                        day = (
                            day.replace("<!-- -->", "")
                            .replace('</span><span class="time-35INk">', ", ")
                            .replace("</span>", "")
                            .replace('<span class="time-35INk">', "")
                        )
                        hrs = (
                            day.split('">')[1].split("<")[0]
                            + ": "
                            + day.split('<div class="times')[1]
                            .split('">')[1]
                            .split("</div></div>")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        info = add + "|" + city
        if info not in locinfo and city != "" and "@ Virtual" not in name:
            locinfo.append(info)
            if "Zoom.com" in add:
                add = "<MISSING>"
            if "1162350/ww-studio--virtual-palmyra" in loc:
                add = "<MISSING>"
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
