var jsonCleaner = require("json-cleaner")
	, fs = require('fs');

try
{
	file = fs.readFileSync('./test.json', 'utf8');
}
catch(e)
{
	err = true;
	console.log('Couldn\'t access \'test.json\'!');
}

console.log(jsonCleaner.clean(file));