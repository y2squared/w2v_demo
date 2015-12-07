const express = require('express');
const path = require('path');
const logger = require('morgan');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const socketio = require('socket.io');
const routes = require('./routes/index');
const passport = require('passport');
const strategy = require('passport-twitter').Strategy;
const port = '8000'; 
const expressSession = require('express-session');
const MongoStore = require('connect-mongo')(expressSession);
const base64 = require('urlsafe-base64');
//const expressSessionStore = new expressSession.MemoryStore;
const passportConfig = {
	twitter: {
		consumerKey: process.env.TWITTER_CONSUMER_KEY,
		consumerSecret: process.env.TWITTER_CONSUMER_SECRET,
		callbackURL: "http://app.y2squared.me/twitter/callback" //帰ってくる先
	}
};

const app = express();
const cookie = require('cookie-parser/node_modules/cookie');
const util = require('util');
const co = require('co');
const promisify = require('es6-promisify');

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// uncomment after placing your favicon in /public
//app.use(express.static(path.join(__dirname, 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));


// passport setup
passport.serializeUser(function(user, done){
	return done(null, user);
});

passport.deserializeUser(function(obj, done) {
	return done(null, obj);
});

passport.use(new strategy(passportConfig.twitter, function(token, tokenSecret, profile, done){
	return process.nextTick(function() {
		profile.token = token;
		profile.tokenSecret = tokenSecret;
		return done(null, profile)});
}));

//session setting
app.use(expressSession({
	store: new MongoStore({
		db: 'testdb',
		host: 'localhost',
		clear_interval: 60 * 60 // 1hour
	}),
	//store: expressSessionStore,
	secret: '"'+process.env.COOKIE_SECRET+'"',
	resave: true,
	saveUninitialized: true,
	cookie: {
		httpOnly: false,
		maxAge: 60*60*1000 // 1 hour
	}
}));

app.use(passport.initialize());
app.use(passport.session());

app.use('/nicomas-tag-analysis', routes);
app.get('/twitter/auth', passport.authenticate('twitter'));
app.get('/twitter/callback', passport.authenticate('twitter', {
	failureRedirect: '/twitter/authenticationError' ,
	successRedirect: '/nicomas-tag-analysis'	
}));

app.get('/twitter/authenticationError', function(req, res){
	return res.end('authentication error.');
});

app.post('/twitter/tweet', function(req,res) {
	const Twitter = require('twitter');
	const tweet = req.body.tweet;
        const client = new Twitter({
        	consumer_key: process.env.TWITTER_CONSUMER_KEY,
		consumer_secret: process.env.TWITTER_CONSUMER_SECRET,
		access_token_key: req.session.passport.user.token,
		access_token_secret: req.session.passport.user.tokenSecret
	});
	
	const img = base64.decode(req.body.img);
	client.post('media/upload', {media:img}, function(error,media,response){
		if(!error){
			console.log("media tweet done")
			const media_id = media.media_id_string;
			client.post('statuses/update', {status:tweet, media_ids: media_id}, function(error,tweet,response){
				if(error){
					console.log(util.inspect(error));
				}
				res.redirect('/nicomas-tag-analysis');
			});
		}else {
			console.log(util.inspect(error));
		}
	});
});


// catch 404 and forward to error handler
app.use(function(req, res, next) {
  const err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});

module.exports = app;
