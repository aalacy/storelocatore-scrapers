const Apify = require('apify');
const child_process = require("child_process"); 
const util = require('util');
const fs = require('fs-extra');
const csv = util.promisify(require('csv-parse'));  
const glob = require("glob");

function fail(message) {
	console.log(message);
	process.exit(1);
}

(async () => {
	console.log("in main.js");
	console.log("starting scrape.....");
	const exec = util.promisify(child_process.exec);
	let err, stdout, stderr;
	try {
		const environment = { env: {
			APIFY_LOCAL_STORAGE_DIR: "apify_storage",
			APIFY_CHROME_EXECUTABLE_PATH: "/usr/bin/google-chrome",
			NODE_ENV: "production",
			NODE_PATH: "/usr/local/lib/node_modules/"
		}};
		({ err, stdout, stderr } = await exec('node scrape.js', environment));
	} catch(err) {
		fail(`error executing scraper: ${err}`);
	}
	console.log('stdout:', stdout);
	console.log('stderr:', stderr);

	if (!fs.existsSync('./apify_storage/datasets/default')) {
		fail("scraper did not produce any output data!");
	}

	let pois = [];
	try {
		glob("./apify_storage/datasets/default/*.json", function(err, files) {
			if(err) {
				console.log("Cannot read output data directory", err);
			}
			files.forEach(function(file) {
				fs.readFile(file, 'utf8', function (err, data) {
					if(err) {
						console.log("Failed to read file: ", err);
					}
					let item = JSON.parse(data);
					pois.push(item);
				});
			});
		});
		console.log(`number of pois: ${pois.length}`);
	} catch(error) {
		console.log(error);
		fail("error parsing output data!");
	}
	await Apify.pushData(pois);
})();
