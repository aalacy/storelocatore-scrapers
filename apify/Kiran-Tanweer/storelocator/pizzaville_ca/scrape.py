from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "shopbedmart_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "authority": "www.pizzaville.ca",
    "method": "GET",
    "path": "/stores",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__utmc=91295899; __utmz=91295899.1612812537.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PIZZAVILLE=crgplomrcjfmhd6bkkbhflme92; __utma=91295899.848614800.1612812537.1612812537.1613634105.2; __utmt=1; _fbp=fb.1.1613634105844.272618394; __utmb=91295899.4.9.1613634155300; AWSALB=zjysWyE51ZP1cfJeyeSd+nL/JYxvNcRoIo1sNzV1Vx9TerlzLC9t/3KZX2Rb8Wi5IQqFQFBwH6A6zIBv6pjIdWuGtFzfmfoT/e7Mgq6B0HXNh0MkA3qB9AmgUCGu; AWSALBCORS=zjysWyE51ZP1cfJeyeSd+nL/JYxvNcRoIo1sNzV1Vx9TerlzLC9t/3KZX2Rb8Wi5IQqFQFBwH6A6zIBv6pjIdWuGtFzfmfoT/e7Mgq6B0HXNh0MkA3qB9AmgUCGu",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

DOMAIN = "https://shopbedmart.com/"
MISSING = "<MISSING>"


def fetch_data():
    url = "https://www.pizzaville.ca/stores"
    r = session.get(url, headers=headers)
    locations = r.text.split("var locations = [")[1].split("];")[0]
    location = locations.split("],")
    location.pop(-1)
    for loc in location:
        loc = loc.strip()
        coords = loc.split("<br/>',")[1].split(",'<a")[0].strip()
        coords = coords.split(",")
        latitude = coords[0]
        longitude = coords[1]
        page_url = loc.split('<a href="')[1].split('" class')[0].strip()
        page_url = "https://www.pizzaville.ca" + page_url
        log.info(page_url)
        address = loc.split('"small-title">')[1].split("Tel:")[0]
        address = address.split("</span>")[1]
        address = address.rstrip("<br />")
        street_address = address.replace("<br />", ", ")
        street_address = street_address.split(",")[0]
        state = MISSING
        zip_postal = MISSING
        r = session.get(page_url, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        div_right = bs.find("div", {"class": "column right"})
        info = div_right.findAll("span")
        location_name = info[-3].text
        city = info[-2].text
        country_code = "US"
        phone = info[-1].text
        div_left = bs.find("div", {"class": "column left"})
        hours_of_operation = div_left.text.strip()
        hours_of_operation = hours_of_operation.replace("\n", " ")
        if hours_of_operation == "":
            hours_of_operation = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
