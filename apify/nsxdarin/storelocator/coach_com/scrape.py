import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("coach_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.coach.com/stores"
    states = []
    alllocs = []
    countries = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'address_states_stateUSSO" >' in line:
            info = (
                line.split('address_states_stateUSSO" >')[1]
                .split("</select>")[0]
                .split('class="select-option" label="')
            )
            for item in info:
                if "SELECT</option>" not in item and "value=" in item:
                    states.append(item.split('"')[0])
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
        start = -10
        while CFound:
            CFound = False
            start = start + 10
            url = (
                "https://www.coach.com/stores-edit-search?country="
                + ccode
                + "&start="
                + str(start)
                + "&sz=10&format=ajax"
            )
            country = ccode
            logger.info(ccode)
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
    for state in states:
        storetypes = [
            "storeType-R",
            "storeType-F",
            "storeType-D",
            "womenFootwear-true",
            "Capability9-true",
        ]
        for stype in storetypes:
            logger.info(("Pulling State %s-%s..." % (state, stype)))
            surl = (
                "https://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery="
                + state
                + "_state&clickedOn="
                + stype
                + "&showRFStoreDivider=false&showRStoreDivider=true&showDStoreDivider=false&showFStoreDivider=false&start=0&sz=10&format=ajax"
            )
            r2 = session.get(surl, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            count = 0
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<span class="newCount hide">' in line2:
                    try:
                        count = int(
                            line2.split('<span class="newCount hide">')[1].split("<")[0]
                        )
                    except:
                        count = "NA"
            if count != "NA":
                for x in range(0, count + 20, 10):
                    s2url = (
                        "https://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery="
                        + state
                        + "_state&clickedOn="
                        + stype
                        + "&showRFStoreDivider=false&showRStoreDivider=true&showDStoreDivider=false&showFStoreDivider=false&start="
                        + str(x)
                        + "&sz=10&format=ajax"
                    )
                    r3 = session.get(s2url, headers=headers)
                    if r3.encoding is None:
                        r3.encoding = "utf-8"
                    for line3 in r3.iter_lines(decode_unicode=True):
                        if '<meta itemprop="name" content="' in line3:
                            stores = line3.split('<meta itemprop="name" content="')
                            for sitem in stores:
                                if '<meta itemprop="branchOf"' in sitem:
                                    name = sitem.split('"')[0]
                                    hours = ""
                                    website = "coach.com"
                                    try:
                                        add = (
                                            sitem.split(
                                                '<span itemprop="streetAddress">'
                                            )[1]
                                            .split("<")[0]
                                            .strip()
                                            .replace("&#35;", "#")
                                        )
                                        city = sitem.split(
                                            '<span itemprop="addressLocality">'
                                        )[1].split("<")[0]
                                        state = sitem.split(
                                            '<span itemprop="addressRegion">'
                                        )[1].split("<")[0]
                                    except:
                                        add = ""
                                        city = ""
                                        state = ""
                                    country = "US"
                                    try:
                                        hours = (
                                            sitem.split(
                                                '<span itemprop="openingHours">'
                                            )[1]
                                            .split("<br/> </span>")[0]
                                            .replace("<br/>", "; ")
                                            .replace("\t", "")
                                            .replace("  ", " ")
                                            .replace("  ", " ")
                                        )
                                    except:
                                        hours = ""
                                    try:
                                        zc = sitem.split('emprop="postalCode">')[
                                            1
                                        ].split("<")[0]
                                    except:
                                        zc = ""
                                    try:
                                        phone = (
                                            sitem.split('itemprop="telephone">')[1]
                                            .split("<")[0]
                                            .replace("&#40;", "(")
                                            .replace("&#41;", ")")
                                        )
                                    except:
                                        phone = ""
                                    typ = stype
                                    store = "<MISSING>"
                                    lat = "<MISSING>"
                                    lng = "<MISSING>"
                                    if hours == "":
                                        hours = "<MISSING>"
                                    if typ == "storeType-R":
                                        typ = "Coach Retail"
                                    if typ == "storeType-F":
                                        typ = "Coach Outlet"
                                    if typ == "storeType-D":
                                        typ = "Coach Department & Specialty Stores"
                                    if typ == "womenFootwear-true":
                                        typ = "Womens Footwear"
                                    if typ == "Capability9-true":
                                        typ = "Bape x Coach Collection"
                                    loc = "<MISSING>"
                                    if phone == "":
                                        phone = "<MISSING>"
                                    if zc == "":
                                        zc = "<MISSING>"
                                    stinfo = name + "|" + add + "|" + city + "|" + state
                                    if stinfo not in alllocs and add != "":
                                        alllocs.append(stinfo)
                                        phone = phone.replace("&#40;", "(").replace(
                                            "&#41;", ")"
                                        )
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
    storetypes = [
        "storeType-R",
        "storeType-F",
        "storeType-D",
        "womenFootwear-true",
        "Capability9-true",
    ]
    for stype in storetypes:
        logger.info(("Pulling Canada %s..." % stype))
        surl = (
            "https://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery=CA_country&clickedOn="
            + stype
            + "&showRFStoreDivider=false&showRStoreDivider=true&showDStoreDivider=false&showFStoreDivider=false&start=0&sz=10&format=ajax"
        )
        r2 = session.get(surl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        count = 0
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<span class="newCount hide">' in line2:
                try:
                    count = int(
                        line2.split('<span class="newCount hide">')[1].split("<")[0]
                    )
                except:
                    count = "NA"
        if count != "NA":
            for x in range(0, count + 20, 10):
                s2url = (
                    "https://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery=CA_country&clickedOn="
                    + stype
                    + "&showRFStoreDivider=false&showRStoreDivider=true&showDStoreDivider=false&showFStoreDivider=false&start="
                    + str(x)
                    + "&sz=10&format=ajax"
                )
                r3 = session.get(s2url, headers=headers)
                if r3.encoding is None:
                    r3.encoding = "utf-8"
                for line3 in r3.iter_lines(decode_unicode=True):
                    if '<meta itemprop="name" content="' in line3:
                        stores = line3.split('<meta itemprop="name" content="')
                        for sitem in stores:
                            if '<meta itemprop="branchOf"' in sitem:
                                name = sitem.split('"')[0]
                                hours = ""
                                website = "coach.com"
                                try:
                                    add = (
                                        sitem.split('<span itemprop="streetAddress">')[
                                            1
                                        ]
                                        .split("<")[0]
                                        .strip()
                                        .replace("&#35;", "#")
                                    )
                                    city = sitem.split(
                                        '<span itemprop="addressLocality">'
                                    )[1].split("<")[0]
                                    state = sitem.split(
                                        '<span itemprop="addressRegion">'
                                    )[1].split("<")[0]
                                except:
                                    add = ""
                                    city = ""
                                    state = ""
                                country = "CA"
                                try:
                                    hours = (
                                        sitem.split('<span itemprop="openingHours">')[1]
                                        .split("<br/> </span>")[0]
                                        .replace("<br/>", "; ")
                                        .replace("\t", "")
                                        .replace("  ", " ")
                                        .replace("  ", " ")
                                    )
                                except:
                                    hours = ""
                                try:
                                    zc = sitem.split('emprop="postalCode">')[1].split(
                                        "<"
                                    )[0]
                                except:
                                    zc = ""
                                try:
                                    phone = (
                                        sitem.split('itemprop="telephone">')[1]
                                        .split("<")[0]
                                        .replace("&#40;", "(")
                                        .replace("&#41;", ")")
                                    )
                                except:
                                    phone = ""
                                typ = stype
                                store = "<MISSING>"
                                lat = "<MISSING>"
                                lng = "<MISSING>"
                                if hours == "":
                                    hours = "<MISSING>"
                                if typ == "storeType-R":
                                    typ = "Coach Retail"
                                if typ == "storeType-F":
                                    typ = "Coach Outlet"
                                if typ == "storeType-D":
                                    typ = "Coach Department & Specialty Stores"
                                if typ == "womenFootwear-true":
                                    typ = "Womens Footwear"
                                if typ == "Capability9-true":
                                    typ = "Bape x Coach Collection"
                                loc = "<MISSING>"
                                if phone == "":
                                    phone = "<MISSING>"
                                if zc == "":
                                    zc = "<MISSING>"
                                stinfo = name + "|" + add + "|" + city + "|" + state
                                if stinfo not in alllocs:
                                    alllocs.append(stinfo)
                                    phone = phone.replace("&#40;", "(").replace(
                                        "&#41;", ")"
                                    )
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
