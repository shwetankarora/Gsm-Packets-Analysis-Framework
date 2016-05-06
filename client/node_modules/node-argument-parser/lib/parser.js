'use strict';

(function()
{
	var fs = require('fs')
		, changeCase = require('change-case');

	var Parser = function(json, process)
	{
		this.json = json;
		this.process = process;

		this.argv = {};

		return this.dissect();
	}

	Parser.prototype =
	{
		dissect : function()
		{
			if(this.json.defaults != null
			&& this.json.defaults.help)
			{
				this.create(true);
			}

			var that = this;
			var next = null;

			this.process.argv.forEach(function(val, index, array)
			{
				if(index >= 2)
				{
					if(next != null)
					{
						that.argv[next] = val;

						next = null;
					}
					else
					{
						for(var i=0; i<that.json.arguments.length; i++)
						{
							if(val == "--" + that.json.arguments[i].full
							|| val == "-" + that.json.arguments[i].short)
							{
								var fullName = changeCase.camelCase(that.json.arguments[i].full.replace(/-/g, " "));

								if(!that.json.arguments[i].value)
								{
									that.argv[fullName] = true;
								}
								else
								{
									next = fullName;
								}
							}

							if(that.argv.help !== undefined)
							{
								if(val == "--help")
								{
									that.argv.help = true;
								}
							}
						}
					}
				}
			});

			return this.argv;
		},

		create : function(withHelp)
		{
			if(withHelp)
			{
				this.argv.help = false;
			}

			var that = this;

			this.json.arguments.forEach(function(val, index, array)
			{
				var fullName = changeCase.camelCase(val.full.replace(/-/g, " "));

				that.argv[fullName] = val.value ? null : false;
			});
		}
	}

	exports.dissect = function(json, process)
	{
		return new Parser(json, process);
	}
})();
