import re

from bs4 import BeautifulSoup

from lxml import etree

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgscrape.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    domain = "https://www.prezzorestaurants.co.uk"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    all_links = []

    for i in range(1, 15):
        base_link = (
            "https://www.prezzorestaurants.co.uk/find-and-book/search/?lat=51.502132&lng=-0.1887645&dist=2000&s=&p=%s&f="
            % (i)
        )
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        locs = base.find(id="restaurant-search-results").find_all(
            class_="button secondary-button w-100 px-i"
        )
        for loc in locs:
            link = domain + loc["href"]
            if link not in all_links:
                all_links.append(link)

    for store_url in all_links:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h2[@class="title mb-2 has-text-weight-bold"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h4[a[contains(@href, "tel")]]/following-sibling::div[1]/p[1]/text()'
        )
        raw_address = [" ".join(e.split()) for e in raw_address][0]
        addr = parse_address_intl(raw_address)
        street_address = ", ".join(raw_address.split(", ")[:-2]).strip()
        city = addr.city
        if not city:
            city = raw_address.split(",")[-2].strip()
        if street_address.split(",")[-1].strip() in city:
            street_address = " ".join(street_address.split(",")[:-1]).strip()
        street_address = street_address.replace(" , ", ", ")
        street_address = (re.sub(" +", " ", street_address)).strip()

        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code:
            zip_code = raw_address.split(",")[-1].strip()
        country_code = "UK"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        try:
            map_link = loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            geo = re.findall(r"[0-9]{2}\.[0-9]+.{1,2}[0-9]{1,3}\.[0-9]+", map_link)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1].split("&")[0]
        except:
            req = session.get(map_link, headers=headers)
            map_link = req.url
            if "@" in map_link:
                latitude = map_link.split("@")[1].split(",")[0]
                longitude = map_link.split("@")[1].split(",")[1]

        loc_response = session.get(store_url + "?X-Requested-With=XMLHttpRequest")
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//div[h4[contains(text(), "Opening times")]]/following-sibling::div//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
