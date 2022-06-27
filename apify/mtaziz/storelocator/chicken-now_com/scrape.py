from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import ssl
import re

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "http://chicken-now.com"
base_url = "http://chicken-now.com/locations.html"
logger = SgLogSetup().get_logger("")


headers2 = {
    "referer": "http://chicken-now.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}


def get_locs():
    with SgRequests() as http:
        r = http.get(base_url, headers=headers2)
        soup = bs(r.text, "lxml")
        locations = soup.select("div#locations a")
        logger.info(f"Total Stores to be Crawled: {len(locations)}")  # noqa
        logger.info(f"Crawling GMapUrls finished!")  # noqa
        radd_from_gmapurl = []
        for loc in locations:
            gmapurl = loc["href"]
            locname = loc["title"]
            radd_from_gmapurl.append((gmapurl, locname))
        return radd_from_gmapurl


def get_hoo(tel_last_part):
    hours = tel_last_part.split("[[[")
    hours2 = hours[2]
    hours3 = hours2.split("[[11]")[0:7]
    hoo = []
    for h3 in hours3:
        h3_split = h3.split(",")
        day = ""
        pm = ""
        for i in h3_split:
            if "day" in i:
                day = (
                    i.replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
            if "PM" in i:
                pm = (
                    i.replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
        logger.info(f"Daytime: {day} {pm}")
        (day, pm)
        day_pm = day + " " + pm
        hoo.append(day_pm)
    hoo = ", ".join(hoo)
    return hoo


def remove_hash(t):
    found = "".join(re.findall(r"#\d+\w+", t))
    logger.info(f"found: {found}")
    t1 = ""
    if found:
        t1 = t.replace(found, ",").replace(" ,", ",")
    elif "#F19" in t:
        t1 = t.replace("#F19", ",").replace(" ,", ",")
    else:
        t1 = t
    return t1


def get_latlng(map_link):
    if "z/data" in map_link:
        latlng = map_link.split("@")[1].split("z/data")[0]
        lat = latlng.split(",")[0].strip()
        lng = latlng.split(",")[1].strip()
    elif "ll=" in map_link:
        latlng = map_link.split("ll=")[1].split("&")[0]
        lat = latlng.split(",")[0]
        lng = latlng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        lat = map_link.split("!3d")[1].strip().split("!")[0].strip()
        lng = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        lat = map_link.split("/@")[1].split(",")[0].strip()
        lng = map_link.split("/@")[1].split(",")[1].strip()
    else:
        lat = "<MISSING>"
        lng = "<MISSING>"
    return lat, lng


def fetch_data():
    urls = get_locs()
    for idx, pgurl_ln in enumerate(urls[0:]):
        with SgRequests(proxy_country="us") as http:
            purl, locname = pgurl_ln
            r = http.get(purl)
            text = r.text
            try:
                tel_last_part = text.split("tel:")[-1]
                tlp = tel_last_part.split('"')
                tel = "".join(tlp[0].split()).replace("\\", "")

                add_part = tel_last_part.split("[[[")
                add_part2 = add_part[1]
                add_part3 = add_part2.split(",")
                location_name = (
                    add_part3[1]
                    .replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
                street_address = (
                    add_part3[2]
                    .replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
                city = (
                    add_part3[3]
                    .replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
                zc_state = (
                    add_part3[4]
                    .replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )
                zc = zc_state.strip().split(" ")[-1]
                state = zc_state.strip().split(" ")[0]
                hours_of_operation = get_hoo(tel_last_part)
                raw_address = (
                    add_part2.split('[[\\"')[3]
                    .split(",[")[0]
                    .replace("[", "")
                    .replace('"', "")
                    .replace("\\", "")
                    .replace("]", "")
                )

                latlng = (
                    text.split("APP_INITIALIZATION_STATE")[-1].split("]")[0].split(",")
                )
                longitude = latlng[-2]
                latitude = latlng[-1]
                if state.strip() == "617":
                    state = ""
                if "617" in state.strip():
                    state = ""

                if "Confirmed" in hours_of_operation:
                    hours_of_operation = ""
                if zc in city:
                    city = ""
                item = SgRecord(
                    locator_domain="chicken-now.com",
                    page_url=purl,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code="US",
                    store_number="",
                    phone=tel,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
                logger.info(f"[{idx}] ITEM: {item.as_dict()}")
                yield item
            except:
                logger.info(f"Problematic URL: {purl}")
                try:
                    add_from_url = purl.split("&q=")[-1].split("&")[0].replace("+", " ")
                    if "maps.google" not in add_from_url:
                        add_from_url = remove_hash(add_from_url)
                        sta = add_from_url.split(",")[0].strip()
                        city = add_from_url.split(",")[1].strip()
                        state_zc = add_from_url.split(",")[-1].strip().split(" ")
                        state = state_zc[0].strip()
                        zc = state_zc[-1].strip()
                        lat, lng = get_latlng(purl)
                        ln = locname.split(",")[0].strip()
                        if zc in city:
                            city = ""
                        item = SgRecord(
                            locator_domain="chicken-now.com",
                            page_url=purl,
                            location_name=ln,
                            street_address=sta,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code="US",
                            store_number="",
                            phone="",
                            location_type="",
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation="",
                            raw_address=add_from_url,
                        )
                        logger.info(f"[{idx}] ITEM: {item.as_dict()}")
                        yield item
                except Exception as e:
                    logger.info(f"FixError at {purl} || <{e}>")


def scrape():
    logger.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
