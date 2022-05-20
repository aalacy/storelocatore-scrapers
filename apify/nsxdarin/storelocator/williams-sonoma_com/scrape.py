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

logger = SgLogSetup().get_logger("williams-sonoma_com")


def fetch_data():
    url = "https://www.williams-sonoma.com/customer-service/store-locator.html"
    r = session.get(url, headers=headers)
    Found = False
    website = "williams-sonoma.com"
    country = "CA"
    lat = "<MISSING>"
    lng = "<MISSING>"
    sc = 0
    typ = "<MISSING>"
    lines = r.iter_lines()
    for line in lines:
        if '<section id="canada">' in line:
            Found = True
            country = "CA"
        if '<section id="mexico">' in line:
            country = "MX"
        if "<h3>Kuwait</h3>" in line:
            country = "KW"
        if '<section id="australia">' in line:
            country = "AU"
        if 'republic-of-korea">' in line:
            country = "KR"
        if Found and "<h4>" in line:
            name = line.split("<h4>")[1].split("<")[0]
            phone = "<MISSING>"
            loc = "<MISSING>"
            hours = "<MISSING>"
            add = "<MISSING>"
            sc = sc + 1
        if "<span>Tel:" in line:
            phone = line.split("<span>Tel:")[1].split("<")[0].strip()
        if Found and '<span class="store-name">' in line:
            name = line.split('<span class="store-name">')[1].split("<")[0]
            add = next(lines).split(">")[1].split("<")[0]
            add = add + " " + next(lines).split(">")[1].split("<")[0]
            phone = "<MISSING>"
            loc = "<MISSING>"
            hours = "<MISSING>"
            sc = sc + 1
        if "Republic of Korea<" in line:
            city = line.split(">")[1].split(",")[0].strip()
            hours = next(lines).split(">")[1].split("<")[0]
        if '<span itemprop="streetAddress">' in line and Found:
            add = (
                next(lines)
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
                .strip()
            )
            city = "<MISSING>"
            state = "<MISSING>"
            zc = "<MISSING>"
        if 'itemprop="addressLocality">' in line and Found:
            city = (
                line.split('itemprop="addressLocality">')[1]
                .split("<")[0]
                .replace(",", "")
                .strip()
            )
        if '"addressRegion">' in line and Found:
            state = line.split('"addressRegion">')[1].split("<")[0]
        if 'itemprop="postalCode">' in line and Found:
            zc = line.split('itemprop="postalCode">')[1].split("<")[0]
        if "phone:" in line.lower() and Found:
            phone = line.lower().split("phone:")[1].split("<")[0].strip()
        if country == "KW":
            add = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zc = "<MISSING>"
            hours = "Sun-Wed: 10AM - 10PM; Thur-Sat: 10AM - MIDNIGHT"
        if Found and '<a href="https://www.williams-sonoma.com/stores/' in line:
            loc = line.split('href="')[1].split('"')[0]
        if Found and "</div>" in line:
            if "The Exchange Building" in add:
                city = "Bondi Junction"
                state = "NSW"
                zc = "2022"
            if "345 Victoria Avenue" in add:
                city = "Chatswood"
                state = "NSW"
                zc = "2067"
            if "1341 Dandenong Road" in add:
                city = "Chadstone"
                state = "VIC"
                zc = "3148"
            if "Homemaker Centre Location F008" in add:
                city = "Essendon Fields"
                state = "VIC"
                zc = "3041"
            add = (
                add.replace("&iacute;", "i")
                .replace("&aacute;", "a")
                .replace("&eacute;", "e")
                .replace("&oacute;", "o")
                .replace("&uacute;", "u")
                .replace("&ntilde;", "n")
            )
            name = (
                name.replace("&iacute;", "i")
                .replace("&aacute;", "a")
                .replace("&eacute;", "e")
                .replace("&oacute;", "o")
                .replace("&uacute;", "u")
                .replace("&ntilde;", "n")
            )
            store = "INTL-" + str(sc)
            add = (
                add.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("amp;", "&")
                .replace("&Aacute;", "A")
            )
            name = name.replace("&nbsp;", " ")
            if "Perisur" in name:
                zc = "04500"
                city = "Coyoacan"
            if "Williams Sonoma Angel" in name:
                city = "Puebla"
                zc = "72450"
            if "Williams Sonoma Le" in name:
                city = "Leon"
                zc = "37150"
            if "Williams Sonoma Quer" in name:
                city = "Santiago de Queretaro"
                zc = "76127"
            if "Williams Sonoma Andamar" in name:
                city = "Veracruz"
                zc = "94298"
            if "de Quevedo" in add:
                city = "Coyoacan"
                zc = "04010"
            if "Phase 3" in name:
                phone = "+965 22283101"
            if '<a href="https://www.williams-sonoma.com/stores/' in line and Found:
                loc = line.split('href="')[1].split('"')[0]
            if "Williams" in add:
                add = add.split("Williams")[0].strip()
            if "WILLIAMS" in add:
                add = add.split("WILLIAMS")[0].strip()
            if loc == "<MISSING>":
                loc = "https://www.williams-sonoma.com/customer-service/store-locator.html"
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

    url = "https://www.williams-sonoma.com/search/stores.json?brands=WS&lat=47.6186&lng=-122.204&radius=20000&includeOutlets=true"
    r = session.get(url, headers=headers)
    website = "williams-sonoma.com"
    country = "US"
    logger.info("Pulling Stores")
    surls = []
    surl = "https://www.williams-sonoma.com/customer-service/store-locator.html"
    r2 = session.get(surl, headers=headers)
    for line2 in r2.iter_lines():
        if '{"storeNumber":' in line2:
            items = line2.split('{"storeNumber":')
            for item in items:
                if '"storeIdentifier":"' in item:
                    sid = item.split(",")[0]
                    sstub = item.split('"storeIdentifier":"')[1].split('"')[0]
                    sweb = "https://www.williams-sonoma.com/stores/us-" + sstub
                    surls.append(sid + "|" + sweb)
    for line in r.iter_lines():
        if '{"properties":' in line:
            items = line.split('{"properties":')
            for item in items:
                if '"DISTANCE":"' in item:
                    typ = "<MISSING>"
                    store = item.split('"STORE_NUMBER":"')[1].split('"')[0]
                    add = (
                        item.split('"ADDRESS_LINE_1":"')[1].split('"')[0]
                        + " "
                        + item.split('"ADDRESS_LINE_2":"')[1].split('"')[0]
                    )
                    phone = item.split('"PHONE_NUMBER_FORMATTED":"')[1].split('"')[0]
                    name = item.split('"STORE_NAME":"')[1].split('"')[0]
                    city = item.split('"CITY":"')[1].split('"')[0]
                    state = item.split('"STATE_PROVINCE":"')[1].split('"')[0]
                    zc = item.split(',"POSTAL_CODE":"')[1].split('"')[0]
                    lat = item.split('"LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"LONGITUDE":"')[1].split('"')[0]
                    country = item.split('"COUNTRY_CODE":"')[1].split('"')[0]
                    loc = "https://www.williams-sonoma.com/customer-service/store-locator.html"
                    hours = (
                        "Sun: "
                        + item.split('"SUNDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Mon: "
                        + item.split('"MONDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + item.split('"TUESDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + item.split('"WEDNESDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + item.split('"THURSDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + item.split('"FRIDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + item.split('"SATURDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    add = (
                        add.replace("&amp;", "&")
                        .replace("amp;", "&")
                        .replace("&Aacute;", "A")
                    )
                    if "Williams" in add:
                        add = add.split("Williams")[0].strip()
                    if "WILLIAMS" in add:
                        add = add.split("WILLIAMS")[0].strip()
                    for sitem in surls:
                        if sitem.split("|")[0] == store:
                            loc = sitem.split("|")[1]
                    if "customer-service/store-locator.html" not in loc:
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
