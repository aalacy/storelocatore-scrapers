from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tesla_com")


def fetch_data():
    locs = []
    states = []
    otherlocs = []
    session = SgRequests()
    url = "https://www.tesla.com/en_AE/findus/list"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "<MISSING>"
    logger.info("Pulling Stores")
    Found = False
    for line in r.iter_lines():
        if "<h2>Tesla Stores & Galleries</h2>" in line:
            Found = True
        if Found and "<h2>Tesla Service Centers</h2>" in line:
            Found = False
        if (
            Found
            and '<a href="/en_AE/findus/list/stores/' in line
            and "United+States" not in line
            and "Canada" not in line
            and "United+Kingdom" not in line
        ):
            states.append(
                "https://www.tesla.com" + line.split('href="')[1].split('"')[0]
            )
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a href="/en_AE/findus/location/store/' in line2:
                otherlocs.append(
                    "https://www.tesla.com" + line2.split('href="')[1].split('"')[0]
                )
    for loc in otherlocs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        typ = ""
        state = ""
        zc = ""
        CS = False
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = True
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                rawadd = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                rawadd = (
                    rawadd
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                rawadd = add.strip()
            if '<span class="locality">' in line2:
                g = line2.replace("  ", " ").replace("  ", " ")
                rawadd = rawadd + " " + g.split('ity">')[1].split("<")[0]
                if "<br />" in g:
                    rawadd = rawadd + " " + g.split("<br />")[1].split("<")[0]
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                state = addr.state
                add = addr.street_address_1
                if add is None:
                    add = "<MISSING>"
                else:
                    add = add.strip()
                if "prsanjuan" in loc:
                    add = "381 Calle Juan Calaf"
                    state = "PR"
                    country = "US"
            if '<span class="type">' in line2 and typ == "":
                typ = typ + "; " + line2.split('<span class="type">')[1].split("<")[0]
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br />" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if CS:
            name = name + " - Coming Soon"
        if state == "" or state is None:
            state = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
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

    url = "https://www.tesla.com/findus/list/stores/United+Kingdom"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        session = SgRequests()
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        HFound = True
        CS = False
        for line2 in lines:
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                addinfo = line2.split('<span class="locality">')[1].split("<")[0]
                if addinfo.count(" ") == 2:
                    city = addinfo.split(" ")[2]
                    zc = addinfo.split(" ")[0] + " " + addinfo.split(" ")[1]
                elif addinfo.count(" ") == 3:
                    city = addinfo.split(" ")[2] + " " + addinfo.split(" ")[3]
                    zc = addinfo.split(" ")[0] + " " + addinfo.split(" ")[1]
                else:
                    city = addinfo.strip()
                    zc = "<MISSING>"
            if '<span class="type">' in line2:
                typ = line2.split('<span class="type">')[1].split("<")[0]
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br />" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if add == "":
            add = "<MISSING>"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if phone == "":
            phone = "<MISSING>"
        if "St Albans" in name:
            zc = "<MISSING>"
        if CS:
            name = name + " - Coming Soon"
        if state == "" or state is None:
            state = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
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
    locs = []
    url = "https://www.tesla.com/findus/list/stores/United+States"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        HFound = True
        CS = False
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in r2.iter_lines():
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                city = line2.split('<span class="locality">')[1].split(",")[0]
                state = line2.split(", ")[1].split(" ")[0]
                zc = line2.split("</span>")[0].rsplit(" ", 1)[1]
            if '<span class="type">' in line2:
                typ = line2.split('<span class="type">')[1].split("<")[0]
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br />" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if CS:
            name = name + " - Coming Soon"
        if state == "" or state is None:
            state = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
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
    locs = []
    url = "https://www.tesla.com/findus/list/stores/Canada"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        typ = ""
        state = ""
        zc = ""
        CS = False
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = True
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                g = line2.replace("  ", " ").replace("  ", " ")
                city = g.split('<span class="locality">')[1].split(",")[0]
                state = g.split(", ")[1].split(" ")[0]
                zc = (
                    g.split('<span class="locality">')[1]
                    .split("<")[0]
                    .split(",")[1]
                    .strip()
                    .split(" ", 1)[1]
                )
            if '<span class="type">' in line2 and typ == "":
                typ = typ + "; " + line2.split('<span class="type">')[1].split("<")[0]
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br />" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "parkroyalvancouver" in loc:
            state = "BC"
            zc = "V7T 2Z3"
        if "robsonstreet" in loc:
            state = "BC"
            zc = "V6Z 2V7"
        if "torontosherwaygardens" in loc:
            state = "ON"
            zc = "M9C 1B8"
        if "torontovaughan" in loc:
            state = "ON"
            zc = "L4L 8V1"
        if "yorkdale" in loc:
            state = "ON"
            zc = "M6A 2T9"
        if "https://www.tesla.com/findus/location/store/montrealferrier" in loc:
            hours = "M-F: 7:30-17:30; Sat-Sun: Closed"
        if "torontovaughan" in loc:
            lat = "43.7937365"
            lng = "-79.5496246"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if CS:
            name = name + " - Coming Soon"
        if state == "" or state is None:
            state = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
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
