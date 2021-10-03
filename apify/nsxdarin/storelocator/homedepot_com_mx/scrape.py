# -*- coding: cp1252 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("homedepot_com_mx")


def fetch_data():
    cities = []
    session = SgRequests()
    url = "https://www.homedepot.com.mx/wcsstore/HDM-SAS/javascript/StoreLocatorStateCitiesList.js"
    r = session.get(url, headers=headers)
    website = "homedepot.com.mx"
    typ = "<MISSING>"
    country = "MX"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "formCitiesObject:" in line:
            items = line.split("formCitiesObject:{")[1].split("}};")[0].split(':"')
            for item in items:
                if "-" in item:
                    if "|" in item:
                        items2 = item.split("|")
                        for item2 in items2:
                            cities.append(item2.split("-")[0])
                    else:
                        cities.append(item.split("-")[0])
    for city in cities:
        url2 = "https://www.homedepot.com.mx/AjaxStoreLocatorResultsView?catalogId=10101&orderId=&storeId=10351&langId=-5"
        headers2 = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        }
        payload = {
            "requesttype": "ajax",
            "cityId": city,
            "filtroLoc": "",
            "fromPage": "StoreLocator",
            "geoCodeLatitude": "",
            "geoCodeLongitude": "",
            "errorMsgKey": "",
        }
        session = SgRequests()
        time.sleep(5)
        r2 = session.post(url2, headers=headers2, data=payload)
        logger.info(city)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        loc = "<MISSING>"
        alltext = ""
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            alltext = alltext + line2.replace("\r", "").replace("\n", "")
        if '<span class="col">' in alltext:
            items = alltext.split('<span class="col">')
            for item in items:
                if '<br clear="all">' in item:
                    name = (
                        item.split("<")[0]
                        .strip()
                        .replace("\t", "")
                        .replace("&nbsp;", " ")
                    )
                    store = name.split("#")[1]
                    add = item.split("<p>")[1].split("<")[0].strip().replace("\t", "")
                    csz = (
                        item.split('<br clear="all">')[1]
                        .split("<")[0]
                        .strip()
                        .replace("\t", "")
                    )
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().split(".")[0].replace("CP", "")
                    zc = csz.rsplit(".", 1)[1].strip()
                    phone = (
                        item.split('<a href="tel:')[1]
                        .split('"')[0]
                        .replace("\t", "")
                        .strip()
                    )
                    lat = item.split("&daddr=")[1].split("+")[0]
                    lng = item.split("&daddr=")[1].split("+")[1].split('"')[0]
                    hours = (
                        item.split(
                            '<td headers="PhysicalStores_tableCell_result2" class=dotted_bottom_border>'
                        )[1]
                        .split("</td>")[0]
                        .strip()
                        .replace("\t", "")
                        .replace("pmD", "pm; D")
                    )
                    hours = (
                        hours.replace("Sábado", "Sat")
                        .replace("Lunes", "Mon")
                        .replace("Domingo", "Sun")
                    )
                    hours = hours.replace("Mon a Sat", "Mon-Sat").replace(
                        "Mon a Sun", "Mon-Sun"
                    )
                    hours = hours.replace(" de ", ": ").replace("am a ", "am - ")
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


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
