from lxml import html
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("kfc_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.kfc.com"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

session = SgRequests()


def fetch_data():
    url = "https://locations.kfc.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'href="https://locations.kfc.com/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count("/") >= 5:
                locs.append(lurl)
    locs = [url for url in locs if "/delivery" not in url]
    locs = [url.replace("amp;", "").replace("&#39;", "'") for url in locs]
    logger.info(("Found %s Locations." % str(len(locs))))
    for idx, loc in enumerate(locs):
        r2 = session.get(loc, headers=headers)
        logger.info(f"Pulling the data from {idx} : {loc}")
        sel = html.fromstring(r2.text, "lxml")
        json_raw = sel.xpath(
            '//script[@id="js-map-config-dir-map-desktop-map"]/text()'
        )[0]
        data_json = json.loads(json_raw)
        entities = data_json["entities"]
        profile = entities[0]["profile"]
        address = profile["address"]

        locator_domain = DOMAIN
        page_url = loc
        page_url = page_url if page_url else MISSING

        location_name = profile["name"]
        location_name = location_name if location_name else MISSING

        street_address = address["line1"]
        street_address = street_address if street_address else MISSING

        city = address["city"]
        city = city if city else MISSING

        state = address["region"]
        state = state if state else MISSING

        zip_postal = address["postalCode"]
        zip_postal = zip_postal if zip_postal else MISSING

        country_code = address["countryCode"]
        country_code = country_code if country_code else MISSING

        store_number = ""
        store_number = profile["meta"]["id"]
        store_number = store_number if store_number else MISSING

        try:
            main_phone = profile["mainPhone"]
            phone = main_phone["display"]
            phone = phone if phone else MISSING
        except KeyError:
            phone = MISSING

        try:
            meta = profile["meta"]
            location_type = meta["entityType"]
            location_type = location_type if location_type else MISSING
        except KeyError:
            location_type = MISSING

        y_ext_display_Coordinate = profile["yextDisplayCoordinate"]

        try:
            latitude = y_ext_display_Coordinate["lat"]
            latitude = latitude if latitude else MISSING
        except KeyError:
            latitude = MISSING

        try:
            longitude = y_ext_display_Coordinate["long"]
            longitude = longitude if longitude else MISSING
        except KeyError:
            longitude = MISSING

        hours_of_operation = ""
        hoo = []
        c_hours_details = sel.xpath('//table[@class="c-hours-details"]/tbody/tr')
        for tr in c_hours_details:
            hrs_details = tr.xpath(".//td//text()")
            hrs_details = " ".join(hrs_details)
            hrs_details = hrs_details.replace("  -  ", " - ")
            hoo.append(hrs_details)
        hours_of_operation = "; ".join(hoo)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        raw_address = ""
        raw_address = raw_address if raw_address else MISSING

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
