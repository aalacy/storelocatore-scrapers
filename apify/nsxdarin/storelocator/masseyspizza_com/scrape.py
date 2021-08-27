from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.masseyspizza.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    name = ""
    state = "OH"
    add = ""
    city = ""
    country = "US"
    store = "<MISSING>"
    phone = ""
    loc = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    website = "masseyspizza.com"
    typ = "Restaurant"
    zc = ""
    hours = ""
    name = "SULLIVANT AVE."
    add = "2970 Sullivant Avenue"
    city = "Columbus"
    state = "OH"
    zc = "<MISSING>"
    phone = "(614) 358-3333"
    hours = "Sun-Thu: 11am-10pm; Fri & Sat: 11am-11pm"
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
    name = "BEECHCROFT/RT. 161"
    add = "1951 E. Dublin-Granville Rd."
    city = "Columbus"
    state = "OH"
    zc = "<MISSING>"
    phone = "(614) 888-0022"
    hours = "11am-10pm Everyday"
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
    for line in lines:
        if "South Carolina</span>" in line:
            state = "SC"
        if ">Ohio Sports Bars" in line:
            state = "OH"
        if (
            '<div class="et_pb_text_inner"><p>' in line
            or '<footer id="main-footer">' in line
        ):
            if name != "":
                if "AVE." in city:
                    city = "COLUMBUS"
                if "/" in city:
                    city = city.split("/")[0]
                if "261 Lincoln" in add:
                    zc = "43230"
                if "!" in zc:
                    zc = zc.split("!")[0]
                if "1951 E" in add or "261 Lincoln" in add:
                    city = "<MISSING>"
                if "Pawleys Island/Litchfield" in name:
                    add = "115 Willbrook Blvd Unit O"
                    city = "Pawleys Island"
                    state = "SC"
                    zc = "<MISSING>"
                    hours = "Tue: Closed; Mon, Wed & Thurs: 4pm-8pm; Fri, Sat & Sun: 11am-9pm"
                if "261 Lincoln" in add:
                    hours = "Sun-Thu: 11am-10pm; Fri-Sat: 11am-MIDNIGHT"
                hours = hours.replace("&amp;", "&")
                if "<span" in hours:
                    hours = hours.split("<span")[0]
                if "; DINI" in hours:
                    hours = hours.split("; DINI")[0]
                if "261 Lincoln" in add:
                    lat = "40.0176083"
                    lng = "-82.8750958"
                if "2970" in add:
                    lat = "39.9438144"
                    lng = "-83.0800593"
                if "1299 N" in add:
                    lat = "39.7274719"
                    lng = "-82.6146089"
                if "1951 E" in add:
                    lat = "40.0903889"
                    lng = "-82.9694044"
                if "399 S" in add:
                    lat = "40.1153043"
                    lng = "-82.9304702"
                if "9838" in add:
                    lat = "40.1546363"
                    lng = "-83.0961791"
                if "440 E" in add:
                    lat = "40.0064944"
                    lng = "-82.6648511"
                if "Willbrook" in add:
                    lat = "33.4838211"
                    lng = "-79.0983286"
                if add != "":
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
        if "google.com/maps" in line and "/@" in line:
            lat = line.split("/@")[1].split(",")[0]
            lng = line.split("/@")[1].split(",")[1]
        if '<div class="et_pb_text_inner"><p>' in line:
            if '<div class="et_pb_text_inner"><p><strong>' in line:
                name = line.split('<div class="et_pb_text_inner"><p><strong>')[1].split(
                    "<"
                )[0]
            else:
                g = next(lines)
                name = g.split("<strong>")[1].split("<")[0]
            add = ""
            city = name
            store = "<MISSING>"
            lat = ""
            lng = ""
            if "google.com/maps" in g and "/@" in g:
                lat = g.split("/@")[1].split(",")[0]
                lng = g.split("/@")[1].split(",")[1]
            if "771 South" in g:
                hours = "SUN-THUR 11am-11pm; FRI &amp; SAT 11am-Midnight"
            elif "4015 Parkmead" in g:
                hours = "SUN-THUR 11am-11pm; FRI &amp; SAT 11am-Midnight"
            elif "6394 Gender Rd" in g:
                hours = "Sun-Thu: 11am-10pm; Fri &amp; Sat 11am-11pm"
            elif "152 Graceland Blvd" in g:
                hours = "Sun-Thu: 11am-10pm; Fri &amp; Sat 11am-11pm"
            else:
                hours = (
                    g.split("</a><br />")[1]
                    .split("<br /><a")[0]
                    .strip()
                    .replace("<br />", "; ")
                )
            country = "US"
            zc = "<MISSING>"
            phone = g.split('<a href="tel:+1')[1].split('"')[0]
            website = "masseyspizza.com"
            typ = "Restaurant"
            loc = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            if name == "DELAWARE":
                city = "Delaware"
                add = "219 S. Sandusky Street"
            else:
                if "</strong><br />" not in g:
                    add = g.split("<")[0]
                else:
                    add = g.split("</strong><br />")[1].split("<")[0]
        if "pm<" in line or "idnight<" in line or "am<" in line:
            hrs = line.split("<")[0]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
            hours = hours.replace("&amp;", "&")
        if "/@" in line:
            try:
                lat = line.split("/@")[1].split(",")[0]
                lng = line.split("/@")[1].split(",")[1]
            except:
                lat = "<MISSING>"
                lng = "<MISSING>"
            if ",+OH+" in line:
                zc = line.split(",+OH+")[1].split("/")[0]
        if '<a href="tel:+' in line:
            phone = line.split('<a href="tel:+')[1].split('"')[0]


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
