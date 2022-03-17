from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import json
import re


session = SgRequests()
website = "hobbylobby_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
headers2 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "visid_incap_792568=K0kiUrJzQcmLknQpYDlUSr35cWEAAAAAQUIPAAAAAADkfMkByTD7isJCHVaMe3Lz; incap_ses_8077_792568=fqQAeJWkIgJfObhw8UQXcL35cWEAAAAAtSZ047eU7wPMQawWujE7fg==; JSESSIONID=F563D33FC925F9F93B9E1AE9E8777173; dtCookie=v_4_srv_5_sn_5F737B7FEC153ADC6B50366811A0EF42_perc_100000_ol_0_mul_1_app-3A1831ff6ef613563c_0; nlbi_792568=0l4/SXLXsl8KUUXklXzcngAAAAAwu4CW2q3Rst/NvL7mshyZ; incap_ses_976_792568=ycxQOELtQSt/T8uhSHOLDUv6cWEAAAAAK0ULQzxevUxqTC3ZHv23nw==; rxVisitor=16348595966908NDQSNNU0AAUKF88NQNRI4KLI114MOT5; _gcl_au=1.1.1240392688.1634859604; _evga_e8e1=728d88c2b17aed51.; _gid=GA1.2.1707895429.1634859608; scarab.visitor=%223761CF15D8933EDA%22; _pin_unauth=dWlkPU1UWTRaREU0TldNdE9USTBZUzAwTlRabUxXSXhZV010TWpCbE9XRmlOamd6TVRGaw; _fbp=fb.1.1634859609219.500920379; OptanonAlertBoxClosed=2021-10-21T23:40:26.547Z; dtLatC=21; _uetsid=3869594032c811ecb7aec3ee4309a4fa; _uetvid=38698b0032c811ec9780b588a4e347f7; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+22+2021+04%3A40%3A57+GMT%2B0500+(Pakistan+Standard+Time)&version=6.21.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&AwaitingReconsent=false&geolocation=%3B; AWSALB=ywhD0z41Sp/YqTvLQ8zXYe9ouWY3F15tI4qqDRzryzVGzHQtfais/ArOvyOJfYvRiYzbSl4UIrTr6n4Aph6NtwFZxDszfq+Sk4zPabK0vRyEqqoxxLC2MgEelaef; AWSALBCORS=ywhD0z41Sp/YqTvLQ8zXYe9ouWY3F15tI4qqDRzryzVGzHQtfais/ArOvyOJfYvRiYzbSl4UIrTr6n4Aph6NtwFZxDszfq+Sk4zPabK0vRyEqqoxxLC2MgEelaef; _ga=GA1.2.204238879.1634859605; _gat_UA-2759128-1=1; rxvt=1634863061996|1634859596692; dtPC=5$459653922_227h20vCCCKHNIILOEWSHVGABCHSVMNFPAOEJPH-0e0; _ga_9WNNN9XWSH=GS1.1.1634859604.1.1.1634861262.0; dtSa=false%7CC%7C20%7CSearch%7Cx%7C1634861261937%7C459653922_227%7Chttps%3A%2F%2Fwww.hobbylobby.com%2Fstores%2Fsearch%3Fq%3DOklahoma%26CSRFToken%3D47258482-bb64-4eb0-9f18-77468d8a8186%7CStore%20Finder%7C%7C%7C",
    "Host": "www.hobbylobby.com",
    "Referer": "https://www.hobbylobby.com/stores/search?q=Oklahoma&CSRFToken=47258482-bb64-4eb0-9f18-77468d8a8186",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}

DOMAIN = "https://www.hobbylobby.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        search = DynamicZipSearch(country_codes=[SearchableCountries.USA])
        for zipcode in search:
            search_url = "https://www.hobbylobby.com/stores/search?q=" + zipcode
            stores_req = session.get(search_url, headers=headers2)
            try:
                soup = BeautifulSoup(stores_req.text, "html.parser")
            except AttributeError:
                continue

            locations = soup.find("div", {"class": "map-canvas"})
            if str(locations).find("map-canvas anime") == -1:
                locations = locations["data-stores"]
                locations = json.loads(locations)
                for loc in locations:
                    lat = loc["latitude"]
                    lng = loc["longitude"]
                    add1 = loc["address1"]
                    add2 = loc["address2"]
                    street = add1 + " " + add2
                    city = loc["city"]
                    state = loc["stateProvinceCode"]
                    pcode = loc["zipcode"]
                    phone = loc["phone"]
                    loc_link = "https://www.hobbylobby.com" + loc["linkUrl"]
                    req = session.get(loc_link, headers=headers)
                    try:
                        bs = BeautifulSoup(req.text, "html.parser")
                        hours = bs.find(
                            "table", {"class": "store-openings weekday_openings"}
                        ).text
                        hours = hours.replace("\n", " ")
                        hours = re.sub(pattern, " ", hours).strip()

                    except AttributeError:
                        hours = "Coming Soon"

                    title = "Hobby Lobby"

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=loc_link,
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
                        hours_of_operation=hours.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE}),
        duplicate_streak_failure_factor=-1,
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
