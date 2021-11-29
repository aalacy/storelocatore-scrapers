from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominospizza_cl")


def fetch_data():
    url = "https://www.dominospizza.cl/locales"
    cities = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<option value="' in line:
            cities.append(line.split('<option value="')[1].split('"')[0])
    website = "dominospizza.cl"
    typ = "<MISSING>"
    country = "CL"
    loc = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    lat = "<MISSING>"
    store = "<MISSING>"
    lng = "<MISSING>"
    for cname in cities:
        curl = (
            "https://www.dominospizza.cl/locales/comuna?utf8=%E2%9C%93&town="
            + cname
            + "&button="
        )
        logger.info("Pulling City %s" % cname)
        city = cname
        r2 = session.get(curl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h5 class="card-title">' in line2:
                add = ""
                phone = ""
                hours = ""
                name = line2.split('<h5 class="card-title">')[1].split("<")[0]
            if '<div class="col-12 col-md-6">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<p>" in g:
                    add = g.split("<p>")[1].split("<")[0].strip()
            if "<a href='tel:" in line2:
                phone = line2.split("<a href='tel:")[1].split("'")[0]
            if "noBorderRadiusRight" in line2:
                day = (
                    line2.split("noBorderRadiusRight")[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
            if "noBorderRadiusLeft" in line2:
                hrs = (
                    day
                    + ": "
                    + (
                        line2.split("noBorderRadiusLeft")[1]
                        .split(">")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                )
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = (
                    hrs
                    + " "
                    + g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "</table>" in line2:
                cstring = ", " + city
                add = add.replace(cstring, "").strip()
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
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
