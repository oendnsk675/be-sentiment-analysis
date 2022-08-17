import tweepy
from textblob import TextBlob
import re
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

bearer_token = 'AAAAAAAAAAAAAAAAAAAAAKFxcgEAAAAAlXDfNaBugN5zcW4zB27xxg3ZD%2FU%3Doj9oSuZ0Nax1qi8Lgd3mBfAu9MN1EjNzgwa4qAjM2POSbvOpGj'

unique_user = []
hit_data = 0

client = tweepy.Client(bearer_token=bearer_token)

class Response(Resource):
	def post(self):
		content_type = request.headers.get('Content-type')
		if content_type == 'application/json':
			data_query = request.json
			tweets = client.search_recent_tweets(query=data_query['query'],  tweet_fields=['created_at', 'public_metrics', 'author_id'],max_results=100)
			data = {
				"positive": 0,
				"netral": 0,
				"negative": 0,
			}
			
			for tweet in tweets.data:
				tweet_clean = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet.text).split())
				analysis = TextBlob(tweet_clean)

				if analysis.sentiment.polarity > 0.0:
					data['positive'] += 1
				elif analysis.sentiment.polarity == 0.0:
					data['netral'] += 1
				else:
					data['negative'] += 1
			
			data = dict(sorted(data.items(), key=lambda item: item[1]))
			if list(data)[-1] == "positive":
				data["summary"] = f"Berdasarkan hasil analisa kata {data_query['query']} sangat disukai"
			elif list(data)[-1] == "netral":
				data["summary"] = f"Berdasarkan hasil analisa kata {data_query['query']} biasa saja"
			else:
				data["summary"] = f"Berdasarkan hasil analisa kata {data_query['query']} sangat tidak disukai"


			return {
				'msg': 'successfully analysis the query!',
				'data': data
			}
		else:
			return {
				'msg': 'Content-Type not supported!'
			}

	def get(self):
		return {
				'msg': 'successfully ygy!'
			} 
		
class User(Resource):
	def get(self):
		return {
			"msg": "Successfully retrive data user",
			"data": unique_user,
			"size": len(unique_user)
		}
	
	def post(self):
		
		data_query = request.json['data']
		if data_query not in unique_user:
			unique_user.append(data_query)
		else:
			return {
				"msg": "User already exists",
				"data": unique_user,
				"size": len(unique_user)
			}
		
		return {
			"msg": "Successfully add data user",
			"data": unique_user,
			"size": len(unique_user)
		}
                

class HitResource(Resource):

	def post(self):
		global hit_data

		hit_data += 1

		return {
			"msg": "Successfully add hit data",
			"data": hit_data
		}

	def get(self):
		return {
			"msg": "Successfully retrive hit data",
			"data": hit_data
		}

api.add_resource(Response, '/api/analysis')
api.add_resource(User, '/api/user')
api.add_resource(HitResource, '/api/hit')
if __name__ == '__main__':
	app.run(debug=True)