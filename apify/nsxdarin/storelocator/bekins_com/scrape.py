from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("bekins_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.bekins.com/agent-sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if (
            "<loc>https://www.bekins.com/find-a-local-agent/agents/" in line
            and "<loc>https://www.bekins.com/find-a-local-agent/agents/<" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = "<MISSING>"
        logger.info(("Pulling Location %s..." % loc))
        website = "bekins.com"
        typ = "Agent"
        if "ams-relocation" not in loc and "bekins-northwest" not in loc:
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            lines = r2.iter_lines(decode_unicode=True)
            for line2 in lines:
                if 'u-paddingTop4gu u-marginBottom0gu">' in line2:
                    name = line2.split('u-paddingTop4gu u-marginBottom0gu">')[1].split(
                        "<"
                    )[0]
                    csz = (
                        line2.split('u-paddingTop4gu u-marginBottom0gu">')[1]
                        .split("<br>")[1]
                        .split("<")[0]
                        .strip()
                    )
                    add = csz.split(",")[0]
                    city = csz.split(",")[1].strip()
                    state = csz.split(",")[2].strip().split(" ")[0]
                    zc = csz.rsplit(" ", 1)[1]
                if "<h2>" in line2:
                    name = line2.split("<h2>")[1].split("<")[0].replace("\t", "")
                if '<div class="agent-address">' in line2:
                    h = line2
                    if h.count(",") == 2:
                        add = h.split(">")[1].split(",")[0]
                        city = h.split(",")[1].strip()
                        state = h.split(",")[2].strip().split(" ")[0]
                        zc = h.split(",")[2].split("<")[0].rsplit(" ", 1)[1]
                    else:
                        add = (
                            h.split(">")[1].split(",")[0]
                            + " "
                            + h.split(",")[1].strip()
                        )
                        city = h.split(",")[2].strip()
                        state = h.split(",")[3].strip().split(" ")[0]
                        zc = h.split(",")[3].split("<")[0].rsplit(" ", 1)[1]
                if '<a class="contact-link contact-phone" href="tel:' in line2:
                    phone = line2.split(
                        '<a class="contact-link contact-phone" href="tel:'
                    )[1].split('"')[0]
                if "Phone:" in line2 and 'href="tel:' in line2:
                    phone = line2.split('href="tel:')[1].split('"')[0].replace("/", "")
                if 'contact-link contact-phone" href="tel:' in line2:
                    phone = line2.split('contact-link contact-phone" href="tel:')[
                        1
                    ].split('"')[0]
        if "ams-relocation" in loc or "bekins-northwest" in loc:
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if 'contact-link contact-phone" href="tel:' in line2:
                    phone = line2.split('contact-link contact-phone" href="tel:')[
                        1
                    ].split('"')[0]
        if "ams-relocation" in loc:
            name = "AMS Relocation, Inc."
            add = "1873 Rollins Rd"
            city = "Burlingame"
            state = "CA"
            zc = "94010"
            phone = "866-798-0342"
        if "ams-relocation-inc" in loc:
            phone = "650-697-3530"
        if "bekins-northwest-10" in loc:
            name = "Bekins Northwest"
            add = "22647 72nd Ave S"
            city = "Kent"
            state = "WA"
            zc = "98032"
        if "bekins-northwest-2" in loc:
            name = "Bekins Northwest"
            add = "1100 Columbia Park Trail"
            city = "Richland"
            state = "WA"
            zc = "99352"
        if "bekins-northwest-3" in loc:
            name = "Bekins Northwest"
            add = "6501 216th Street SW"
            city = "Mountlake Terrace"
            state = "WA"
            zc = "98043"
        if "bekins-northwest-4" in loc:
            name = "Bekins Northwest"
            add = "1891 N 1st Street"
            city = "Yakima"
            state = "WA"
            zc = "98901"
        if "bekins-northwest-5" in loc:
            name = "Bekins Northwest"
            add = "1017 South 344th Street, Suite A"
            city = "Federal Way"
            state = "WA"
            zc = "98003"
        if "bekins-northwest-6" in loc:
            name = "Bekins Northwest"
            add = "10115 E. Knox Avenue"
            city = "Spokane"
            state = "WA"
            zc = "99206"
        if "bekins-northwest-7" in loc:
            name = "Bekins Northwest"
            add = "940 Poplar St SE"
            city = "Olympia"
            state = "WA"
            zc = "98501"
        if "bekins-northwest-9" in loc:
            name = "Bekins Northwest"
            add = "841 N 6th Ave"
            city = "Walla Walla"
            state = "WA"
            zc = "99362"
        if "bekins-northwest" in loc and "northwest-" not in loc:
            name = "Bekins Northwest"
            add = "7010 150th St SW, Suite 101"
            city = "Lakewood"
            state = "WA"
            zc = "98439"
        if "bekins-of-south-florida-3" in loc:
            add = "SALES OFFICE , 7875 Mandarin Dr"
            city = "Boca Raton"
            state = "FL"
            zc = "33433"
        if "bekins-transfer-storage-2" in loc:
            add = "201 Windsor Rd , Limerick Airport Business Center"
            city = "Pottstown"
            state = "PA"
            zc = "19464"
        if "bekins-moving-solutions-inc-5" in loc:
            add = "2025 Gillespie Way, Ste B"
            city = "El Cajon"
            state = "CA"
            zc = "92020"
        if "boyer-rosene-moving-storage-inc" in loc:
            add = "2638 S Clearbrook Dr"
            city = "Arlington Heights"
            state = "IL"
            zc = "60005"
        if "bekins-moving-solutions-va" in loc:
            add = "5827 Curlew Drive, Suite 5"
            city = "Norfolk"
            state = "VA"
            zc = "23502"
        country = "US"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        if "ridgewood-moving-services" in loc:
            add = "575 Corporate Drive, Suite 405"
            city = "Mahwah"
            state = "NJ"
            zc = "07430"
        if state != "":
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
