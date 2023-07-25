from flask import Flask, request, Response,Blueprint
from datetime import datetime
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from error_logs import *
import os
import re

load_dotenv("variables.env")

search_logs = Blueprint("search_logs",__name__)
ES_USER_NAME=os.environ["ES_USER_NAME"]
ES_PASSWORD=os.environ["ES_PASSWORD"]
ES_IP=os.environ["ES_IP"]
es_connection="http://{ES_USER_NAME}:{ES_PASSWORD}@{ES_IP}:9200".format(ES_USER_NAME=ES_USER_NAME,ES_PASSWORD=ES_PASSWORD,ES_IP=ES_IP)
# es_connection="http://localhost:9200"
es=Elasticsearch([es_connection])

# @app.route("/create_search_log",methods=["POST"])
def create_search_log(partner_id,phrase,total_search_results,auto_suggs_suggestions,search_type,search_parameters):
	try:
		es_search_logs_index_name=partner_id+os.environ["SEARCH_LOGS_INDEX"]
		index_exists=es.indices.exists(index=es_search_logs_index_name)
		if(index_exists):
			datetime_now=datetime.now()
			search_logs_dict={
				"timestamp":datetime_now,
				"searched_term":phrase,
				"total_search_results":total_search_results,
				"search_type":search_type,
				"search_parameters":search_parameters,
				"suggested_search_terms":auto_suggs_suggestions
			}
			es_result=es.index(index=es_search_logs_index_name,body=search_logs_dict)
			if(es_result['_shards']["successful"]>0):
				return Response("search_logs created",status=200)
			else:
				return Response("search_logs not created",status=500)
		else:
			return Response("es partner index not found",status=500)


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

@search_logs.route("/searches_by_volume",methods=["POST"])
def searches_by_volume():
	if(request.method=="POST"):
		try:
			sort_by="desc"
			result_size=10
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("result_size" in request.json):
				result_size=int(request.json["result_size"])
			

			if("sort_by" in request.json):
				sort_by=request.json["sort_by"].strip().lower()
				if(sort_by in ["desc","asc"]):
					pass
				else:
					error_dict={
						"error_msg":"sort_by is not expected value",
						"error_code":500,
						"request_json":request.json,
						"timestamp":datetime.now()
					}
					create_error_log(partner_id,error_dict)
					return Response("sort_by is not expected value",status=500)

			if("from_timestamp" in request.json):
				from_timestamp=request.json["from_timestamp"].strip()
			else:
				from_timestamp=None

			
			if("to_timestamp" in request.json):
				to_timestamp=request.json["to_timestamp"].strip()
			else:
				to_timestamp=None

			if("search_type" in request.json):
				search_type=request.json["search_type"].strip()
			else:
				search_type=None

			

			es_search_logs_index_name=partner_id+os.environ["SEARCH_LOGS_INDEX"]
			index_exists=es.indices.exists(index=es_search_logs_index_name)
			if(index_exists):
				most_searched_by_volume_query={
				  "size": 0,
				  "query":{
				  	"bool":{
				  		"must":[]
				  	}
				  },				  
				  "aggs": {
				    "group_by": {
				      "terms": {
				        "size": result_size,
				        "field": "searched_term.keyword",
				        "order": {
				          "_key":sort_by
				        }
				      }
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
					most_searched_by_volume_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp!=None and to_timestamp==None):
					range_query={
					    "range": {
					      "timestamp": {
					        "gte": from_timestamp
					      }
					    }
					  }
					most_searched_by_volume_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp==None and to_timestamp!=None):
					range_query={
					    "range": {
					      "timestamp": {
					        "lte": to_timestamp
					      }
					    }
					  }
					most_searched_by_volume_query["query"]["bool"]["must"].append(range_query)

				if(search_type!=None):
					if("query" in most_searched_by_volume_query):
						most_searched_by_volume_query["query"]["bool"]["must"].append({"match_phrase":{"search_type":search_type}})
					else:
						most_searched_by_volume_query["query"]["bool"]["must"].append({"match_phrase":{"search_type":search_type}})





				# print("es_search_logs_index_name:",es_search_logs_index_name)
				# print("most_searched_by_volume_query:",json.dumps(most_searched_by_volume_query))
				es_result=es.search(index=es_search_logs_index_name,body=most_searched_by_volume_query)
				# print("es_result:",es_result)
				return es_result['aggregations']["group_by"]["buckets"]



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


@search_logs.route("/most_search_results",methods=["POST"])
def most_search_results():
	if(request.method=="POST"):
		try:
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

			if("search_type" in request.json):
				search_type=request.json["search_type"].strip()
			else:
				search_type=None

			es_search_logs_index_name=partner_id+os.environ["SEARCH_LOGS_INDEX"]
			index_exists=es.indices.exists(index=es_search_logs_index_name)
			if(index_exists):
				most_search_results_query={
										  "from": from_index,
										  "size": result_size,
										  "query":{
										  	"bool":{
										  		"must":[]
										  	}
										  },
										  "sort": [{
										    "total_search_results": {
										      "order": "desc"
										    }
										  }, {
										    "timestamp": {
										      "order": "desc"
										    }
										  }]
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
					most_search_results_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp!=None and to_timestamp==None):
					range_query={
					    "range": {
					      "timestamp": {
					        "gte": from_timestamp
					      }
					    }
					  }
					most_search_results_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp==None and to_timestamp!=None):
					range_query={
					    "range": {
					      "timestamp": {
					        "lte": to_timestamp
					      }
					    }
					  }
					most_search_results_query["query"]["bool"]["must"].append(range_query)

				if(search_type!=None):
					if("query" in most_search_results_query):
						search_type_query={
							"match_phrase":{"search_type":search_type}
						}
						most_search_results_query["query"]["bool"]["must"].append(search_type_query)
					else:
						search_type_query={
							"match_phrase":{
								"search_type":search_type
							}
						}
						most_search_results_query["query"]["bool"]["must"].append(search_type_query)
				es_result=es.search(index=es_search_logs_index_name,body=most_search_results_query)
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


