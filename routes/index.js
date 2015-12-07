var express = require('express');
var mongoose= require('mongoose');
var util    = require('util');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'word2vec toy example' , user: req.user});
});

module.exports = router;
