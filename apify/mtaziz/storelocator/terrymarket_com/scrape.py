from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import html


logger = SgLogSetup().get_logger("terrymarket_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

DOMAIN = "https://terrymarket.com"
base_url = "https://terrymarket.com/locations.html"
MISSING = "<MISSING>"

session = SgRequests()


def get_address_phone(data_address_phone_raw):
    data_phone = "".join(data_address_phone_raw)
    data_phone = (
        data_phone.replace("#1-Terry's Supermarket Grand Central Ctr.", "")
        .replace("#2-Terry's Supermarket Western Park Vlg.", "")
        .replace("#3-Terry's Supermarket Riverside", "")
        .replace("#9-Terry's Supermarket Plano", "")
        .replace("#11-El Mariachi #2, OK", "")
    )
    logger.info(f"Address and Phone Data: {data_phone}")
    data_phone = data_phone.split("\r\n")
    data_phone = [" ".join(i.split()) for i in data_phone]
    data_phone = [i for i in data_phone if i]
    data_phone = [i.split("Fax") for i in data_phone]
    address_list = []
    for idx, i in enumerate(data_phone):
        if idx == 0:
            address_list.append(i[0])
        if idx == 1:
            address_list.append(i[0])
        if idx == 2:
            for idx1, j in enumerate(i):
                if idx1 == 0:
                    address_list.append(j)
                if idx1 == 1:
                    ij1 = " ".join(" ".join(j.split()).split(" ")[2:])
                    address_list.append(ij1)
                if idx1 == 2:
                    ij2 = " ".join(" ".join(j.split()).split(" ")[2:])
                    address_list.append(ij2)
                if idx1 == 3:
                    ij3 = " ".join(" ".join(j.split()).split(" ")[2:])
                    address_list.append(ij3)
        if idx == 3:
            address_list.append(i[0])
        if idx == 4:
            for idx2, k in enumerate(i):
                if idx2 == 0:
                    address_list.append(k.strip())
                if idx2 == 1:
                    ijk1 = " ".join(" ".join(k.split()).split(" ")[2:])
                    address_list.append(ijk1)
                if idx2 == 2:
                    ijk2 = " ".join(" ".join(k.split()).split(" ")[2:])
                    address_list.append(ijk2)
    address_list = [i.strip() for i in address_list]
    return address_list


def get_lat_lng(page_urls_temp):
    latlng = []
    for mapurl in page_urls_temp:
        if "mapquest" in mapurl:
            r_latlng = session.get(mapurl)
            sel_latlng = html.fromstring(r_latlng.text, "lxml")
            lat = sel_latlng.xpath(
                '//meta[@property="place:location:latitude"]/@content'
            )[0]
            lng = sel_latlng.xpath(
                '//meta[@property="place:location:longitude"]/@content'
            )[0]

        if "maps.yahoo" in mapurl:
            lat = mapurl.split("&lat=")[-1].split("&lon")[0]
            lng = mapurl.split("&lon=")[-1].split("&mag")[0]
        latlng.append((lat, lng))
    return latlng


def fetch_data():
    r = session.get(base_url, headers=headers, timeout=20)
    sel = html.fromstring(r.text, "lxml")
    xpath_address_phone = '//table[tr[td[starts-with(text(), "Phone:") or starts-with(text(), " Phone:")]]]/tr/td//text()'
    data_address_phone = sel.xpath(xpath_address_phone)
    data = get_address_phone(data_address_phone)
    for store_num, d in enumerate(data):
        # Locator Domain
        locator_domain = DOMAIN

        # Page URL
        xpath_page_url = '//a[contains(@href, "http://www.mapquest.com/maps?") or contains(@href, "maps.yahoo")]/@href'
        page_urls = sel.xpath(xpath_page_url)
        page_urls_raw = sel.xpath(xpath_page_url)
        page_urls = []
        for url in page_urls_raw:
            if url not in page_urls:
                page_urls.append(url)
        page_urls = [i for i in page_urls if "/;_ylc" not in i]
        page_url = page_urls[store_num] or MISSING
        logger.info(
            f"{store_num} out of {len(data)} Stores][Pulling the data from: {page_url} "
        )

        # Location Name
        xpath_location_names = '//a[contains(@href, "http://www.mapquest.com/maps?") or contains(@href, "maps.yahoo")]//text()'
        location_names = sel.xpath(xpath_location_names)
        location_names = [i.strip() for i in location_names]
        locname_new = []
        for idxln, locname in enumerate(location_names):
            if idxln == 0 or idxln == 1 or idxln == 2 or idxln == 3 or idxln == 4:
                locname_new.append(locname)
            if idxln == 5:
                locname = locname.strip() + "Terry's Supermarket Lewisville"
                locname = locname.replace("#7 ", "#7")
                locname_new.append(locname)
            if idxln == 7:
                locname_new.append(locname)
            if idxln == 8:
                locname = locname.replace(
                    "3020 NW 16th Street", "#11-El Mariachi #2, OK"
                )
                locname_new.append(locname)
            if idxln == 9 or idxln == 11:
                locname_new.append(locname)

        location_name = locname_new[store_num].strip()
        location_name = location_name if location_name else MISSING
        logger.info(f"[Location Name: {location_name}]")

        # Parse address using sgpostal
        address = d.split("Phone:")[0].strip()
        address = address.replace("100Dallas", "100 Dallas")
        address = address.replace("Dr.Fort", "Dr. Fort")
        address = address.replace("160Grand Prairie", "160 Grand Prairie")
        pai = parse_address_intl(address)

        # Street Address
        street_address = pai.street_address_1
        street_address = street_address.replace(
            "1830 E. Main St.", "1830 E. Main St., Suite 160"
        )
        street_address = street_address.replace(
            "4444 W. Illinois Ave.", "4444 W. Illinois Ave., Suite 100"
        )
        street_address = street_address if street_address else MISSING
        logger.info(f"[Street Address: {street_address}]")

        # City
        try:
            city = pai.city
        except Exception:
            city = MISSING
        logger.info(f"[City: {city}]")

        # State
        state = pai.state
        state = state.replace("Texas", "TX")
        state = state if state else MISSING
        logger.info(f"[State: {state}]")

        # Zipcode
        zip_postal = pai.postcode
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"[Zip: {zip_postal}]")

        # Country Code
        country_code = "US"

        # Store Number
        store_number = location_name.strip().split("-")[0]
        store_number = store_number.replace("#", "").strip()
        store_number = store_number if store_number else MISSING
        logger.info(f"[Store Number: {store_number}]")

        # Phone

        phone = d.split("Phone:")[-1].strip()
        phone = phone if phone else MISSING
        logger.info(f"[Phone Number: {phone}]")

        # Location Type
        location_type = MISSING

        # Latitude
        data_latlng = get_lat_lng(page_urls)
        latitude = data_latlng[store_num][0]
        latitude = latitude if latitude else MISSING
        logger.info(f"[Latitude: {latitude}]")

        # Longitude
        longitude = data_latlng[store_num][1]
        longitude = longitude if longitude else MISSING
        logger.info(f"[Longitude: {longitude}]")

        # Hours of operation
        hoo = ""
        hours_of_operation = hoo if hoo else MISSING
        logger.info(f"[Hours of Operation: {hours_of_operation}]")

        # Raw Address
        raw_address = address
        raw_address = raw_address if raw_address else MISSING
        logger.info(f"[Raw Address: {raw_address}]")
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