@search_logs.route("/search_types_count",methods=["POST"])
def search_types_count():
	if(request.method=="POST"):
		try:
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)
			if("from_timestamp" in request.json):
				from_timestamp=request.json["from_timestamp"].strip()
			else:
				from_timestamp=None

			
			if("to_timestamp" in request.json):
				to_timestamp=request.json["to_timestamp"].strip()
			else:
				to_timestamp=None

			if("search_type" in request.json):
				search_type=request.json["search_type"].strip()
			else:
				search_type=None


			es_search_logs_index_name=partner_id+os.environ["SEARCH_LOGS_INDEX"]
			index_exists=es.indices.exists(index=es_search_logs_index_name)

			if(index_exists):
				search_types_count_query={
					  "size": 0,
					  "query":{
					  	"bool":{
					  		"must":[]
					  	}
					  },
					  "aggs": {
					    "field_type_count": {
					      "terms": {
					        "field": "search_type.keyword"
					      }
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
					search_types_count_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp!=None and to_timestamp==None):
					range_query={
					    "range": {
					      "timestamp": {
					        "gte": from_timestamp
					      }
					    }
					  }
					search_types_count_query["query"]["bool"]["must"].append(range_query)
				elif(from_timestamp==None and to_timestamp!=None):
					range_query={
					    "range": {
					      "timestamp": {
					        "lte": to_timestamp
					      }
					    }
					  }
					search_types_count_query["query"]["bool"]["must"].append(range_query)

				if(search_type!=None):
					if("query" in search_types_count_query):
						search_type_query={
							"match_phrase":{"search_type":search_type}
						}
						search_types_count_query["query"]["bool"]["must"].append(search_type_query)
					else:
						search_type_query={
							"match_phrase":{
								"search_type":search_type
							}
						}
						search_types_count_query["query"]["bool"]["must"].append(search_type_query)
				es_result=es.search(index=es_search_logs_index_name,body=search_types_count_query)
				# print("es_result:",es_result)
				return es_result['aggregations']["field_type_count"]["buckets"]

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

			


