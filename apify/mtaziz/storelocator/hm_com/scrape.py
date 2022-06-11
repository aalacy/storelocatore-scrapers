from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("hm_com")
MISSING = "<MISSING>"
DOMAIN = "hm.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}


session = SgRequests()
r = session.get("https://www.hm.com/nz/store-locator/new-zealand/", headers=headers)
sel = html.fromstring(r.text, "lxml")
urls_all_countries_raw = sel.xpath(
    '//div[contains(@class, "store-locator-nav")]/div/nav/ul/li/a/@href'
)
for idx1, country in enumerate(urls_all_countries_raw):
    if "vietnam" in country:
        id_end = idx1
urls_all_countries_clean = urls_all_countries_raw[: id_end + 1]
all_countries_list = [
    url.split("/")[-2].replace("-", " ") for url in urls_all_countries_clean
]


logger.info(f"Number of countries found: {len(all_countries_list)}")

# Mapping the country name ( full ) with ISO-based country code

country_code_iso = [
    ("Afghanistan", "AF"),
    ("Aland Islands", "AX"),
    ("Albania", "AL"),
    ("Algeria", "DZ"),
    ("American Samoa", "AS"),
    ("Andorra", "AD"),
    ("Angola", "AO"),
    ("Anguilla", "AI"),
    ("Antarctica", "AQ"),
    ("Antigua and Barbuda", "AG"),
    ("Argentina", "AR"),
    ("Armenia", "AM"),
    ("Aruba", "AW"),
    ("Australia", "AU"),
    ("Austria", "AT"),
    ("Azerbaijan", "AZ"),
    ("Bahamas", "BS"),
    ("Bahrain", "BH"),
    ("Bangladesh", "BD"),
    ("Barbados", "BB"),
    ("Belarus", "BY"),
    ("Belgium", "BE"),
    ("Belize", "BZ"),
    ("Benin", "BJ"),
    ("Bermuda", "BM"),
    ("Bhutan", "BT"),
    ("Bolivia", "BO"),
    ("Bosnia and Herzegovina", "BA"),
    ("Botswana", "BW"),
    ("Bouvet Island", "BV"),
    ("Brazil", "BR"),
    ("British Virgin Islands", "VG"),
    ("British Indian Ocean Territory", "IO"),
    ("Brunei Darussalam", "BN"),
    ("Bulgaria", "BG"),
    ("Burkina Faso", "BF"),
    ("Burundi", "BI"),
    ("Cambodia", "KH"),
    ("Cameroon", "CM"),
    ("Canada", "CA"),
    ("Cape Verde", "CV"),
    ("Cayman Islands", "KY"),
    ("Central African Republic", "CF"),
    ("Chad", "TD"),
    ("Chile", "CL"),
    ("China", "CN"),
    ("Hong Kong, SAR China", "HK"),
    ("Macao, SAR China", "MO"),
    ("Christmas Island", "CX"),
    ("Cocos (Keeling) Islands", "CC"),
    ("Colombia", "CO"),
    ("Comoros", "KM"),
    ("Congo, Brazzaville", "CG"),
    ("Congo, Kinshasa", "CD"),
    ("Cook Islands", "CK"),
    ("Costa Rica", "CR"),
    ("Côte d'Ivoire", "CI"),
    ("Croatia", "HR"),
    ("Cuba", "CU"),
    ("Cyprus", "CY"),
    ("Czech Republic", "CZ"),
    ("Denmark", "DK"),
    ("Djibouti", "DJ"),
    ("Dominica", "DM"),
    ("Dominican Republic", "DO"),
    ("Ecuador", "EC"),
    ("Egypt", "EG"),
    ("El Salvador", "SV"),
    ("Equatorial Guinea", "GQ"),
    ("Eritrea", "ER"),
    ("Estonia", "EE"),
    ("Ethiopia", "ET"),
    ("Falkland Islands (Malvinas)", "FK"),
    ("Faroe Islands", "FO"),
    ("Fiji", "FJ"),
    ("Finland", "FI"),
    ("France", "FR"),
    ("French Guiana", "GF"),
    ("French Polynesia", "PF"),
    ("French Southern Territories", "TF"),
    ("Gabon", "GA"),
    ("Gambia", "GM"),
    ("Georgia", "GE"),
    ("Germany", "DE"),
    ("Ghana", "GH"),
    ("Gibraltar", "GI"),
    ("Greece", "GR"),
    ("Greenland", "GL"),
    ("Grenada", "GD"),
    ("Guadeloupe", "GP"),
    ("Guam", "GU"),
    ("Guatemala", "GT"),
    ("Guernsey", "GG"),
    ("Guinea", "GN"),
    ("Guinea-Bissau", "GW"),
    ("Guyana", "GY"),
    ("Haiti", "HT"),
    ("Heard and Mcdonald Islands", "HM"),
    ("Holy See, Vatican City State", "VA"),
    ("Hong Kong SAR", "HK"),
    ("Honduras", "HN"),
    ("Hungary", "HU"),
    ("Iceland", "IS"),
    ("India", "IN"),
    ("Indonesia", "ID"),
    ("Iran, Islamic Republic of", "IR"),
    ("Iraq", "IQ"),
    ("Ireland", "IE"),
    ("Isle of Man", "IM"),
    ("Israel", "IL"),
    ("Italy", "IT"),
    ("Jamaica", "JM"),
    ("Japan", "JP"),
    ("Jersey", "JE"),
    ("Jordan", "JO"),
    ("Kazakhstan", "KZ"),
    ("Kenya", "KE"),
    ("Kiribati", "KI"),
    ("Kuwait", "KW"),
    ("Kyrgyzstan", "KG"),
    ("Lao PDR", "LA"),
    ("Latvia", "LV"),
    ("Lebanon", "LB"),
    ("Lesotho", "LS"),
    ("Liberia", "LR"),
    ("Libya", "LY"),
    ("Liechtenstein", "LI"),
    ("Lithuania", "LT"),
    ("Luxembourg", "LU"),
    ("Macedonia, Republic of", "MK"),
    ("Macao SAR", "MO"),
    ("Madagascar", "MG"),
    ("Malawi", "MW"),
    ("Malaysia", "MY"),
    ("Maldives", "MV"),
    ("Mali", "ML"),
    ("Malta", "MT"),
    ("Marshall Islands", "MH"),
    ("Martinique", "MQ"),
    ("Mauritania", "MR"),
    ("Mauritius", "MU"),
    ("Mayotte", "YT"),
    ("Mexico", "MX"),
    ("Micronesia, Federated States of", "FM"),
    ("Moldova", "MD"),
    ("Monaco", "MC"),
    ("Mongolia", "MN"),
    ("Montenegro", "ME"),
    ("Montserrat", "MS"),
    ("Morocco", "MA"),
    ("Mozambique", "MZ"),
    ("Myanmar", "MM"),
    ("Namibia", "NA"),
    ("Nauru", "NR"),
    ("Nepal", "NP"),
    ("Netherlands", "NL"),
    ("Netherlands Antilles", "AN"),
    ("New Caledonia", "NC"),
    ("New Zealand", "NZ"),
    ("Nicaragua", "NI"),
    ("Niger", "NE"),
    ("Nigeria", "NG"),
    ("Niue", "NU"),
    ("Norfolk Island", "NF"),
    ("Northern Mariana Islands", "MP"),
    ("Norway", "NO"),
    ("Oman", "OM"),
    ("Pakistan", "PK"),
    ("Palau", "PW"),
    ("Palestinian Territory", "PS"),
    ("Panama", "PA"),
    ("Papua New Guinea", "PG"),
    ("Paraguay", "PY"),
    ("Peru", "PE"),
    ("Philippines", "PH"),
    ("Pitcairn", "PN"),
    ("Poland", "PL"),
    ("Portugal", "PT"),
    ("Puerto Rico", "PR"),
    ("Qatar", "QA"),
    ("Réunion", "RE"),
    ("Romania", "RO"),
    ("Russia", "RU"),
    ("Rwanda", "RW"),
    ("Saint-Barthélemy", "BL"),
    ("Saint Helena", "SH"),
    ("Saint Kitts and Nevis", "KN"),
    ("Saint Lucia", "LC"),
    ("Saint-Martin (French part)", "MF"),
    ("Saint Pierre and Miquelon", "PM"),
    ("Saint Vincent and Grenadines", "VC"),
    ("Samoa", "WS"),
    ("San Marino", "SM"),
    ("Sao Tome and Principe", "ST"),
    ("Saudi Arabia", "SA"),
    ("Senegal", "SN"),
    ("Serbia", "RS"),
    ("Seychelles", "SC"),
    ("Sierra Leone", "SL"),
    ("Singapore", "SG"),
    ("Slovakia", "SK"),
    ("Slovenia", "SI"),
    ("Solomon Islands", "SB"),
    ("Somalia", "SO"),
    ("South Africa", "ZA"),
    ("South Georgia and the South Sandwich Islands", "GS"),
    ("South Sudan", "SS"),
    ("North Korea", "KP"),
    ("South Korea", "KR"),
    ("Spain", "ES"),
    ("Sri Lanka", "LK"),
    ("Sudan", "SD"),
    ("Suriname", "SR"),
    ("Svalbard and Jan Mayen Islands", "SJ"),
    ("Swaziland", "SZ"),
    ("Sweden", "SE"),
    ("Switzerland", "CH"),
    ("Syria", "SY"),
    ("Taiwan", "TW"),
    ("Tajikistan", "TJ"),
    ("Tanzania", "TZ"),
    ("Thailand", "TH"),
    ("Timor-Leste", "TL"),
    ("Togo", "TG"),
    ("Tokelau", "TK"),
    ("Tonga", "TO"),
    ("Trinidad and Tobago", "TT"),
    ("Tunisia", "TN"),
    ("Turkey", "TR"),
    ("Turkmenistan", "TM"),
    ("Turks and Caicos Islands", "TC"),
    ("Tuvalu", "TV"),
    ("Uganda", "UG"),
    ("Ukraine", "UA"),
    ("United Arab Emirates", "AE"),
    ("United Kingdom", "GB"),
    ("USA", "US"),
    ("US Minor Outlying Islands", "UM"),
    ("Uruguay", "UY"),
    ("Uzbekistan", "UZ"),
    ("Vanuatu", "VU"),
    ("Venezuela", "VE"),
    ("Vietnam", "VN"),
    ("Virgin Islands, US", "VI"),
    ("Wallis and Futuna Islands", "WF"),
    ("Western Sahara", "EH"),
    ("Yemen", "YE"),
    ("Zambia", "ZM"),
    ("Zimbabwe", "ZW"),
]


