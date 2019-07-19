const Apify = require('apify');
const axios = require('axios');
const extract = new RegExp('<script>(.*)<\/script>', 'm');
Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  return await axios({
    method: "GET",
    url: "http://kitchencollection.com/stores-kitchen-collection.php"
  }).then((resp) => {
    data = [];
    for (let line of resp.data.split("\n")){
      if (line.startsWith('[ "')){
        row = [];
        for (let v of line.split('",')){
          v = v.replace(/\[|"|,|\]|/g, '').trim();
          if (v.length > 0){row.push(v)}
        }
        data.push({
            locator_domain: 'kitchencollection.com',
            location_name: row[1].split('<br>')[0],
            street_address: row[1].split('<br>')[1],
            city: row[2],
            state: row[3],
            zip: row[4].replace('.', ''),
            country_code: 'US',
            store_number: '<MISSING>',
            phone: row[5],
            location_type: '<MISSING>',
            latitude: '<MISSING>',
            longitude: '<MISSING>',
            hours_of_operation: '<MISSING>',
        });
      }
    }
    return data;
  });
}
