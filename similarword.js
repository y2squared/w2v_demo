var mongoose = require('mongoose');
// connect to testdb
//mongoose.connect('mongodb://133.130.113.188:27017/testdb');
mongoose.connect('mongodb://localhost/testdb');
var db = mongoose.connection;

var similarwordSchema = mongoose.Schema({
    src: String,
    dst: String,
    score: Number
});

var similarword = mongoose.model( 'similarword', similarwordSchema );

module.exports=similarword;
