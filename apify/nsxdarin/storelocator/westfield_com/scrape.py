from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("westfield_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.westfield.com"
    r = session.get(url, headers=headers)
    website = "westfield.com"
    for line in r.iter_lines():
        if 'class="js-centre-name"' in line:
            city = line.split('data-track="click center tile" data-track-label="')[
                1
            ].split(" home")[0]
            locs.append(
                "https://www.westfield.com"
                + line.split('href="')[1].split('"')[0]
                + "|"
                + city
            )
    for loc in locs:
        logger.info((loc.split("|")[0]))
        r2 = session.get(loc.split("|")[0], headers=headers)
        typ = "Center"
        store = "<MISSING>"
        name = ""
        add = ""
        city = loc.split("|")[1]
        state = ""
        zc = ""
        country = "US"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        for line2 in r2.iter_lines():
            if 'name="title" content="' in line2:
                name = line2.split('name="title" content="')[1].split('"')[0]
            if '"addresses":"' in line2:
                addinfo = line2.split('"addresses":"')[1].split('"')[0]
                zc = addinfo.rsplit(" ", 1)[1]
                state = addinfo.rsplit(" ", 2)[1].split(" ")[0]
                add = addinfo.split(city)[0].strip()
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
        loc2 = loc.split("|")[0] + "/access"
        try:
            r3 = session.get(loc2, headers=headers)
            for line3 in r3.iter_lines():
                if '<span class="date">' in line3:
                    items = line3.split('<span class="date">')
                    for item in items:
                        if '<span class="schedule">' in item:
                            hrs = (
                                item.split("<")[0]
                                + ": "
                                + item.split('<span class="schedule">')[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
        except:
            hours = "<MISSING>"
        if add != "":
            if "annapolis" in loc.split("|")[0]:
                add = "2002 Annapolis Mall"
                city = "Annapolis"
                state = "MD"
                zc = "21401"
            if "southcenter" in loc.split("|")[0]:
                add = "2800 Southcenter Mall"
                city = "Seattle"
            if "gardenstate" in loc.split("|")[0]:
                add = "One Garden State Plaza"
                city = "Paramus"
            if "oldorchard" in loc.split("|")[0]:
                add = "4905 Old Orchard Center"
                city = "Skokie"
            if "plazabonita" in loc.split("|")[0]:
                add = "3030 Plaza Bonita Road, Suite 2075"
                city = "National City"
            if "gardenstate" in loc.split("|")[0]:
                add = "One Garden State Plaza"
                city = "Paramus"
            if "topanga" in loc.split("|")[0]:
                add = "6600 Topanga Canyon Boulevard"
                city = "Canoga Park"
            if " (" in add:
                add = add.split(" (")[0]
            if "brandon" in loc.split("|")[0]:
                add = "459 Brandon Town Center"
                city = "Brandon"
                state = "FL"
                zc = "33511"
            if "valencia" in add.split("|")[0]:
                add = "24201 West Valencia Blvd Suite 150"
                city = "Valencia"
                state = "CA"
                zc = "91355"
            cities = [
                "Sherman Oaks",
                "Los Angeles",
                "San Diego",
                "Bethesda",
                "Escondido",
                "San Francisco",
                "Arcadia",
                "Bay Shore",
                "Canoga Park",
                "Valencia",
                "Santa Clara",
                "New York",
            ]
            for cname in cities:
                if cname in add:
                    add = add.split(cname)[0].strip()
                    city = cname
            yield SgRecord(
                locator_domain=website,
                page_url=loc.split("|")[0],
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
