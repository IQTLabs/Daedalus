#!/usr/bin/env node

var NaturalNameGenerator = require('natural-filename-generator');

var g = new NaturalNameGenerator();

for(var i = 0; i < 10000; i++){
    var name = g.generate('foo');
    console.log(name);
}
