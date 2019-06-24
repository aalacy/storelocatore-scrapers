const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const mapKeys = require('lodash.mapkeys');

(async () => {
	const exec = util.promisify(child_process.exec);
	await exec('python ryans.py');
	let data = await fs.readFile('ryans.csv');
	let parsed = await csv(data);
	let header = parsed[0];
	let translation = {...header}
	let rows = parsed.slice(1);
	let pois = rows.map((row) => mapKeys({...row}, (value, key) => { return translation[key]; } ));
	await Apify.pushData(pois);
})();
