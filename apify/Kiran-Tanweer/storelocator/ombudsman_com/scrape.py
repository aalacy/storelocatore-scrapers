import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser

session = SgRequests()
website = "ombudsman_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.ombudsman.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.ombudsman.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.select("a[href*=state]")
    for st in statelist:
        stlink = st["href"]
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        if r.url == "https://az.ombudsman.com/locations/":
            loclist = r.text.split('<script type="application/ld+json">')[1:]
            phone_list = soup.findAll("div", {"class": "cl-lgmap_location-list-item"})
            for loc, temp in zip(loclist, phone_list):
                temp = temp.get_text(separator="|", strip=True).split("|")
                phone = temp[-1]
                if "Fax:" in phone:
                    phone = temp[-2]
                loc = json.loads(loc.split("</script>")[0])
                location_name = loc["name"]
                page_url = loc["url"]
                log.info(page_url)
                address = loc["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                latitude = loc["geo"]["latitude"]
                longitude = loc["geo"]["longitude"]
                location_name = location_name.replace("&#8211;", "-")
                yield SgRecord(
                    locator_domain="https://www.ombudsman.com/",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

        else:
            r = session.get(r.url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("div", {"id": "content"})
            locations = loclist.findAll("div", {"class": "location-group clearfix"})
            coords = soup.find("script", {"id": "mappress-js-after"})
            coords = str(coords)
            coords = coords.replace(
                '<script id="mappress-js-after" type="text/javascript">//', ""
            )
            coords = coords.replace(
                "window.mapp = window.mapp || {}; mapp.data = mapp.data || [];", ""
            )
            coords = coords.replace(
                "if (typeof mapp.load != 'undefined') { mapp.load(); };", ""
            )
            coords = coords.replace("//</script>", "")
            coords = coords.replace("mapp.data.push( ", "")
            coords = coords.replace(");", "")
            coords = json.loads(coords)
            for loc in locations:
                stores = loc.findAll("li")
                for store in stores:
                    location_name = store.find("h4").text.strip()
                    location_name = location_name.replace("&#8211;", "-")
                    details = store.find("p")
                    details = str(details)
                    details = details.replace("</p>", "")
                    details = details.replace("<p>", "").strip()
                    details = details.split("<br/>")
                    address = details[0] + " " + details[1]
                    if len(details) == 3:
                        if details[-1].find("-") != -1:
                            phone = details[-1].strip()
                        else:
                            address = details[0] + " " + details[1] + " " + details[2]
                    else:
                        phone = MISSING
                    address = address.replace("  ", " ").strip()
                    address = address.replace(",", "")
                    address = address.strip()
                    parsed = parser.parse_address_usa(address)
                    street1 = (
                        parsed.street_address_1
                        if parsed.street_address_1
                        else "<MISSING>"
                    )
                    street = (
                        (street1 + ", " + parsed.street_address_2)
                        if parsed.street_address_2
                        else street1
                    )
                    city = parsed.city if parsed.city else "<MISSING>"
                    state = parsed.state if parsed.state else "<MISSING>"
                    pcode = parsed.postcode if parsed.postcode else "<MISSING>"

                    for geo in coords["pois"]:
                        title = geo["title"]
                        title = title.replace("&#8211;", "-")
                        if location_name.strip() == title.strip():
                            lat = geo["point"]["lat"]
                            lng = geo["point"]["lng"]
                            continue

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=r.url,
                        location_name=location_name,
                        street_address=street.strip(),
                        city=city.replace(",", "").strip(),
                        state=state.strip(),
                        zip_postal=pcode.strip(),
                        country_code="US",
                        store_number=SgRecord.MISSING,
                        phone=phone.strip(),
                        location_type=SgRecord.MISSING,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=SgRecord.MISSING,
                    )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
