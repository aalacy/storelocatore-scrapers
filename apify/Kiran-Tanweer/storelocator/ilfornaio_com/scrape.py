from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import re


session = SgRequests()
website = "ilfornaio_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
headers2 = {
    "authority": "www.ilfornaio.com",
    "method": "GET",
    "path": "/location/il-fornaio-san-jose/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'csrftoken=NOpfIFE2oPkU5nWUF4Trmo598PNaRiSzCTii9uscIJjlRDROmyp3VCvu8eliOYE3; _ga=GA1.2.1661647810.1614820370; _fbp=fb.1.1614820371304.543547716; Indicative_62e150f7-1993-460b-90ab-1bb1bd494ad7="%7B%22defaultUniqueID%22%3A%2220fd67db-68b7-4f8e-9c5e-03cea3951924%22%7D"; _aeaid=7038d6b4-8ae0-4fda-9461-6f9d38649ac4; aeatstartmessage=true; _gid=GA1.2.1947720619.1615058256',
    "referer": "https://www.ilfornaio.com/locations/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
}

DOMAIN = "www.ilfornaio.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        url = "https://www.ilfornaio.com/locations/"
        stores_req = session.get(url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        scripts = soup.findAll("script", {"type": "application/ld+json"})
        locations = str(scripts)
        locations = locations.lstrip(
            '<script type="application/ld+json">{"@context": "http://schema.org", "@type": "Organization", "@id": "https://www.ilfornaio.com/#organization", "url": "https://www.ilfornaio.com", "name": "Il Fornaio", "description": "Founded in Italy in 1972, Il Fornaio Authentic Italian Restaurants are located throughout the United States in California, Las Vegas \u0026 Denver.", "logo": "https://images.getbento.com/accounts/23ff2389c98ff1551eb861c58a668822/media/images/66267logo.png?w=600\u0026fit=max\u0026auto=compress,format\u0026h=600", "subOrganization": [{"@type": "FoodEstablishment", "@id": "https://www.ilfornaio.com/location/il-fornaio-beverly-hills/#foodestablishment",'
        )
        locations = locations.rstrip("</script>")
        locations = locations.split('{"@id"')
        for loc in locations:
            link = loc.split('"url": "')[1].split('", "name')[0]
            if (
                link
                != 'https://www.ilfornaio.com/#action-reservations"}, "result": {"@type": "Reservation'
            ):
                r = session.get(link, headers=headers2)
                bs = BeautifulSoup(r.text, "html.parser")
                loc_div = bs.find("section", {"id": "intro"})
                title = loc_div.find("h2").text
                ptag = loc_div.findAll("p")
                address = ptag[0].findAll("a")[0].text
                phone = ptag[0].findAll("a")[1].text
                hours = loc_div.findAll("p")
                hoo = ""
                for hr in hours:
                    ho = hr.text
                    hoo = hoo + " " + ho
                try:
                    hoo = hoo.split("Delivery Available")[1]
                except IndexError:
                    hoo = hoo.split("Dine In")[1]

                hoo = hoo.split("pm ")[0].strip()
                hoo = hoo + "pm"

                hoo = hoo.replace("Every Day", "Monday-Sunday").strip()
                hoo = hoo.replace("Everyday", "Monday-Sunday").strip()

                if hoo == "":
                    hoo = "Temporarily Closed"

                hoo = re.sub(pattern, " ", hoo)
                hoo = re.sub(cleanr, " ", hoo)
                maps = bs.find("div", {"class": "gmaps"})
                lat = maps["data-gmaps-lat"]
                lng = maps["data-gmaps-lng"]
                address = re.sub(pattern, " ", address)
                address = re.sub(cleanr, " ", address)
                address = address.strip()
                address = address.split(",")
                if len(address) == 4:
                    street = address[0] + "" + address[1]
                    city = address[2].strip()
                    locality = address[3].strip()
                else:
                    street = address[0]
                    city = address[1].strip()
                    locality = address[2].strip()
                locality = locality.split(" ")
                state = locality[0]
                pcode = locality[1]
                if street.find("P.O. Box") != -1:
                    street = street.split("P.O. Box")[0]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo.strip(),
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
