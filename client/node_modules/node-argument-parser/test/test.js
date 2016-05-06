var argumentParser = require("node-argument-parser");

var argv = argumentParser.parse("./arguments.json", process);

console.log(argv);