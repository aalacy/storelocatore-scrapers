from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ikea_co_uk")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.ikea.com/gb/en/stores/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if (
            '<p><a href="https://www.ikea.com/gb/en/stores/' in line
            and "Bromley - Planning studio" not in line
        ):
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "ikea.co.uk"
        typ = "IKEA Store"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        country = "GB"
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        if "planning-studios" in loc:
            typ = "IKEA Planning Studio"
        if "order-collection-point" in loc:
            typ = "IKEA Order and Collection Point"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if (
                "planning-studios" in loc
                and "<h2><strong>" in line2
                and "FAQ" not in line2
            ):
                name = line2.split("<strong>")[1].split("<")[0]
                if "Bromley" in name:
                    add = "156-160 High Street"
                    city = "Bromley"
                    zc = "BR1 1HE"
                if "Tottenham" in name:
                    add = "95 Tottenham Court Road, Bloomsbury"
                    city = "London"
                    zc = "W1T 4TW"
            if "planning-studios" in loc and "Opening Hours</strong></h3>" in line2:
                g = next(lines)
                hours = (
                    g.split("<p>")[1]
                    .split("</p>")[0]
                    .replace("&nbsp;", " ")
                    .replace("<strong>", "")
                    .replace("</strong>", "")
                    .replace("<br>", "; ")
                )
                if hours == "":
                    hours = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                yield [
                    website,
                    loc,
                    name,
                    add,
                    city,
                    state,
                    zc,
                    country,
                    store,
                    phone,
                    typ,
                    lat,
                    lng,
                    hours,
                ]
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if "Address</strong>" in line2:
                g = next(lines)
                addinfo = g.split(">")[1].split("<")[0]
                if addinfo.count(",") == 2:
                    add = addinfo.split(",")[0].strip()
                    city = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                else:
                    add = (
                        addinfo.split(",")[0].strip()
                        + " "
                        + addinfo.split(",")[1].strip()
                    )
                    city = addinfo.split(",")[2].strip()
                    zc = addinfo.split(",")[3].strip()
            if ":00</strong>" in line2 and "planning-studios" not in loc:
                hrs = line2.split("<p>")[1].split("</p>")[0].replace("</strong>", "")
                hrs = hrs.replace("<strong>", "").replace("&nbsp;", " ")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "gb/en/stores/edinburgh" in loc:
            city = "Edinburgh"
            add = "Costkea way, Loanhead"
            zc = "EH20 9BY"
        if "gb/en/stores/glasgow" in loc:
            city = "Glasgow"
            add = "99 Kings Inch Drive"
            zc = "G51 4FB"
        if "/stores/nottingham" in loc:
            zc = "NG16 2RP"
        if "stores/gateshead" in loc:
            zc = "NE11 9XS"
        if "stores/milton-keynes" in loc:
            zc = "MK1 1QB"
        if "/stores/croydon" in loc:
            city = "Croydon"
            add = "Access via Hesterman Way"
            zc = "CR0 4YA"
        if "planning-studios" not in loc:
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
