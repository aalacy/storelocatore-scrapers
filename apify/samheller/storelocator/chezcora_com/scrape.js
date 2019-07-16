const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');

Apify.main(async () => {
  await scrape();
});

async function scrape() {
  return await axios({
    method: 'GET',
    url: 'https://www.chezcora.com/en/breakfast-restaurants'
  }).then(async (resp) => {
      document = new JSDOM(resp.data).window.document;
      rows = document.querySelectorAll('.resto-contact');
      for (let row of rows){
        latlon = extractLatLon(row.querySelector('script').textContent)
        store = row.querySelector('h2').textContent
          .replace('Cora -', '')
          .trim()
        address = row.querySelector('p:nth-child(4)')
          .innerHTML
          .replace('<br>', "\n")
        address = sanitize(address);
        area = address[1].split(', ')
        address = address[0];
        phone = row.querySelector('p.telephone').textContent.trim();
        hours = sanitize(row.querySelector('.tabHoraire').textContent).join(", ");
        
        //Edge case cleaning
        hours = hours.replace(/^The.*?, /, '').replace(/, \*\*.*/, '');

        await Apify.pushData([{
          locator_domain: 'chezcora.com',
          location_name: store,
          street_address: address,
          city: area[0].trim(),
          state: area[1].trim(),
          zip: area[2].trim(),
          country_code: 'CA',
          store_number: '<MISSING>',
          phone: phone,
          location_type: '<MISSING>',
          latitude: latlon.lat,
          longitude: latlon.lon,
          hours_of_operation: hours,
        }]);

      }
  })
}


function extractLatLon(scriptText){
  data = sanitize(scriptText);
  return {
    lat: data[1].replace('lat:', '').replace(',', '').trim(),
    lon: data[2].replace('lon:', '').replace(',', '').trim()
  }
}

function sanitize(textRow){
  sane = [];
  for (s of textRow.split("\n")){
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
}
// 	const record = {
//     locator_domain: 'safegraph.com',
//     location_name: 'safegraph',
//     street_address: '1543 mission st',
//     city: 'san francisco',
//     state: 'CA',
//     zip: '94107',
//     country_code: 'US',
// 		store_number: '<MISSING>',
// 		phone: '<MISSING>',
// 		location_type: '<MISSING>',
//     naics_code: '518210',
//     latitude: -122.417774,
//     longitude: -122.417774,
// 		hours_of_operation: '<MISSING>',
// 	};

// 	return [record];

// 	// End scraper

// }
