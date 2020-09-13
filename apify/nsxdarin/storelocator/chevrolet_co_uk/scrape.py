import csv
from sgrequests import SgRequests

MISSING = '<MISSING>'
session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'locale': 'en_GB'
}

cities = ["London", "Birmingham", "Leeds", "Glasgow", "Sheffield", "Bradford", "Liverpool", "Edinburgh", "Manchester", "Bristol", "Kirklees", "Fife", "Wirral", "North Lanarkshire", "Wakefield", "Cardiff", "Dudley", "Wigan", "East Riding", "South Lanarkshire", "Coventry", "Belfast", "Leicester", "Sunderland", "Sandwell", "Doncaster", "Stockport", "Sefton", "Nottingham", "Newcastle-upon-Tyne", "Kingston-upon-Hull", "Bolton", "Walsall", "Plymouth", "Rotherham", "Stoke-on-Trent", "Wolverhampton", "Rhondda, Cynon, Taff", "South Gloucestershire", "Derby", "Swansea", "Salford", "Aberdeenshire", "Barnsley", "Tameside", "Oldham", "Trafford", "Aberdeen", "Southampton", "Highland", "Rochdale", "Solihull", "Gateshead", "Milton Keynes", "North Tyneside", "Calderdale", "Northampton", "Portsmouth", "Warrington", "North Somerset", "Bury", "Luton", "St Helens", "Stockton-on-Tees", "Renfrewshire", "York", "Thamesdown", "Southend-on-Sea", "New Forest", "Caerphilly", "Carmarthenshire", "Bath & North East Somerset", "Wycombe", "Basildon", "Bournemouth", "Peterborough", "North East Lincolnshire", "Chelmsford", "Brighton", "South Tyneside", "Charnwood", "Aylesbury Vale", "Colchester", "Knowsley", "North Lincolnshire", "Huntingdonshire", "Macclesfield", "Blackpool", "West Lothian", "South Somerset", "Dundee", "Basingstoke & Deane", "Harrogate", "Dumfries & Galloway", "Middlesbrough", "Flintshire", "Rochester-upon-Medway", "The Wrekin", "Newbury", "Falkirk", "Reading",
          "Wokingham", "Windsor & Maidenhead", "Maidstone", "Redcar & Cleveland", "North Ayrshire", "Blackburn", "Neath Port Talbot", "Poole", "Wealden", "Arun", "Bedford", "Oxford", "Lancaster", "Newport", "Canterbury", "Preston", "Dacorum", "Cherwell", "Perth & Kinross", "Thurrock", "Tendring", "Kings Lynn & West Norfolk", "St Albans", "Bridgend", "South Cambridgeshire", "Braintree", "Norwich", "Thanet", "Isle of Wight", "Mid Sussex", "South Oxfordshire", "Guildford", "Elmbridge", "Stafford", "Powys", "East Hertfordshire", "Torbay", "Wrexham Maelor", "East Devon", "East Lindsey", "Halton", "Warwick", "East Ayrshire", "Newcastle-under-Lyme", "North Wiltshire", "South Kesteven", "Epping Forest", "Vale of Glamorgan", "Reigate & Banstead", "Chester", "Mid Bedfordshire", "Suffolk Coastal", "Horsham", "Nuneaton & Bedworth", "Gwynedd", "Swale", "Havant & Waterloo", "Teignbridge", "Cambridge", "Vale Royal", "Amber Valley", "North Hertfordshire", "South Ayrshire", "Waverley", "Broadland", "Crewe & Nantwich", "Breckland", "Ipswich", "Pembrokeshire", "Vale of White Horse", "Salisbury", "Gedling", "Eastleigh", "Broxtowe", "Stratford-on-Avon", "South Bedfordshire", "Angus", "East Hampshire", "East Dunbartonshire", "Conway", "Sevenoaks", "Slough", "Bracknell Forest", "West Lancashire", "West Wiltshire", "Ashfield", "Lisburn", "Scarborough", "Stroud", "Wychavon", "Waveney", "Exeter", "Dover", "Test Valley", "Gloucester", "Erewash", "Cheltenham", "Bassetlaw", "Scottish Borders"]


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([
            "locator_domain",
            "page_url",
            "location_name",
            "location_type",
            "store_number",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "latitude",
            "longitude",
            "phone",
            "hours_of_operation"
        ])
        for row in data:
            writer.writerow(row)


def fetch_data():
    dealer_map = {}
    for city in cities:
        url = f'https://www.chevrolet.co.uk/OCRestServices/dealer/city/v1/faw/{city}?distance=14000&maxResults=50'
        r = session.get(url, headers=headers)
        data = r.json()

        dealers = data.get('payload', {}).get('dealers', [])
        for dealer in dealers:
            dealer_url = dealer.get('dealerUrl')

            locator_domain = 'chevrolet.co.uk'
            page_url = r.url
            location_type = 'dealer'
            location_name = dealer.get('dealerName')
            store_number = MISSING

            address = dealer.get('address', {})
            street_address = address.get('addressLine1', MISSING)
            city = address.get('cityName', MISSING)
            zip_code = address.get('postalCode', MISSING)
            state = MISSING
            country_code = address.get('countryCode', MISSING)

            geolocation = dealer.get('geolocation', {})
            latitude = geolocation.get('latitude', MISSING)
            longitude = geolocation.get('longitude', MISSING)

            contact = dealer.get('generalContact', {})
            phone = contact.get('phone1').replace(' ', '')
            hours_of_operation = MISSING

            if dealer_url not in dealer_map:
                dealer_map[dealer_url] = True
                yield [
                    locator_domain,
                    page_url,
                    location_name,
                    location_type,
                    store_number,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    latitude,
                    longitude,
                    phone,
                    hours_of_operation
                ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
