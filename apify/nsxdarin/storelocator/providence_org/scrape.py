from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("providence_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    alllocs = []
    scalocs = []
    mtlocs = []
    aklocs = []
    orlocs = []
    locadds = [
        "https://oregon.providence.org/location-directory/p/providence-arrhythmia-services-at-providence-portland-medical-center|4805 NE Glisan St.|<MISSING>",
        "https://oregon.providence.org/location-directory/p/providence-childrens-development-institute-east|830 NE 47th Ave|Mon-Fri: 8 a.m.-5 p.m.",
        "https://alaska.providence.org/locations/p/providence-laboratory-services|3851 Piper St Suite T211|Mon - Fri: 6 a.m. - 6 p.m.; Sat - Sun: 7 a.m. - 3 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-outpatient-neurological-therapy-southern-oregon|1111 Crater Lake Ave.|Mon. - Fri.: 7 a.m. - 6 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-outpatient-orthopedic-therapy-southern-oregon/|1111 Crater Lake Ave.|Mon. - Fri.: 7 a.m. - 6 p.m.",
        "https://oregon.providence.org/location-directory/c/community-teaching-kitchen|10202 SE 32nd Ave., Suite 101|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-neurological-specialties-milwaukie|10330 SE 32nd Ave., Suite 226|<MISSING>",
        "https://oregon.providence.org/location-directory/p/providence-psychiatry-clinic-milwaukie|10202 SE 32nd Ave., Bldg. 700, Suite 701|<MISSING>",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-newberg-clinic|1000 Providence Drive, Suite 310|Mon - Fri: 8 a.m. - 5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-medical-group-ear-nose-and-throat-newberg|1003 Providence Drive, Suite 210|Monday-Friday: 7:30 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-neurological-specialties-newberg|1003 Providence Drive, Suite 110|Monday-Friday: 7:30 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-breast-care-clinic|4805 NE Glisan St, Suite 11N-2|Mon - Fri: 8 a.m. - 5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-clinic|4805 NE Glisan St, Suite 11N-1|Monday-Friday, 8 a.m. to 5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-dysplasia-clinic|4805 NE Glisan St., Suite 11N-5|Monday-Friday 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-genetic-risk-clinic|4805 NE Glisan St., Suite 11N-3|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-head-and-neck-clinic|4805 NE Glisan St., Suite 11N-7|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-liver-clinic|4805 NE Glisan St., Suite 11N-6|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-oral-oncology-clinic|4805 NE Glisan St., Suite 11N-4|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-cancer-institute-franz-thoracic-surgery|4805 NE Glisan St., Suite 11N-8|Monday-Friday, 8 a.m.-5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-neurological-specialties-east|5050 NE Hoyt St., Suite 315|Monday - Friday: 8 a.m. to 4:30 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-occupational-medicine-the-plaza|5050 NE Hoyt, Suite B48|Monday-Friday, 7 a.m.-6 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-pediatric-surgery-the-plaza|5050 NE Hoyt St., Suite 610|1st and 3rd Monday of each month from 10 a.m. to noon",
        "https://oregon.providence.org/location-directory/p/providence-cancer-center-oncology-and-hematology-care-clinic-westside-portland|9135 SW Barnes Road, Suite 261|Monday-Friday, 8 a.m. to 5 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-childrens-development-institute-west|9135 SW Barnes Rd, Suite 561|Mon-Fri: 8 a.m.-4:30 p.m.",
        "https://oregon.providence.org/location-directory/p/providence-diabetes-and-health-education-center|9340 SW Barnes Road, Suite 200|<MISSING>",
        "https://oregon.providence.org/location-directory/p/providence-oral-oncology-and-oral-medicine-clinic-west|9135 SW Barnes Road, Suite 261|<MISSING>",
        "https://oregon.providence.org/location-directory/p/providence-neurological-specialties-willamette-falls|1510 Division St, Suite 180|Mon-Fri: 8 a.m.-5 p.m.",
    ]

    Found = False
    for x in range(1, 10):
        logger.info(("Pulling MT Page %s..." % str(x)))
        url = (
            "https://montana.providence.org/locations-directory/list-view?page="
            + str(x)
        )
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<ul  class="list-unstyled row">' in line:
                Found = True
            if Found and '<div id="psjh_body_1' in line:
                Found = False
            if Found and '<a href="/locations-directory/' in line:
                lurl = (
                    "https://montana.providence.org"
                    + line.split('href="')[1].split('"')[0]
                )
                if lurl not in mtlocs:
                    mtlocs.append(lurl)
                mloc = lurl
                website = "providence.org"
                typ = "<MISSING>"
                hours = "<MISSING>"
                g = next(lines)
                name = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                while "<br" not in g:
                    g = next(lines)
                h = (
                    next(lines)
                    .strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                )
                if (
                    "Professional Plaza" in g
                    or "Medical Center" in g
                    or " Hospital" in g
                    or "Child Center" in g
                    or "Services at " in g
                ):
                    g = next(lines)
                add = g.split("<")[0].strip().replace("\t", "")
                if " Suite" in add:
                    add = add.split(" Suite")[0]
                city = h.split(",")[0]
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.rsplit(" ", 1)[1]
                country = "US"
                phone = "<MISSING>"
                lat = "<MISSING>"
                store = "<MISSING>"
                lng = "<MISSING>"
            if Found and "?q=" in line:
                lat = line.split("?q=")[1].split(",")[0]
                lng = line.split("?q=")[1].split(",")[1].split('"')[0]
            if Found and "</li>" in line:
                newadd = ""
                if "," in add:
                    addparts = add.split(",")
                    for aitem in addparts:
                        if "Floor" not in aitem:
                            if newadd == "":
                                newadd = aitem
                            else:
                                newadd = newadd + "," + aitem
                else:
                    newadd = add
                if "," in phone:
                    phone = phone.split(",")[0].strip()
                if " Option" in phone:
                    phone = phone.split(" Option")[0].strip()
                citytext = " - " + city
                name = name.replace(citytext, "")
                addfirst = add[0:5]
                if addfirst in name:
                    nameorig = name
                    name = name.split(addfirst)[0].strip()
                    if name == "":
                        name = nameorig
                infotext = mloc + "|" + name + "|" + newadd + "|" + phone
                if infotext not in alllocs:
                    alllocs.append(infotext)
                    r2 = session.get(mloc, headers=headers)
                    for line2 in r2.iter_lines():
                        if '"latitude" content="' in line2:
                            lat = line2.split('"latitude" content="')[1].split('"')[0]
                            lng = line2.split('"longitude" content="')[1].split('"')[0]
                    yield SgRecord(
                        locator_domain=website,
                        page_url=mloc,
                        location_name=name,
                        street_address=newadd,
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
        logger.info(("%s MT Locations Found" % str(len(mtlocs))))
    for x in range(1, 50):
        logger.info(("Pulling OR Page %s..." % str(x)))
        PFound = True
        while PFound:
            try:
                PFound = False
                url = (
                    "https://oregon.providence.org/location-directory/list-view/?page="
                    + str(x)
                    + "&within=5000"
                )
                r = session.get(url, headers=headers)
                lines = r.iter_lines()
                for line in lines:
                    if '<h4><a id="main_0_contentpanel' in line:
                        lurl = (
                            "https://oregon.providence.org"
                            + line.split('href="')[1].split('"')[0]
                        )
                        if lurl not in orlocs:
                            orlocs.append(lurl)
                        mloc = lurl
                        website = "providence.org"
                        typ = "<MISSING>"
                        hours = "<MISSING>"
                        name = line.split('">')[1].split("<")[0].strip()
                        phone = "<MISSING>"
                        add = ""
                        city = ""
                        state = ""
                        country = "US"
                        zc = ""
                        store = "<MISSING>"
                    if "pnlAddress_" in line:
                        next(lines)
                        g = next(lines)
                        if g.count("<br/>") == 1:
                            add = g.split("<br/>")[0].strip().replace("\t", "")
                            csz = (
                                g.split("<br/>")[1]
                                .strip()
                                .replace("\t", "")
                                .replace("\r", "")
                                .replace("\n", "")
                            )
                            city = csz.split(",")[0]
                            state = csz.split(",")[1].strip().split(" ")[0]
                            zc = csz.rsplit(" ", 1)[1]
                        else:
                            add = g.split("<br/>")[0].strip().replace("\t", "")
                            csz = (
                                g.split("<br/>")[2]
                                .strip()
                                .replace("\t", "")
                                .replace("\r", "")
                                .replace("\n", "")
                            )
                            city = csz.split(",")[0]
                            state = csz.split(",")[1].strip().split(" ")[0]
                            zc = csz.rsplit(" ", 1)[1]
                        phone = "<MISSING>"
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    if "Phone:" in line:
                        g = next(lines)
                        phone = g.split("tel:")[1].split('"')[0]
                    if '<div class="module-lc-services">' in line:
                        newadd = ""
                        if add != "":
                            if " Suite" in add:
                                add = add.split(" Suite")[0]
                            if "," in add:
                                addparts = add.split(",")
                                for aitem in addparts:
                                    if "Floor" not in aitem:
                                        if newadd == "":
                                            newadd = aitem
                                        else:
                                            newadd = newadd + "," + aitem
                            else:
                                newadd = add
                            if "," in phone:
                                phone = phone.split(",")[0].strip()
                            if " Option" in phone:
                                phone = phone.split(" Option")[0].strip()
                            for ladd in locadds:
                                if ladd.split("|")[0] == mloc:
                                    newadd = ladd.split("|")[1]
                                    hours = ladd.split("|")[2]
                            citytext = " - " + city
                            name = name.replace(citytext, "")
                            addfirst = add[0:5]
                            if addfirst in name:
                                nameorig = name
                                name = name.split(addfirst)[0].strip()
                                if name == "":
                                    name = nameorig
                            infotext = mloc + "|" + name + "|" + newadd + "|" + phone
                            if infotext not in alllocs:
                                alllocs.append(infotext)
                                r2 = session.get(mloc, headers=headers)
                                for line2 in r2.iter_lines():
                                    if '"latitude" content="' in line2:
                                        lat = line2.split('"latitude" content="')[
                                            1
                                        ].split('"')[0]
                                        lng = line2.split('"longitude" content="')[
                                            1
                                        ].split('"')[0]
                                yield SgRecord(
                                    locator_domain=website,
                                    page_url=mloc,
                                    location_name=name,
                                    street_address=newadd,
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
                logger.info(("%s OR Locations Found" % str(len(orlocs))))
            except:
                PFound = True
    for x in range(1, 15):
        logger.info(("Pulling WA Page %s..." % str(x)))
        url = (
            "https://washington.providence.org/locations-directory/search-results?page="
            + str(x)
        )
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<ul  class="list-unstyled row">' in line:
                Found = True
            if Found and '<div id="psjh_body_1' in line:
                Found = False
            if (
                Found
                and '<a href="/locations-directory/' in line
                and "/e/example" not in line
            ):
                lurl = (
                    "https://washington.providence.org"
                    + line.split('href="')[1].split('"')[0]
                )
                if lurl not in mtlocs:
                    mtlocs.append(lurl)
                mloc = lurl
                website = "providence.org"
                typ = "<MISSING>"
                hours = "<MISSING>"
                g = next(lines)
                name = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                next(lines)
                next(lines)
                next(lines)
                g = next(lines)
                h = (
                    next(lines)
                    .strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                )
                if "<br />" in h:
                    g = h
                    h = next(lines)
                add = g.split("<")[0].strip().replace("\t", "")
                if " Suite" in add:
                    add = add.split(" Suite")[0]
                if "," not in h:
                    h = next(lines)
                city = h.split(",")[0]
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.rsplit(" ", 1)[1]
                country = "US"
                phone = "<MISSING>"
                lat = "<MISSING>"
                store = "<MISSING>"
                lng = "<MISSING>"
            if Found and "?q=" in line:
                lat = line.split("?q=")[1].split(",")[0]
                lng = line.split("?q=")[1].split(",")[1].split('"')[0]
            if Found and "</li>" in line:
                if zc == "":
                    zc = "<MISSING>"
                if "h/hospice-of-seattle" in mloc:
                    name = "Providence Hospice of Seattle"
                city = city.strip().replace("\t", "")
                newadd = ""
                if "," in add:
                    addparts = add.split(",")
                    for aitem in addparts:
                        if "Floor" not in aitem:
                            if newadd == "":
                                newadd = aitem
                            else:
                                newadd = newadd + "," + aitem
                else:
                    newadd = add
                if "," in phone:
                    phone = phone.split(",")[0].strip()
                if " Option" in phone:
                    phone = phone.split(" Option")[0].strip()
                citytext = " - " + city
                name = name.replace(citytext, "")
                addfirst = add[0:5]
                if addfirst in name:
                    nameorig = name
                    name = name.split(addfirst)[0].strip()
                    if name == "":
                        name = nameorig
                infotext = mloc + "|" + name + "|" + newadd + "|" + phone
                if infotext not in alllocs:
                    alllocs.append(infotext)
                    r2 = session.get(mloc, headers=headers)
                    for line2 in r2.iter_lines():
                        if '"latitude" content="' in line2:
                            lat = line2.split('"latitude" content="')[1].split('"')[0]
                            lng = line2.split('"longitude" content="')[1].split('"')[0]
                    yield SgRecord(
                        locator_domain=website,
                        page_url=mloc,
                        location_name=name,
                        street_address=newadd,
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
        logger.info(("%s WA Locations Found" % str(len(mtlocs))))
    for x in range(1, 10):
        logger.info(("Pulling AK Page %s..." % str(x)))
        url = (
            "https://alaska.providence.org/locations/list-view?page="
            + str(x)
            + "&within=5000"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h4><a id="main_0' in line:
                lurl = (
                    "https://alaska.providence.org"
                    + line.split('href="')[1].split('"')[0]
                )
                if lurl not in aklocs:
                    aklocs.append(lurl)
        logger.info(("%s AK Locations Found" % str(len(aklocs))))
    for loc in aklocs:
        website = "providence.org"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        HFound = False
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if 'pnlOfficeHours">' in line:
                HFound = True
            if HFound and "</div>" in line:
                HFound = False
            if HFound and "p.m." in line:
                hrs = line.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                if "<" in hrs:
                    hrs = hrs.split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if HFound and "p.m." not in line and "losed" in line:
                hrs = line.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                if "<" in hrs:
                    hrs = hrs.split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "<title>" in line:
                g = next(lines)
                name = g.split(" |")[0].strip().replace("\t", "")
            if 'class="address">' in line or 'pnlAddress">' in line:
                next(lines)
                g = next(lines)
                addinfo = (
                    g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                )
                if addinfo.count("<br/>") == 1:
                    add = addinfo.split("<br/>")[0]
                    city = addinfo.split("<br/>")[1].split(",")[0]
                    state = (
                        addinfo.split("<br/>")[1].split(",")[1].strip().split(" ")[0]
                    )
                    zc = addinfo.split("<br/>")[1].rsplit(" ", 1)[1]
                else:
                    add = addinfo.split("<br/>")[0]
                    try:
                        city = addinfo.split("<br/>")[2].split(",")[0]
                        state = (
                            addinfo.split("<br/>")[2]
                            .split(",")[1]
                            .strip()
                            .split(" ")[0]
                        )
                        zc = addinfo.split("<br/>")[2].rsplit(" ", 1)[1]
                    except:
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zc = "<MISSING>"
            if '<a id="main_0_rightpanel_0_hlAlternatePhone"' in line:
                phone = line.split('"tel:')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "n/neuroscience-center" in loc:
            add = "3851 Piper Street"
            city = "Anchorage"
            state = "AK"
            zc = "99508"
            phone = "907-212-5606"
        if "3801-" in loc:
            add = "3801 Lake Otis Parkway"
            city = "Anchorage"
            state = "AK"
            zc = "99508"
        if "c/providence-cancer-center" in loc:
            add = "3851 Piper Street"
            state = "AK"
            zc = "99508"
            city = "Anchorage"
        if "anchorage/providence-diabetes-and-nutrition-center" in loc:
            add = "3220 Providence Drive"
            city = "Anchorage"
            state = "AK"
            zc = "99508"
        if "/p/providence-medical-group-u-med" in loc:
            add = "3260 Providence Drive"
            city = "Anchorage"
            state = "AK"
            zc = "99508"
        if "medical-group-primary-care" in loc:
            add = "3300 Providence Drive"
            city = "Anchorage"
            state = "AK"
            zc = "99508"
        if "providence-rehabilitation-services" in loc:
            add = "4411 Business Park Blvd"
            city = "Anchorage"
            state = "AK"
            zc = "99503"
        if "," in add:
            add = add.split(",")[0].strip()
        if " Suite" in add:
            add = add.split(" Suite")[0]
        if add != "":
            newadd = ""
            if " Suite" in add:
                add = add.split(" Suite")[0]
            if "," in add:
                addparts = add.split(",")
                for aitem in addparts:
                    if "Floor" not in aitem:
                        if newadd == "":
                            newadd = aitem
                        else:
                            newadd = newadd + "," + aitem
            else:
                newadd = add
            if "," in phone:
                phone = phone.split(",")[0].strip()
            if " Option" in phone:
                phone = phone.split(" Option")[0].strip()
            for ladd in locadds:
                if ladd.split("|")[0] == loc:
                    newadd = ladd.split("|")[1]
                    hours = ladd.split("|")[2]
            citytext = " - " + city
            name = name.replace(citytext, "")
            addfirst = add[0:5]
            if addfirst in name:
                nameorig = name
                name = name.split(addfirst)[0].strip()
                if name == "":
                    name = nameorig
            infotext = loc + "|" + name + "|" + newadd + "|" + phone
            if infotext not in alllocs:
                alllocs.append(infotext)
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    if '"latitude" content="' in line2:
                        try:
                            lat = line2.split('"latitude" content="')[1].split('"')[0]
                        except:
                            lat = "<MISSING>"
                    if '"longitude" content="' in line2:
                        try:
                            lng = line2.split('"longitude" content="')[1].split('"')[0]
                        except:
                            lng = "<MISSING>"
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=newadd,
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

    for x in range(1, 75):
        logger.info(("Pulling SCA Page %s..." % str(x)))
        url = (
            "https://www.providence.org/locations?postal=90210&lookup=&lookupvalue=&page="
            + str(x)
            + "&radius=5000&term=#"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h3><a href="' in line:
                stub = line.split('a href="')[1].split('"')[0]
                if "/location" in stub and ".providence.org" not in stub:
                    lurl = "https://www.providence.org" + stub
                    if lurl not in scalocs and lurl.count("http") == 1:
                        scalocs.append(lurl)
        logger.info(("%s SCA Locations Found" % str(len(scalocs))))
    for loc in scalocs:
        logger.info(("Pulling SCA Location %s..." % loc))
        website = "providence.org"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if '"streetAddress":"' in line:
                name = line.split('"name":"')[1].split('"')[0]
                add = line.split('"streetAddress":"')[1].split('"')[0]
                city = line.split('"addressLocality":"')[1].split('"')[0]
                state = line.split('"addressRegion":"')[1].split('"')[0]
                zc = line.split('"postalCode":"')[1].split('"')[0]
                phone = line.split('"telephone":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(",")[0]
                lng = line.split('"longitude":')[1].split("}")[0]
                typ = line.split(',"@type":"')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "," in add:
            add = add.split(",")[0].strip()
        if " Suite" in add:
            add = add.split(" Suite")[0]
        if add != "":
            newadd = ""
            if "," in add:
                addparts = add.split(",")
                for aitem in addparts:
                    if "Floor" not in aitem:
                        if newadd == "":
                            newadd = aitem
                        else:
                            newadd = newadd + "," + aitem
            else:
                newadd = add
            if "," in phone:
                phone = phone.split(",")[0].strip()
            if " Option" in phone:
                phone = phone.split(" Option")[0].strip()
            citytext = " - " + city
            name = name.replace(citytext, "")
            addfirst = add[0:5]
            if addfirst in name:
                nameorig = name
                name = name.split(addfirst)[0].strip()
                if name == "":
                    name = nameorig
            infotext = loc + "|" + name + "|" + newadd + "|" + phone
            if infotext not in alllocs:
                alllocs.append(infotext)
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    if '"latitude" content="' in line2:
                        lat = line2.split('"latitude" content="')[1].split('"')[0]
                        lng = line2.split('"longitude" content="')[1].split('"')[0]
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=newadd,
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

    r = session.get("https://www.stjosephhealth.org/our-locations/", headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if '<div class="location">' in line:
            g = next(lines)
            if "<h3>" in g:
                typ = "<MISSING>"
                name = g.split('">')[1].split("<")[0]
            else:
                g = next(lines)
                name = g.split(">")[1].split("<")[0]
                typ = name
                if " - " in typ:
                    typ = typ.split(" - ")[0]
            next(lines)
            g = next(lines)
            if "<p>" not in g:
                next(lines)
            g = next(lines)
            add = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
            g = next(lines)
            csz = (
                g.split("<br>")[1]
                .strip()
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
            )
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.rsplit(" ", 1)[1]
            country = "US"
            website = "providence.org"
        if "Phone:" in line:
            try:
                phone = line.split("tel:")[1].split('"')[0]
            except:
                phone = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = "<MISSING>"
            loc = "<MISSING>"
            store = "<MISSING>"
            newadd = ""
            if "," in add:
                add = add.split(",")[0].strip()
            if " Suite" in add:
                add = add.split(" Suite")[0]
            if "," in add:
                addparts = add.split(",")
                for aitem in addparts:
                    if "Floor" not in aitem:
                        if newadd == "":
                            newadd = aitem
                        else:
                            newadd = newadd + "," + aitem
            else:
                newadd = add
            if "," in phone:
                phone = phone.split(",")[0].strip()
            if " Option" in phone:
                phone = phone.split(" Option")[0].strip()
            citytext = " - " + city
            name = name.replace(citytext, "")
            addfirst = add[0:5]
            if addfirst in name:
                nameorig = name
                name = name.split(addfirst)[0].strip()
                if name == "":
                    name = nameorig
            infotext = loc + "|" + name + "|" + newadd + "|" + phone
            if infotext not in alllocs:
                alllocs.append(infotext)
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    if '"latitude" content="' in line2:
                        lat = line2.split('"latitude" content="')[1].split('"')[0]
                        lng = line2.split('"longitude" content="')[1].split('"')[0]
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=newadd,
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
