from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("onehourheatandair_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    url = "https://www.onehourheatandair.com/locations/"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "View Website</a>" in line:
            stub = (
                "https://www.onehourheatandair.com"
                + line.split('href="')[1].split('"')[0]
            )
            if stub not in locs and "comhttp" not in stub:
                locs.append(stub)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "onehourheatandair.com"
        name = ""
        country = "US"
        lat = "<MISSING>"
        lng = "<MISSING>"
        typ = "Location"
        store = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        hours = "<MISSING>"
        phone = "<MISSING>"
        zc = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        add = "<MISSING>"
        add2 = "<MISSING>"
        for line2 in lines:
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if (
                '<a class="color-swap social-link" href="https://www.google.com/maps/place/'
                in line2
            ):
                try:
                    add2 = line2.split("2s")[1].split(",")[0].replace("+", " ")
                except:
                    add2 = "<MISSING>"
            if '<span itemprop="streetAddress">' in line2:
                g = next(lines)
                add = g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if "<title>" in line2:
                name = line2.split(">")[1].split(" |")[0]
            if 'flex-middle margin-right-tiny">' in line2:
                city = line2.split('flex-middle margin-right-tiny">')[1].split(",")[0]
                state = (
                    line2.split('flex-middle margin-right-tiny">')[1]
                    .split("<")[0]
                    .rsplit(" ", 1)[1]
                )
            if (
                '<a class="phone-link phone-number-style text-color" href="tel:'
                in line2
            ):
                phone = line2.split(
                    '<a class="phone-link phone-number-style text-color" href="tel:'
                )[1].split('"')[0]
            if '<span itemprop="name" data-item="i" data-key="' in line2:
                store = line2.split('<span itemprop="name" data-item="i" data-key="')[
                    1
                ].split('"')[0]
            if "/maps/place/" in line2:
                lat = line2.split("/@")[1].split(",")[0]
                lng = line2.split("/@")[1].split(",")[1]
        if name != "":
            if add == "<MISSING>":
                add = add2
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