mapped_country_name_full_and_iso_code = []
for i in all_countries_list:
    for j in country_code_iso:
        if i == j[0].lower():
            mapped_country_name_full_and_iso_code.append((i, j[1]))

# mapped_country_name_full_and_iso_code
logger.info(f"ISO-based country matched: {len(mapped_country_name_full_and_iso_code)}")


zip_code_containing_extra_text = [
    "Salmiya",
    "Abu Dhabi",
    "47913 2613",
    "jeddah",
    "+962 6",
    "Dublin 15",
    "Lima 41",
    "Musacat",
    "Al Manama",
    "Cairo",
    "Cork",
    "Dublin 22",
    "N/A",
    "Kildare",
    "Dammam",
    "Riyadh",
    "Hofuf",
    "-",
    "Warszawa",
    "Al Rai",
    "X",
    "Beirut",
    "Fintas",
    "Jahra",
    "Ireland",
    "Dublin 16",
    "Taif",
    "Dublin 2",
    "Madina",
    "Piura 200",
    "Jeddah",
    "Co.",
    "Amman",
    "Dublin 24",
    "Dublin",
    "Fujairah",
    "Muscat",
    "XXX",
    "x",
    "Atlhone",
    "Kilkenny",
    "Sharjah",
    "Casablanca",
    "Dubai",
    "+20 2",
    "1110 Wien",
    "Shuwaikh",
    "Limerick",
    "〒158-0094",
    "Doha",
    "C.P. 36643",
    "Dublin 9",
    "Mecca",
    "RAK",
    "Al Ain",
    "0",
    "Москва",
    "XXXX",
    "Gia Lam",
    "1",
]


