# -*- coding: cp1252 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_id import SgRecordID

logger = SgLogSetup().get_logger("coach_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    main_url = "https://fr.coach.com/en_FR/stores-edit-country?dwfrm_storelocator_address_international=FR&dwfrm_storelocator_findbycountry=Search%2Bcountry"
    states = []
    cities = []
    countries = []
    r = session.get(main_url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'name="dwfrm_storelocator_address_international" >' in line:
            info = (
                line.split('name="dwfrm_storelocator_address_international" >')[1]
                .split("</select>")[0]
                .split('value="')
            )
            for item in info:
                if "</option>" in item:
                    ccode = item.split('"')[0]
                    if len(ccode) > 1:
                        countries.append(ccode)
    for ccode in countries:
        CFound = True
        start = -15
        while CFound:
            CFound = False
            start = start + 15
            url = (
                "https://fr.coach.com/en_FR/stores-edit-search?country="
                + ccode
                + "&start="
                + str(start)
                + "&sz=15&format=ajax"
            )
            country = ccode
            logger.info(url)
            loc = "<MISSING>"
            r2 = session.get(url, headers=headers)
            allinfo = ""
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                allinfo = allinfo + line2.replace("\r", "").replace("\n", "").replace(
                    "\t", ""
                )
            if "<h2>" in allinfo:
                CFound = True
                items = allinfo.split("<h2>")
                for item in items:
                    if '<div class="store-info">' in item:
                        name = item.split("</h2>")[0].replace("&amp;", "&")
                        add = (
                            item.split('span itemprop="streetAddress">')[1]
                            .split("</span>")[0]
                            .replace("<br />", "")
                            .replace("  ", " ")
                            .replace("  ", " ")
                        )
                        website = "coach.com"
                        typ = "<MISSING>"
                        store = "<MISSING>"
                        city = item.split('<span itemprop="addressLocality">')[1].split(
                            "</span>"
                        )[0]
                        state = "<MISSING>"
                        try:
                            zc = item.split('<span itemprop="postalCode">')[1].split(
                                "<"
                            )[0]
                        except:
                            zc = "<MISSING>"
                        phone = item.split('itemprop="telephone">')[1].split("<")[0]
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        try:
                            hours = (
                                item.split('<span itemprop="openingHours">')[1]
                                .split("</span>")[0]
                                .replace("<br />", "")
                                .replace("  ", " ")
                                .replace("  ", " ")
                            )
                        except:
                            hours = "<MISSING>"
                        hours = hours.replace("<br/>", "; ")
                        add = add.replace("&amp;", "&")
                        if ", TIER" in city:
                            city = city.split(", TIER")[0].strip()
                        if phone == "":
                            phone = "<MISSING>"
                        phone = phone.replace("&#40;", "(").replace("&#41;", ")")
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
    main_url = "https://www.coach.com/stores/"
    locs = []
    r = session.get(main_url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://www.coach.com/stores/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'class="Directory-listLink" href="' in line2:
                items = line2.split('class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        lurl = "https://www.coach.com/stores/" + item.split('"')[0]
                        if count == "1":
                            if lurl not in locs:
                                locs.append(lurl)
                        else:
                            if lurl not in cities and lurl not in states:
                                cities.append(lurl)

    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"visitpage" href="../' in line2:
                items = line2.split('"visitpage" href="../')
                for item in items:
                    if "Explore This Shop" in item:
                        lurl = "https://www.coach.com/stores/" + item.split('"')[0]
                        if lurl not in locs:
                            locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        loc = loc.replace("&amp;", "&").replace("&#39;", "'")
        website = "coach.com"
        country = "US"
        typ = "<MISSING>"
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        name = ""
        store = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'emprop="openingHours" content="' in line2:
                days = line2.split('emprop="openingHours" content="')
                for day in days:
                    if '"><td class="c-hours-details-row-day">' in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if '"og:title" content="' in line2:
                name = line2.split('"og:title" content="')[1].split('"')[0]
                if " – " in name:
                    name = name.split(" – ")[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if 'itemprop="addressLocality" content="' in line2:
                city = line2.split('itemprop="addressLocality" content="')[1].split(
                    '"'
                )[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
        if "Outlet In" in name:
            typ = "Coach Outlet"
        else:
            typ = "Coach"
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

    states = []
    cities = []
    locs = []
    main_url = "https://ca.coach.com/stores/"
    locs = []
    r = session.get(main_url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://ca.coach.com/stores/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'class="Directory-listLink" href="' in line2:
                items = line2.split('class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        lurl = "https://ca.coach.com/stores/" + item.split('"')[0]
                        if count == "1":
                            if lurl not in locs:
                                locs.append(lurl)
                        else:
                            if lurl not in cities and lurl not in states:
                                cities.append(lurl)

    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"visitpage" href="../' in line2:
                items = line2.split('"visitpage" href="../')
                for item in items:
                    if "Explore This Shop" in item:
                        lurl = "https://ca.coach.com/stores/" + item.split('"')[0]
                        if lurl not in locs:
                            locs.append(lurl)
    for loc in locs:
        loc = loc.replace("&amp;", "&").replace("&#39;", "'")
        logger.info(loc)
        website = "coach.com"
        country = "CA"
        typ = "<MISSING>"
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        name = ""
        store = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'emprop="openingHours" content="' in line2:
                days = line2.split('emprop="openingHours" content="')
                for day in days:
                    if '"><td class="c-hours-details-row-day">' in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if '"og:title" content="' in line2:
                name = line2.split('"og:title" content="')[1].split('"')[0]
                if " – " in name:
                    name = name.split(" – ")[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if 'itemprop="addressLocality" content="' in line2:
                city = line2.split('itemprop="addressLocality" content="')[1].split(
                    '"'
                )[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
        if "Outlet In" in name:
            typ = "Coach Outlet"
        else:
            typ = "Coach"
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
