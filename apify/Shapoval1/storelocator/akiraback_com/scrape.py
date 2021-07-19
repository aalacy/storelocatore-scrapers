import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://www.akiraback.com"
    api_url = "https://www.akiraback.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="sortMain"]/div[position()<5]//a')
    s = set()
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        slug = "".join(d.xpath('.//preceding::span[@class="ai-rf"][1]/text()'))
        location_name = (
            "".join(d.xpath('.//span[@class="cta-text js-cta-element"]/text()'))
            .replace("ABSTEAK BY CHEF ", "")
            .strip()
        )
        location_type = "RESTAURANT"
        ad = "<MISSING>"
        if page_url == "https://absteakla.com/":
            page_url = "https://absteakla.com/location/"
        if page_url == "https://lumirooftop.com/":
            page_url = "https://lumirooftop.com/contact/"
        if page_url == "https://www.akirabackdubai.com/":
            page_url = "https://www.akirabackdubai.com/contact-us"
        if page_url == "https://www.caesars.com/dubai/restaurants/paru/":
            continue
        if (
            page_url
            == "https://www.fourseasons.com/seoul/dining/restaurants/akira-back/"
        ):
            page_url = "https://www.fourseasons.com/seoul/getting-here/"
        if page_url == "http://dosaseoul.com/":
            continue
        if page_url == "https://dashatoronto.com/":
            page_url = "https://dashatoronto.com/contact/"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        if (
            slug.find("beverly hills") != -1
            or slug.find("san diego") != -1
            or slug.find("las vegas") != -1
        ):
            slug = "US"
        if slug.find("toronto") != -1:
            slug = "CA"
        if slug.find("NORTH ISLAND SEYCHELLES") != -1:
            slug = "NORTH ISLAND"
        if slug.find("SEOUL") != -1:
            slug = "South Korea"
        if slug.find("HANOI") != -1:
            slug = "Vietnam"
        if slug.find("BANGKOK") != -1:
            slug = "Thailand"
        country_code = slug
        city = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url == "https://absteakla.com/location/":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h2[./span[text()="LOCATION"]]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(tree.xpath('//a[contains(text(), "Telephone")]/text()'))
                .replace("Telephone:", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h2[./span[text()="HOURS OF OPERATION"]]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            map_link = "".join(tree.xpath("//iframe/@data-src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        if page_url == "https://lumirooftop.com/contact/":
            ad = (
                " ".join(tree.xpath('//div[@class="map_popup_address"]//a/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            phone = "".join(tree.xpath('//div[@class="map_popup_address"]/p[2]/text()'))
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[text()="Lumi Hours"]/following-sibling::p[position()>1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            latitude = "".join(tree.xpath('//div[@class="contact_map"]/@data-lat'))
            longitude = "".join(tree.xpath('//div[@class="contact_map"]/@data-lng'))
        if (
            page_url
            == "https://bellagio.mgmresorts.com/en/restaurants/yellowtail-japanese-restaurant-lounge.html"
        ):
            ad = (
                " ".join(tree.xpath('//a[contains(@href, "goo")]/text()'))
                .replace("\n", "")
                .strip()
            )
            phone = "".join(
                tree.xpath(
                    '//div[./h4[text()="Contact"]]/following-sibling::div//a//text()'
                )
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//aside[@class="OverviewHeaderSection__aside"]//div[./h4[text()="Hours of Operation"]]/following-sibling::div//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude":"')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude":"')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://www.akirabacktoronto.com/":
            ad = (
                " ".join(
                    tree.xpath('//h6[text()="Find Us"]/following-sibling::p/text()')
                )
                .replace("\n", "")
                .strip()
            )
            phone = (
                " ".join(
                    tree.xpath(
                        '//h6[text()="Contact Us"]/following-sibling::p[1]//a[1]/following-sibling::a[1]/text()'
                    )
                )
                .replace("\n", "")
                .split()[0]
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="sixcol-one"]//h6[text()="Hours"]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude": "')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://dashatoronto.com/contact/":
            ad = "".join(
                tree.xpath(
                    '//div[@class="pdf-link"]/following-sibling::div[1]/div/div/p[1]/text()'
                )
            )
            phone = "".join(
                tree.xpath('//div[@class="siteFooter__telephone"]/a/text()')
            )
            hours_of_operation = "".join(
                tree.xpath(
                    '//div[@class="pdf-link"]/following-sibling::div[1]/div/div/p[2]/text()'
                )
            )
            map_link = "".join(tree.xpath("//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        if page_url == "http://misterctoronto.com/":
            ad = (
                " ".join(
                    tree.xpath('//h3[text()="LOCATION"]/following-sibling::div/text()')
                )
                .replace("\r\n", "")
                .strip()
            )
            phone = "".join(
                tree.xpath('//h3[text()="CONTACT"]/following-sibling::div/a[2]/text()')
            ).strip()
            hours_of_operation = "".join(
                tree.xpath('//h3[text()="HOURS"]/following-sibling::div//text()')
            ).strip()
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude": "')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://www.akirabackdubai.com/contact-us":
            ad = "".join(tree.xpath('//a[@id="hotel-address"]/text()'))
            phone = "".join(
                tree.xpath(
                    '//div[@class="hotel-adddress"]//a[contains(@href, "tel")]/text()'
                )
            ).strip()
            hours_of_operation = tree.xpath(
                '//*[contains(text(), "Opening Hours")]/following-sibling::*[1]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude": "')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://www.north-island.com/dining-options/":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h4[text()="CONTACT US"]/following-sibling::div/p[1]/text()'
                    )
                )
                .replace("\n", "")
                .split("Telephone")[0]
                .strip()
            )
            phone = (
                " ".join(
                    tree.xpath(
                        '//h4[text()="CONTACT US"]/following-sibling::div/p[1]/text()'
                    )
                )
                .replace("\n", "")
                .split("Telephone:")[1]
                .split("Fax:")[0]
                .strip()
            )
        if page_url == "https://www.fourseasons.com/seoul/getting-here/":
            ad = "".join(
                tree.xpath('//address[@class="LocationBar-address ty-c2"]/text()')
            )
            phone = "".join(
                tree.xpath('//a[@class="phone LocationBar-phone invoca_class"]/text()')
            )
            latitude = (
                "".join(
                    tree.xpath(
                        '//div[@class="EmbeddedMap-map EmbeddedMap-map--fixedHeight"]/@data-map'
                    )
                )
                .split('"lat": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(
                        '//div[@class="EmbeddedMap-map EmbeddedMap-map--fixedHeight"]/@data-map'
                    )
                )
                .split('"lng": "')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://portal.marriott.com/hanjw-dining/akira-back":
            ad = "".join(
                tree.xpath('//i[@class="icon-maps-pin"]/following-sibling::span/text()')
            )
            phone = (
                "".join(
                    tree.xpath('//div[@class="header-main-details-phone"]/a/text()')
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                "".join(tree.xpath('//ul[@class="hourlist carouselitems"]/li//text()'))
                .replace("\n", "")
                .strip()
            )
            if hours_of_operation.find("Temporarily closed") != -1:
                hours_of_operation = "Temporarily closed"
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude": "')[1]
                .split('"')[0]
                .strip()
            )
        if (
            page_url
            == "https://bangkokmarriottmarquisqueenspark.com/dining/akira-back/"
        ):
            ad = "".join(
                tree.xpath('//i[@class="icon-maps-pin"]/following-sibling::span/text()')
            )
            phone = (
                "".join(tree.xpath('//span[@class="header-main-phone"]/a/text()'))
                .replace("\n", "")
                .strip()
            )
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude": "')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude": "')[1]
                .split('"')[0]
                .strip()
            )
        if page_url == "https://bangkokmarriottmarquisqueenspark.com/dining/abar/":
            ad = "".join(
                tree.xpath('//i[@class="icon-maps-pin"]/following-sibling::span/text()')
            )
        if (
            page_url
            == "https://www.marriott.com/hotels/hotel-information/restaurant/details/sinjw-jw-marriott-hotel-singapore-south-beach/5895579"
        ):
            ad = (
                " ".join(tree.xpath("//address/a/span/text()"))
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//span[@class="phone-number t-color-brand t-font-s t-line-height-m l-l-display-inline-block is-hidden-s l-phone-number t-force-ltr"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"latitude":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
                .split('"longitude":')[1]
                .split("}")[0]
                .strip()
            )
            hours_of_operation = tree.xpath(
                '//p[text()="Hours of Operation"]/following-sibling::div//div//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)

        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if street_address == "<MISSING>":
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            country_code = a.country

        line = ad
        if line in s:
            continue
        s.add(line)

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
