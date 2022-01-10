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

logger = SgLogSetup().get_logger("virginmobile_ca")


def fetch_data():
    for x in range(-55, -140, -1):
        for y in range(41, 71):
            logger.info(str(y) + "-" + str(x))
            url = (
                "https://virgin.know-where.com/virginplus/cgi/selection?place=&lang=en&ll="
                + str(y)
                + "%2C"
                + str(x)
                + "&stype=ll&async=results"
            )
            r = session.get(url, headers=headers)
            website = "virginmobile.ca"
            typ = "<MISSING>"
            country = "CA"
            loc = "<MISSING>"
            if r.encoding is None:
                r.encoding = "utf-8"
            lines = r.iter_lines(decode_unicode=True)
            for line in lines:
                if '<span class="kw-results-FIELD-NAME ultra"' in line:
                    name = line.split('font-size:16px; ">')[1].split("<")[0].strip()
                if '<td class="kw-results-info" data-kwsite="' in line:
                    store = line.split('data-kwsite="')[1].split('"')[0]
                    add = ""
                    city = ""
                    csz = ""
                    city = ""
                    zc = ""
                    phone = ""
                    state = ""
                    hours = ""
                    name = ""
                if '-address" >' in line:
                    add = line.split('-address" >')[1].split("<")[0]
                if 'city-state">' in line:
                    csz = line.split('city-state">')[1].split("<")[0].strip()
                    zc = csz.rsplit(" ", 1)[1]
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().rsplit(" ", 1)[0]
                if '<i class="fa fa-phone"></i>' in line:
                    phone = (
                        line.split('<i class="fa fa-phone"></i>')[1]
                        .split("<")[0]
                        .strip()
                    )
                if 'kw-detail-hours-list-row ">' in line:
                    next(lines)
                    g = next(lines)
                    day = (
                        g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                    )
                    g = next(lines)
                    g = next(lines)
                    g = next(lines)
                    ope = (
                        g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                    )
                    g = next(lines)
                    g = next(lines)
                    g = next(lines)
                    g = next(lines)
                    g = next(lines)
                    g = next(lines)
                    clo = (
                        g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                    )
                    hrs = day + " " + ope + "-" + clo
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                    hours = (
                        hours.replace('<b style="font-weight: bold">', "")
                        .replace("</b>", "")
                        .replace("  ", " ")
                    )
                if "Services</h4>" in line:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
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
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
