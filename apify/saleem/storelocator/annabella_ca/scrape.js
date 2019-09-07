const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  const $ = cheerio.load(await request.get({
    url: 'http://www.annabella.ca/storelocator.aspx/',
    headers: {
      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'
    }
  }));

  // unwrap table
  const pois = [];
  let currentPoi;
  $('table tr').each((_, element) => {
    let nameRow
    // everytime a name comes in the first column, a new poi is starting
    if ((nameRow = $('td', element).eq(0).text().trim()) !== "") {
      currentPoi = { location_name: nameRow };
      pois.push(currentPoi);
      currentPoi.address = "";
      currentPoi.phone = ""
      currentPoi.hours = "";
    }
    // This line is to create consistency, since some addresses are in a single row element, where
    // others are spread across multiple rows.
    $('td', element).eq(1).find('br').replaceWith('\n');
    currentPoi.address += `${$('td', element).eq(1).text().trim()}\n`;
    currentPoi.phone += ` ${$('td', element).eq(2).text().trim()}`;
    currentPoi.hours += ` ${$('td', element).eq(3).text().trim()}`;
  });

  // Remove table headers
  pois.splice(0, 2);

  for (const poi of pois) {
    const { address1, address2, address3, city, state, zip } = poi.address.match(/^(?<address1>.*?)\b,?\s*?\n\s*?\b(?<city>.*?)\b, \b(?<state>.*?)\b\s*?\n\s*?\b(?<address2>.*?)\b\s*?\n(\s*?\b(?<address3>.*?)\b\s*?\n)?\s*?\b(?<zip>.*?)\b\s*?\n$/).groups;
    const street_address = `${address1} ${address2} ${address3 || ""}`.trim()

    records.push({
      locator_domain: 'annabella.ca',
      location_name: poi.location_name,
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone: poi.phone,
      location_type: '<MISSING>',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: poi.hours
    })
  }


	return records;

	// End scraper

}
