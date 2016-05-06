'use strict';

(function()
{
	exports.clean = function(json)
	{
		return json.replace(/\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*\/+/g, "").replace(/\/\/.*/g,"");
	}
})();