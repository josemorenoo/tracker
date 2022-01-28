import tweepy

consumer_key ="jrGZWJz46oxwqay1FalhzGDgZ"
consumer_secret ="daFWAxQNEjcx9UINyNJwnThdDcodGDqmZFJoH3YRCjf0E5g3jl"
access_key = "1478755386052292608-ZGCd0u1BYWcIxKWmrO37xT8o2Xvbrj"    
access_secret = "Trsa6G2d3ujI9YbyexHX1iIKFFg8DSZiaPlRiCPFraH2u"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)
api.update_status('Hello?')