def fetch_data():
    # Your scraper here
    session = SgRequests()
    total = 0
    for idx, country_code_iso in enumerate(mapped_country_name_full_and_iso_code):
        start_url = f"https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_US/country/{country_code_iso[1]}?_type=json&campaigns=true&departments=true&openinghours=true&maxnumberofstores=1000"
        logger.info(f"Pulling the data from ({idx}) : ( {start_url} )")

        # US POI
        data = session.get(start_url, headers=headers).json()
        all_poi = data["stores"]
        total += len(all_poi)
        for poi in all_poi:
            # Locator Domain
            locator_domain = DOMAIN

            # Page URL
            page_url = MISSING

            # Location Name
            location_name = poi["name"]
            location_name = location_name if location_name else MISSING

            # Street Address
            street_address1 = poi["address"]["streetName1"].strip().rstrip(",")
            street_address2 = poi["address"]["streetName2"].strip().rstrip(",")
            raw_address_to_be_parsed = ""
            if street_address2:
                raw_address_to_be_parsed = street_address1 + ", " + street_address2
            else:
                raw_address_to_be_parsed = street_address1

            street_address_parsed = parse_address_intl(raw_address_to_be_parsed)
            street_address_parsed = street_address_parsed.street_address_1
            logger.info(f" Parsed Street Address: {street_address_parsed}")

            # sgpostal returned the following incomplete street addresses,
            # These addresses have been replaced by street address 1 or 2 found in the API response data.
            # Suite No. 2320
            # Building G
            # Suite 1200
            # Suite E2
            # x
            # Unit #C095A
            # Unit #C095A
            # Space #1040
            # Unit # 260
            # H&M Space 84

            street_address = ""
            if street_address2:
                street_address = street_address2
            else:
                street_address = street_address_parsed

            if street_address == "Suite No. 2320":
                street_address = street_address_parsed

            if street_address == "Building G":
                street_address = street_address_parsed

            if street_address == "Suite 1200":
                street_address = street_address_parsed

            if street_address == "Suite E2":
                street_address = street_address_parsed

            if street_address == "x":
                street_address = street_address1

            if street_address == "Unit #C095A":
                street_address = street_address1
            if street_address == "Space #1040":
                street_address = street_address1
            if street_address == "Unit # 260":
                street_address = street_address1
            if street_address == "H&M Space 84":
                street_address = street_address1

            street_address = street_address if street_address else MISSING

            # City
            city = poi["city"]
            if not city:
                city = poi.get("address", {}).get("postalAddress")
            city = city if city else MISSING

            # State
            state = poi.get("region", {}).get("name")
            if not state:
                state = poi.get("address", {}).get("state")
            state = state if state else MISSING

            # Zip Code
            zip_code = poi["address"]["postCode"].strip()
            zip_code = zip_code.replace("US", "").strip()
            if zip_code == "x" or zip_code == "X" or zip_code == "XXX":
                zip_code = (
                    zip_code.replace("x", "")
                    .replace("X", "")
                    .replace("XXX", "")
                    .replace("〒158-0094", "158-0094")
                    .replace("12190x", "12190")
                )

            # Clean up extraneous string in zip code
            for i in zip_code_containing_extra_text:
                if i == zip_code:
                    zip_code = zip_code.replace(i, "")

            zip_code = zip_code if zip_code else MISSING

            # Country Code
            country_code = poi["countryCode"].strip()
            country_code = country_code if country_code else MISSING

            # Store Number
            store_number = poi["storeCode"].strip()
            store_number = store_number if store_number else MISSING

            # Phone Number
            phone = poi.get("phone")
            phone = phone.strip() if phone else MISSING

            # Location Type
            location_type = MISSING
            location_type = location_type if location_type else MISSING

            # Latitude
            latitude = poi["latitude"]
            latitude = latitude if latitude else MISSING

            # Longitude
            longitude = poi["longitude"]
            longitude = longitude if longitude else MISSING

            # Hours of operation
            hours_of_operation = []
            for elem in poi["openingHours"]:
                hours_of_operation.append(
                    "{} {} - {}".format(elem["name"], elem["opens"], elem["closes"])
                )
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else MISSING
            )

            # Parsing raw address and join those raw fields' data

            try:
                st1_raw_1 = poi["address"]["streetName1"]
            except KeyError:
                st1_raw_1 = ""

            try:
                st2_raw_2 = poi["address"]["streetName2"]
            except KeyError:
                st2_raw_2 = ""

            try:
                city_raw_3 = poi["city"]
            except KeyError:
                city_raw_3 = ""
            try:
                state_raw_4 = poi["address"]["state"]
            except KeyError:
                state_raw_4 = ""
            try:
                zc_raw_5 = poi["address"]["postCode"]
            except KeyError:
                zc_raw_5 = ""

            country_code_raw_6 = poi["countryCode"]
            raw_address_concat = f"{st1_raw_1}, {st2_raw_2}, {city_raw_3}, {state_raw_4}, {zc_raw_5}, {country_code_raw_6}"
            raw_address_concat = raw_address_concat.split(",")
            raw_address_concat = [" ".join(i.split()) for i in raw_address_concat if i]
            raw_address_concat = [i for i in raw_address_concat if i]
            raw_address_concat = ", ".join(raw_address_concat)
            raw_address = raw_address_concat if raw_address_concat else MISSING
            logger.info(f"Raw Address: {raw_address}")

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
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
                raw_address=raw_address,
            )

        logger.info(f"Total: {total} | Found: {len(all_poi)}")


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
