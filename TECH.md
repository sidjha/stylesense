# Must have

## Tech

- Subscription to the #ootd tag from IG's real-time api - [reference this blog post](http://blog.pamelafox.org/2012/04/using-instagram-real-time-api-from.html)
 - Filter in app.py, then push the rest to Parse app
- Which two pictures to show?
 - Connect with rating system so that we can use the rank for a "weighted randomization"
 - [Reference this stackoverflow post](http://stackoverflow.com/questions/1367181/in-need-of-a-random-hot-or-not-algorithm-solutions)
- Ranking
 - Use either trueskill or elo rating system
- Persisting votes in the database
- Updating global leaderboard
 - Get top 5 from ranking system and show IG handle along with winning picture and votes
 - Done on the fly
 
## UI
 
- Basically move current pics to a score view (move them down essentially with the score and display as a thumbnail) and fade in new pics
- If you click on a previous pic, it should take you to the instagram link

## Analytics

- GA for basic analytics
- Mixpanel for event tracking
 - Track votes and skips
