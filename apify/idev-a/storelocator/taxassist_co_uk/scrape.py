from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://us.fatface.com/stores",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Cookie": "__cfduid=daf10bd77120abd062ff79ae36a3394561614035333; dwac_0da89386c839c79e6773009f39=jTksSzgK29bHn4ewF1OU7gstpVxp30TmWAk%3D|dw-only|||GBP|false|Europe%2FLondon|true; cqcid=acZGV7iE3z709qnlaDSpcnNUR5; cquid=||; sid=jTksSzgK29bHn4ewF1OU7gstpVxp30TmWAk; dwanonymous_c587c8d662b3833601b344f41b2494fb=acZGV7iE3z709qnlaDSpcnNUR5; dwsid=VX1DfcviX-HEIPyDsVVa7tNpymqaN8DRW7bkrUqO8Kw7SA-9PO10QK473Yp8gKK3BTyGRlqm73qA-yj0s13z7w==; s_fid=515E81C6AC83CB7E-139201ED3D830070; s_getNewRepeat=1614035353525-New; s_cc=true; scarab.visitor=%22457AE3AEEC97CE16%22; s_vi=[CS]v1|301A1CC577F7199A-400005B84D13BDA5[CE]; __cq_uuid=ab0JNNtOLkGoBEqJunjlYWMnfK; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _hjTLDTest=1; _hjid=dc9183c0-0b35-4025-b2bb-7b109fa47b38; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=0; _fbp=fb.1.1614035344290.1677450804; _uetsid=f0cad3b0756211eb821f59b490c0f61c; _uetvid=f0caf790756211ebb247ab8ba216d046; s_sq=fatfaceusproduction%3D%2526c.%2526a.%2526activitymap.%2526page%253D%25252Fstores%2526link%253DGBP%252520%2525C2%2525A3%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253D%25252Fstores%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.fatface.com%25252Fstores%2526ot%253DA; __cq_dnt=0; dw_dnt=0; selectedLocale=en_GB",
}


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original).replace("\t", "").replace("\n", "")


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.taxassist.co.uk/"
        base_url = "https://www.taxassist.co.uk/locations"
        r = session.get(base_url)
        soup = bs(r.text, "lxml")
        links = soup.select("main div.row a.primary.outline")
        for link in links:
            r1 = session.get(link["href"])
            soup1 = bs(r1.text, "lxml")
            details = soup1.select("main div.mt-auto a.outline")
            for detail in details:
                r2 = session.get(detail["href"])
                soup2 = bs(r2.text, "lxml")
                location = json.loads(
                    _fix(
                        soup2.find("script", type="application/ld+json").string.strip()
                    )
                )
                if location["address"]["streetAddress"] == "Coming Soon":
                    continue
                hours = []
                for _ in location["openingHoursSpecification"]:
                    hour = f"{_['opens']}-{_['closes']}"
                    if hour == "00:00-00:00":
                        hour = "closed"
                    hours.append(f"{_['dayOfWeek']}: {hour}")
                yield SgRecord(
                    page_url=detail["href"],
                    location_type=location["@type"],
                    location_name=location["name"],
                    street_address=location["address"]["streetAddress"],
                    city=location["name"],
                    zip_postal=location["address"]["postalCode"],
                    country_code="uk",
                    latitude=location["geo"]["latitude"],
                    longitude=location["geo"]["longitude"],
                    phone=location["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
