# Node Argument Parser
Quick argument parser for Node.JS

### Installation

```shell
$ npm install node-argument-parser -g
```

### Description

v0.1.0
Fixed publish bug.

## Quick Usage

You will need to create a file to place your configurations.

**arguments.json**
```json
/* SAMPLE */

{
	"arguments" : [
		{
			"full" : "file", // full version (e.g. --file)
			"short" : "f", // short version (e.g. -f)
			"value" : true, // expects value (e.g. --file input)
			"description" : "File for parse" // for help display
		},
		{
			"full" : "overwrite", // required
			"short" : "o", // required
			"description" : "Should overwrite changes?" // required (if has help)
		}
	],
	"defaults" : {
		"help" : true, // displays help on --help
		"helpExtras" : "Documentation can be fount at: http://foo.eu/" // extras (optional)
	}
}
```

After that, you can start using it!

**test.js**
```javascript
var argumentParser = require("node-argument-parser");

var argv = argumentParser.parse("./arguments.json", process);

console.log(argv);
```

Now you just need to test your application:
```shell
$ node test.js
  { help: false, file: null, overwrite: false }

$ node test.js --file input -o
  { help: false, file: 'input', overwrite: true }

$ node test.js --help
  Usage: node test.js [options argument]

  Options:

    -f, --file		File for parse (expects value)
    -o, --overwrite	Should overwrite changes?

  Example:
   node test.js --file sampleValue -o 

  Documentation can be fount at: http://foo.eu/
```
