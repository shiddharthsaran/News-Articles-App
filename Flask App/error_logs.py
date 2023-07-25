from flask import Flask, request, Response,Blueprint
from datetime import datetime
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import re

load_dotenv("variables.env")

error_logs = Blueprint("error_logs",__name__)

ES_USER_NAME=os.environ["ES_USER_NAME"]
ES_PASSWORD=os.environ["ES_PASSWORD"]
ES_IP=os.environ["ES_IP"]
es_connection="http://{ES_USER_NAME}:{ES_PASSWORD}@{ES_IP}:9200".format(ES_USER_NAME=ES_USER_NAME,ES_PASSWORD=ES_PASSWORD,ES_IP=ES_IP)
# es_connection="http://localhost:9200"
es=Elasticsearch([es_connection])

def create_error_log(partner_id,error_dict):
	try:
		es_error_logs_index_name=partner_id+os.environ["ERROR_LOGS_INDEX"]
		# print("es_error_logs_index_name:",es_error_logs_index_name)
		index_exists=es.indices.exists(index=es_error_logs_index_name)
		if(index_exists):
			# print("error_dict:",error_dict)
			es_result=es.index(index=es_error_logs_index_name,body=error_dict)
			if(es_result['_shards']["successful"]>0):
				return Response("error_logs created",status=200)
			else:
				return Response("error_logs not created",status=500)
		else:
			return Response("es partner index not found",status=500)


	except Exception as e:
		e=str(e)
		return Response(e,status=500)

@error_logs.route("/read_error_logs",methods=["POST"])
def read_error_logs():
	try:
		if(request.method=="POST"):
			sort_by="desc"
			from_index=0
			result_size=10
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("result_size" in request.json):
				result_size=int(request.json["result_size"])

			if("from_index" in request.json):
				from_index=int(request.json["from_index"])

			

			if("from_timestamp" in request.json):
				from_timestamp=request.json["from_timestamp"].strip()
			else:
				from_timestamp=None

			
			if("to_timestamp" in request.json):
				to_timestamp=request.json["to_timestamp"].strip()
			else:
				to_timestamp=None

			if("error_code" in request.json):
				error_code=int(request.json["error_code"])
			else:
				error_code=None

			if("error_msg" in request.json):
				error_msg=request.json["error_msg"].strip()
			else:
				error_msg=None

			es_error_logs_index_name=partner_id+os.environ["ERROR_LOGS_INDEX"]
			index_exists=es.indices.exists(index=es_error_logs_index_name)
			if(index_exists):
				error_logs_read_query={
					"from":from_index,
					"size":result_size,
					"query":{
						"bool":{
							"must":[]
						}
					}
				}
				if(from_timestamp==None and to_timestamp==None):
					pass
				elif(from_timestamp!=None and to_timestamp!=None):
					range_query={
					    "range": {
					      "timestamp": {
					        "gte": from_timestamp,
					        "lte": to_timestamp
					      }
					    }
					  }
					error_logs_read_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp!=None and to_timestamp==None):
					range_query={
					    "range": {
					      "timestamp": {
					        "gte": from_timestamp
					      }
					    }
					  }
					error_logs_read_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp==None and to_timestamp!=None):
					range_query={
					    "range": {
					      "timestamp": {
					        "lte": to_timestamp
					      }
					    }
					  }
					error_logs_read_query["query"]["bool"]["must"].append(range_query)
				if(error_code!=None):
					term_query={
						"term":{
							"error_code":{
								"value":error_code
							}
						}
					}
					error_logs_read_query["query"]["bool"]["must"].append(term_query)

				if(error_msg!=None):
					match_query={
						"match_phrase":{
							"error_msg":error_msg
						}
					}
					error_logs_read_query["query"]["bool"]["must"].append(match_query)
				# print("error_logs_read_query:",error_logs_read_query)
				es_result=es.search(index=es_error_logs_index_name,body=error_logs_read_query)
				# print("es_result:",es_result)
				es_result=es_result["hits"]["hits"]
				return_result=[]
				for result in es_result:
					return_result.append(result["_source"])

				return return_result



	except Exception as e:
		e=str(e)
		error_dict={
					"error_msg":e,
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
		create_error_log(partner_id,error_dict)
		return Response(e,status=500)
