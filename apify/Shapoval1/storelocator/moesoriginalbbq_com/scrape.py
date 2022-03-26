import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    session = SgRequests()
    r = session.get("https://www.moesoriginalbbq.com/#location-list-section")
    tree = html.fromstring(r.content)
    urls = tree.xpath("//h2/a")
    for url in urls:
        page_url = "".join(url.xpath(".//@href"))
        if page_url.find("st-george") != -1:
            page_url = "https://www.moesoriginalbbq.com/st-george"
        if page_url.find("https://www.moesoriginalbbq.com/mexico-city") != -1:
            return
        session = SgRequests()
        tag = {
            "Recipient": "recipient",
            "AddressNumber": "address1",
            "AddressNumberPrefix": "address1",
            "AddressNumberSuffix": "address1",
            "StreetName": "address1",
            "StreetNamePreDirectional": "address1",
            "StreetNamePreModifier": "address1",
            "StreetNamePreType": "address1",
            "StreetNamePostDirectional": "address1",
            "StreetNamePostModifier": "address1",
            "StreetNamePostType": "address1",
            "CornerOf": "address1",
            "IntersectionSeparator": "address1",
            "LandmarkName": "address1",
            "USPSBoxGroupID": "address1",
            "USPSBoxGroupType": "address1",
            "USPSBoxID": "address1",
            "USPSBoxType": "address1",
            "BuildingName": "address2",
            "OccupancyType": "address2",
            "OccupancyIdentifier": "address2",
            "SubaddressIdentifier": "address2",
            "SubaddressType": "address2",
            "PlaceName": "city",
            "StateName": "state",
            "ZipCode": "postal",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[contains(text(), "Address")]/a/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/a/strong/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Address")]/a/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if page_url.find("http://www.moesoriginalbbq.com/lo/newark/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/steamboat") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/a/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/tuscaloosa/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2/a/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/westmobile") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("https://www.moesoriginalbbq.com/durham") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/orange-beach/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-2 span-2"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/eagle/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p/a/strong[contains(text(), "Address")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/atlanta/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/a/strong/em/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/destin") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/montgomery") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/woodfin/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/mobile/") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/huntsville") != -1:
            ad = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/nola/") != -1:
            ad = (
                " ".join(
                    tree.xpath(
                        '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Address")]//text()'
                    )
                )
                .replace("Address:", "")
                .strip()
            )

        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        if ad.find("843-") != -1:
            ad = ad.split("843-")[0].strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"

        location_name = (
            " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h1/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h1/text()'
                )
            )
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = "".join(
                tree.xpath(
                    "//p[./a]/preceding-sibling::h1/text() | //h2/preceding-sibling::h1/text()"
                )
            ).strip()
        if page_url.find("http://www.moesoriginalbbq.com/lo/newark/") != -1:
            location_name = " ".join(
                tree.xpath(
                    '//div[./div/h1[contains(text(), "CONTACT")]]/following-sibling::div/div[1]/div[1]/div/h2//text()'
                )
            )
        phone = "".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/strong[contains(text(), "(")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/following-sibling::p/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Phone")]//text()'
            )
        )
        if page_url.find("http://www.moesoriginalbbq.com/bentcreek") != -1:
            phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        if page_url.find("http://www.moesoriginalbbq.com/lo/pawleysisland") != -1:
            phone = "".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//a[contains(@href, "tel")]/strong/text()'
                )
            )
        phone = (
            phone.replace("PORK ", "")
            .replace("RIBS(", "(")
            .replace("RIBS ", "")
            .replace("(4BBQ)", "")
        )
        if phone.find("Phone:") != -1:
            phone = phone.split("Phone:")[1].strip()
        if page_url.find("http://www.moesoriginalbbq.com/lo/steamboat") != -1:
            phone = (
                "".join(
                    tree.xpath(
                        '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3[contains(text(), "Phone")]/text()'
                    )
                )
                .replace("Phone:", "")
                .strip()
            )
        ll = (
            "".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//a[contains(@href, "google.com/maps")]/@href | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//a[contains(@href, "google.com/maps")]/@href'
                )
            )
            or "<MISSING>"
        )
        try:
            if ll.find("ll=") != -1:
                latitude = ll.split("ll=")[1].split(",")[0]
                longitude = ll.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = ll.split("@")[1].split(",")[0]
                longitude = ll.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if page_url.find("http://www.moesoriginalbbq.com/lo/guntersville") != -1:
            latitude = (
                "".join(
                    tree.xpath(
                        '//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json'
                    )
                )
                .split('"markerLat":')[1]
                .split(",")[0]
            )
            longitude = (
                "".join(
                    tree.xpath(
                        '//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json'
                    )
                )
                .split('"markerLng":')[1]
                .split(",")[0]
            )

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//em[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "HOURS")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "Dining Room")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Hours")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Dining Room and")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Monday")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        if page_url.find("https://www.moesoriginalbbq.com/priceville") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Hours")]/text()'
                )
            )
        if (
            page_url.find(
                "http://www.moesoriginalbbq.com/lo/huntsvillevillageofprovidence/"
            )
            != -1
        ):
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Kitchen")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/huntsville") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Kitchen")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/orange-beach/") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "NOW OPEN")]/text()'
                )
            )
        if page_url.find("https://www.moesoriginalbbq.com/st-george") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//em[contains(text(), "11am")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/asheville/") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text()'
                )
            )
        if page_url.find("https://www.moesoriginalbbq.com/lo/boulder") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Open to in-house and patio dining.")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/mobile/") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Hours")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/hillcrest/") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/tuscaloosa") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Daily")]/text()'
                )
            )
        if page_url.find("http://www.moesoriginalbbq.com/lo/guntersville") != -1:
            hours_of_operation = " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[./strong]//text()'
                )
            )

        hours_of_operation = (
            hours_of_operation.replace("Open to in-house and patio dining.", "")
            .replace("NOW OPEN:", "")
            .strip()
        )

        if hours_of_operation.find("Kitchen:") != -1:
            hours_of_operation = (
                hours_of_operation.split("Kitchen:")[1].split("Bar:")[0].strip()
            )
        if hours_of_operation.find("Curbside") != -1:
            hours_of_operation = hours_of_operation.split("Curbside")[0].strip()
        if (
            hours_of_operation.find(
                "Dining Room & Patio, Take Out and Delivery plus Catering Available"
            )
            != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("HOURS: ")[1].split("Dining")[0].strip()
            )
        if (
            hours_of_operation.find(
                "Dining Room and Drive Thru Open plus Take Out & Delivery"
            )
            != -1
        ):
            hours_of_operation = hours_of_operation.split(
                "Dining Room and Drive Thru Open plus Take Out & Delivery"
            )[1].strip()
        if hours_of_operation.find("Kitchen") != -1:
            hours_of_operation = (
                hours_of_operation.split("Kitchen")[1].split("Bar:")[0].strip()
            )
        if (
            hours_of_operation.find(
                "Dining Room & Patio Open, Take Out and Delivery plus Catering Available"
            )
            != -1
        ):
            hours_of_operation = hours_of_operation.replace(
                "Dining Room & Patio Open, Take Out and Delivery plus Catering Available",
                "",
            ).strip()
        if hours_of_operation.find("Hours:  Restaurant ") != -1:
            hours_of_operation = (
                hours_of_operation.split("Hours:  Restaurant ")[1]
                .split("Bar")[0]
                .strip()
            )

        hours_of_operation = (
            hours_of_operation.replace("DINE IN NOW AVAILABLE!", "")
            .replace("Dining Room and Patio Open plus Take Out & Catering", "")
            .replace("Address:", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("Hours (dine in and drive thru)", "")
            .replace("Dine in and Carry Out Available", "")
            .replace("Open:", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace(
                "Take out and third party delivery thru Door Dash also available.", ""
            )
            .replace("NOW OPEN", "")
            .replace("Hours of operation:", "")
            .strip()
        )

        if page_url == "https://moesbbqcharlotte.com/":
            location_name = "".join(
                tree.xpath('//div[@class="col sqs-col-5 span-5"]/div/div/h1/text()')
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="col sqs-col-5 span-5"]/div/div/h3[contains(text(), "HOURS")]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = "".join(
                tree.xpath(
                    '//div[@class="col sqs-col-5 span-5"]/div/div/h3[contains(text(), "LOCATION")]/following-sibling::p[1]/text()'
                )
            ).strip()
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = (
                f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
                + " "
                + "St."
            )
            city = a.get("city").replace("St.", "").strip()
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="col sqs-col-5 span-5"]/div/div/h3[contains(text(), "PHONE")]/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("Matthews", "")
                .strip()
            )
            ll = "".join(
                tree.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
                )
            )
            js = json.loads(ll)
            latitude = js.get("location").get("mapLat")
            longitude = js.get("location").get("mapLng")
        if page_url == "https://www.moesdenver.com":
            location_name = "".join(tree.xpath('//div[@class="top-info"]/h3/text()'))
            street_address = "".join(
                tree.xpath(
                    '//div[@class="top-info"]/h3/following-sibling::p[1]/text()[1]'
                )
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="top-info"]/h3/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = "".join(
                tree.xpath('//p[contains(text(), "every day")]/text()')
            )
            city = "<MISSING>"
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if page_url.find("http://www.moesbbqtahoe.com/") != -1:
            location_name = "".join(
                tree.xpath('//span[@style="font-weight:bold"]//text()')
            )
            street_address = "700 N Lake Blvd"
            city = "Tahoe City"
            state = "CA"
            postal = "96145"
            country_code = "US"
            hours_of_operation = (
                "".join(tree.xpath('//div[@id="comp-kl6yd3tj"]/p[2]//text()'))
                + " "
                + "".join(tree.xpath('//div[@id="comp-kl6yd3tj"]/p[3]//text()'))
                + " "
                + "".join(tree.xpath('//div[@id="comp-kl6yd3tj"]/p[4]//text()'))
            )
            phone = "530-807-1023"
        if page_url.find("http://www.moesoriginalbbq.com/lo/vail/") != -1:
            slug = "".join(tree.xpath('//h2[contains(text(), "will be")]/text()[1]'))
            if slug:
                hours_of_operation = "Coming Soon"
        if page_url.find("http://www.moesoriginalbbq.com/lo/steamboat") != -1:
            hours_of_operation = "".join(
                tree.xpath('//h3[contains(text(), "Daily")]/text()[1]')
            )
        if location_name.find("Hours") != -1:
            location_name = location_name.split("Hours")[0].strip()
        street_address = street_address or "<MISSING>"
        if street_address == "<MISSING>" and location_name == "decatur":
            ad = "".join(tree.xpath("//h2/a/text()"))
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            state = ad.split(",")[2].split()[0].strip()
            postal = ad.split(",")[2].split()[1].strip()
        if location_name == "Leadville":
            street_address = (
                "".join(tree.xpath('//a[contains(@href, "goo.")]//text()[1]'))
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(tree.xpath('//a[contains(@href, "google")]//text()[1]'))
                .replace("\n", "")
                .strip()
            )
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()

        phone = phone or "<MISSING>"
        hours_of_operation = hours_of_operation or "<MISSING>"
        cms = "".join(
            tree.xpath(
                '//strong[text()="Coming Soon!"]//text() | //h2[text()="Coming Soon!"]/text()'
            )
        )
        if cms:
            hours_of_operation = "Coming Soon"
        if hours_of_operation == "<MISSING>" and location_name == "Priceville":
            hours_of_operation = (
                " ".join(tree.xpath("//h2/text()"))
                .replace("\n", "")
                .replace("Re-opening Wednesday May 5th!!", "")
                .strip()
            )
        if hours_of_operation == "<MISSING>" and location_name == "Asheville":
            hours_of_operation = (
                " ".join(tree.xpath("//h2/text()")).replace("\n", "").strip()
            )
        if hours_of_operation == "<MISSING>" and location_name == "steamboat Springs":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h1[text()="steamboat Springs"]/following-sibling::h3[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if hours_of_operation == "<MISSING>" and location_name == "Tuscaloosa":
            hours_of_operation = (
                " ".join(tree.xpath("//div/h2[1]/text()")).replace("\n", "").strip()
            )
        if hours_of_operation == "<MISSING>" and location_name == "Boulder":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//h1[text()="Boulder"]/following-sibling::h2//text()')
                )
                .replace("\n", "")
                .strip()
            )
        if location_name == "Lakeview":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//h1[text()="Lakeview"]/following-sibling::h2//text()')
                )
                .replace("\n", "")
                .replace("Bar open as long as there's a crowd!", "")
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("HOURS:", "")
            .replace("Close  @ 3pm 12/24 Closed  12/25", "")
            .strip()
        )
        if latitude == "<MISSING>":
            ll = (
                "".join(tree.xpath('//a[contains(@href, "maps")]/@href')) or "<MISSING>"
            )
            if ll == "<MISSING>":
                ll = "".join(tree.xpath("//iframe/@src")) or "<MISSING>"
        try:
            latitude = ll.split("@")[1].split(",")[0].strip()
            longitude = ll.split("@")[1].split(",")[1].strip()
        except:
            try:
                latitude = ll.split("!3d")[1].split("!")[0].strip()
                longitude = ll.split("!2d")[1].split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.moesoriginalbbq.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
