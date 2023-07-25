from flask import Flask, request, Response,Blueprint
from datetime import datetime
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import uuid
import re
from search_logs import *
from error_logs import *
load_dotenv("variables.env")

app = Flask(__name__)
app.register_blueprint(search_logs)
app.register_blueprint(error_logs)
ES_USER_NAME=os.environ["ES_USER_NAME"]
ES_PASSWORD=os.environ["ES_PASSWORD"]
ES_IP=os.environ["ES_IP"]
es_connection="http://{ES_USER_NAME}:{ES_PASSWORD}@{ES_IP}:9200".format(ES_USER_NAME=ES_USER_NAME,ES_PASSWORD=ES_PASSWORD,ES_IP=ES_IP)
# es_connection="http://localhost:9200"
es=Elasticsearch([es_connection])

def get_es_read_results(es_articles_index_name,sort_by,from_result,request,partner_id,result_size=10):
	try:
	
		es_read_query={
					"_source":["news_id"],
					  "query": {
						"match_all": {
						}
					  }
					  , "from": from_result,
					  "size": result_size
					}
		if(sort_by=="relv"):
			es_read_query["sort"]=[
									  {
										 "_score":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="desc"):
			es_read_query["sort"]=[
									  {
										 "date_created":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="asc"):
			es_read_query["sort"]=[
									  {
										 "date_created":{
											"order":"asc"
										 }
									  }
								   ]
		# print("es_read_query:",json.dumps(es_read_query))
		es_read_query_response= es.search(index=es_articles_index_name, body=es_read_query)
		es_read_results=es_read_query_response["hits"]["hits"]
		total_read_results=es_read_query_response["hits"]["total"]["value"]
		# print("total_read_results:",total_read_results)
		# print("es_read_results:",es_read_results)
		news_id_list=list()
		for n,result in enumerate(es_read_results):
			# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
			news_id_list.append(result["_source"]["news_id"])



		return total_read_results,news_id_list
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
def get_es_search_results(es_articles_index_name,search_keyword,from_result,sort_by,fields,request,partner_id,result_size=10):
	try:
		# print("fields:",fields)
		# print("search_keyword:",search_keyword)

		must_list=list()

		matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
		# print("matches:",matches)
		for match in matches:
			# print(match)
			if(match[0]):
				search_keyword=match[0]
				multi_match_dict={	
							"query":search_keyword,				   
						   "fields":fields,
						   "operator":"and",
						   "type":"phrase"
						}
				must_list.append({"multi_match":multi_match_dict})
			elif(match[1]):
				search_keyword=match[1]
				for term in search_keyword.strip().split():
					term=term.strip()
					if(re.search("\d",term)):
						# print("term1:",term)
						multi_match_dict={	
								"query":term,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
						must_list.append({"multi_match":multi_match_dict})
					else:
						multi_match_dict={	
								"query":term,				   
							   "fields":fields,
							   "operator":"and",
							   "fuzziness":"auto"
							}
						must_list.append({"multi_match":multi_match_dict})




		es_search_query={
							"_source":["news_id"],					   
						   "query":{
							  "bool":{
								 "must":must_list
							  }
						   },
						   "from":from_result,
						   "size":result_size
						}

		if(sort_by=="relv"):
			es_search_query["sort"]=[
									  {
										 "_score":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="desc"):
			es_search_query["sort"]=[
									  {
										 "date_created":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="asc"):
			es_search_query["sort"]=[
									  {
										 "date_created":{
											"order":"asc"
										 }
									  }
								   ]
		# print("es_search_query:",json.dumps(es_search_query))
		es_search_query_response= es.search(index=es_articles_index_name, body=es_search_query)
		# print("\n")
		# print("es_search_query_response:",es_search_query_response)
		es_search_took_time=es_search_query_response["took"]
		es_search_results=es_search_query_response["hits"]["hits"]
		total_search_results=es_search_query_response["hits"]["total"]["value"]
		# results_dict={}
		news_id_list=list()
		for n,result in enumerate(es_search_results):
			# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
			news_id_list.append(result["_source"]["news_id"])
		return total_search_results,news_id_list,es_search_took_time
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


# es_articles_index_name,phrase,from_result,sort_by,"auto_suggs_field.trigram")
def get_es_adv_search_results(es_articles_index_name,from_result,sort_by,field_query_values,request,partner_id,result_size=10):
	try:
		tags_should_list=list()

		# for tag in tags:
		# 	temp_dict={
				# "multi_match":{
				# 	"query":tag,
				# 	"fields":["news_tags"],
				# 	"operator":"and",
				# 	"fuzziness":"auto"
				# }
		# 	}
		# 	tags_should_list.append(temp_dict)
		# print("hi")
		if("result_size" in field_query_values):
			result_size=field_query_values["result_size"]






		es_adv_search_query={
						   
						   "query":{
							  "bool":{
								 "must":[
								 ]
							  }
						   },
						   "from":from_result,
						   "size":result_size
						}

		if("from_pub_date" in field_query_values and "to_pub_date" in field_query_values):
			date_range_dict={
				"range":{
					"date_created":{
						"gte":field_query_values["from_pub_date"],
						"lte":field_query_values["to_pub_date"]
					}
				}
			}
			es_adv_search_query["query"]["bool"]["must"].append(date_range_dict)
		elif("from_pub_date" in field_query_values):
			date_range_dict={
				"range":{
					"date_created":{
						"gte":field_query_values["from_pub_date"]
					}
				}
			}
			es_adv_search_query["query"]["bool"]["must"].append(date_range_dict)

		elif("to_pub_date" in field_query_values):
			date_range_dict={
				"range":{
					"date_created":{
						"lte":field_query_values["to_pub_date"]
					}
				}
			}
			es_adv_search_query["query"]["bool"]["must"].append(date_range_dict)


		if("author_name" in field_query_values):
			search_keyword=field_query_values["author_name"]
			fields=["author_name"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})

			# author_name_dict={
			# 	"bool":{
			# 		"should":[
			# 			{
			# 				"multi_match":{
			# 					"query":,
			# 					"fields":["author_name"],
			# 					"operator":"and",
			# 					"fuzziness":"auto"
			# 				}
			# 			}
			# 		]
			# 	}
			# }
			# es_adv_search_query["query"]["bool"]["must"].append(author_name_dict)

		if("phrase" in field_query_values):
			search_keyword=field_query_values["phrase"]
			fields=["suggs_search_field.trigram"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
			# phrase_dict={
			# 	"bool":{
			# 		"should":[
			# 			{
			# 				"multi_match":{
			# 					"query":field_query_values["phrase"],
			# 					"fields":["suggs_search_field.trigram"],
			# 					"operator":"and",
			# 					"fuzziness":"auto"
			# 				}
			# 			}
			# 		]
			# 	}
			# }
			# es_adv_search_query["query"]["bool"]["must"].append(phrase_dict)

		if("topic" in field_query_values):
			search_keyword=field_query_values["topic"]
			fields=["associated_keywords","associated_tags"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
		if("author_ids" in field_query_values):
			fields=["author_id"]

			bool_should_dict={
				"bool":{
					"should":[]
				}
			}

			for field in fields:
				terms_dict={
					"terms":{
						field:field_query_values["author_ids"]
					}
				}
				bool_should_dict["bool"]["should"].append(terms_dict)

			es_adv_search_query["query"]["bool"]["must"].append(bool_should_dict)

		if("category_ids" in field_query_values):
			fields=["primary_category_id","other_category_ids"]

			bool_should_dict={
				"bool":{
					"should":[]
				}
			}

			for field in fields:
				terms_dict={
					"terms":{
						field:field_query_values["category_ids"]
					}
				}
				bool_should_dict["bool"]["should"].append(terms_dict)

			es_adv_search_query["query"]["bool"]["must"].append(bool_should_dict)

		if("location_ids" in field_query_values):
			fields=["location_id"]

			bool_should_dict={
				"bool":{
					"should":[]
				}
			}

			for field in fields:
				terms_dict={
					"terms":{
						field:field_query_values["location_ids"]
					}
				}
				bool_should_dict["bool"]["should"].append(terms_dict)

			es_adv_search_query["query"]["bool"]["must"].append(bool_should_dict)

		if("news_type" in field_query_values):
			search_keyword=field_query_values["news_type"]
			fields=["news_type"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})








		if("location" in field_query_values):
			search_keyword=field_query_values["location"]
			fields=["location_name"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
			# location_dict={
			# 	"bool":{
			# 		"should":[
			# 			{
			# 				"multi_match":{
			# 					"query":field_query_values["location"],
			# 					"fields":["location_name"],
			# 					"operator":"and",
			# 					"fuzziness":"auto"
			# 				}
			# 			}
			# 		]
			# 	}
			# }
			# es_adv_search_query["query"]["bool"]["must"].append(location_dict)

		if("category_name" in field_query_values):
			search_keyword=field_query_values["category_name"]
			fields=["primary_category_name","other_category_names"]
			matches=re.findall("[\'\"]([^\'\"]+)[\'\"]|\s*(.*)\s*",search_keyword)
			for match in matches:
				if(match[0]):
					search_keyword=match[0]
					multi_match_dict={	
								"query":search_keyword,				   
							   "fields":fields,
							   "operator":"and",
							   "type":"phrase"
							}
					es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
				elif(match[1]):
					search_keyword=match[1]
					for term in search_keyword.strip().split():
						term=term.strip()
						if(re.search("\d",term)):
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "type":"phrase"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
						else:
							multi_match_dict={	
									"query":term,				   
								   "fields":fields,
								   "operator":"and",
								   "fuzziness":"auto"
								}
							es_adv_search_query["query"]["bool"]["must"].append({"multi_match":multi_match_dict})
			# category_name_dict={
			# 	"bool":{
			# 		"should":[
			# 			{
			# 				"multi_match":{
			# 					"query":field_query_values["category_name"],
			# 					"fields":["primary_category_name","other_category_names"],
			# 					"operator":"and",
			# 					"fuzziness":"auto"
			# 				}
			# 			}
			# 		]
			# 	}
			# }
			# es_adv_search_query["query"]["bool"]["must"].append(category_name_dict)

		if(sort_by=="relv"):
			es_adv_search_query["sort"]=[
									  {
										 "_score":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="desc"):
			es_adv_search_query["sort"]=[
									  {
										 "date_created":{
											"order":"desc"
										 }
									  }
								   ]
		elif(sort_by=="asc"):
			es_adv_search_query["sort"]=[
									  {
										 "date_created":{
											"order":"asc"
										 }
									  }
								   ]
		es_adv_search_query_response= es.search(index=es_articles_index_name, body=es_adv_search_query)
		# print("es_adv_search_query:",json.dumps(es_adv_search_query))
		es_adv_search_took_time=es_adv_search_query_response["took"]
		es_adv_search_results=es_adv_search_query_response["hits"]["hits"]
		total_search_results=es_adv_search_query_response["hits"]["total"]["value"]

		news_id_list=list()
		for n,result in enumerate(es_adv_search_results):
			# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
			news_id_list.append(result["_source"]["news_id"])
		return total_search_results,news_id_list,es_adv_search_took_time
	except Exception as e:
		e=str(e)
		# print("errr:",e)
		# print("request:",request)
		error_dict={
					"error_msg":e,
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
		create_error_log(partner_id,error_dict)
		return Response(e,status=500)
	

@app.route("/adv_search_articles",methods=["POST"])
def adv_search_articles():

	if(request.method=="POST"):
		try:
			# print("request:",request)
			partner_id=None
			# print("request.json:",request.json)
			field_query_values=dict()
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				
				return Response("partner_id not found",status=500)

			if("phrase" in request.json):
				phrase=request.json["phrase"].lower().strip()
				field_query_values["phrase"]=phrase

			else:
				error_dict={
					"error_msg":"phrase not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("phrase not found",status=500)

			if("from_pub_date" in request.json):
				from_pub_date=request.json["from_pub_date"].strip()
				field_query_values["from_pub_date"]=from_pub_date

			

			if("to_pub_date" in request.json):
				to_pub_date=request.json["to_pub_date"].strip()
				field_query_values["to_pub_date"]=to_pub_date


			

			if("author_name" in request.json):
				author_name=request.json["author_name"].lower().strip()
				field_query_values["author_name"]=author_name

			

			if("category_name" in request.json):
				category_name=request.json["category_name"].lower().strip()
				field_query_values["category_name"]=category_name

			

			if("topic" in request.json):
				topic=request.json["topic"].lower().strip()
				field_query_values["topic"]=topic

			

			if("location" in request.json):
				location=request.json["location"].lower().strip()
				field_query_values["location"]=location

			if("result_size" in request.json):
				result_size=int(str(request.json["result_size"]).lower().strip())
				field_query_values["result_size"]=result_size
			else:
				result_size=10
			

			if("sort_by" in request.json):
				sort_by=request.json["sort_by"].strip().lower()
				if(sort_by in ["relv","desc","asc"]):
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

			else:
				sort_by="relv"
			field_query_values["sort_by"]=sort_by
			# if("next_page" in request.json):
			# 	from_result=request.json["next_page"]
			# elif("prev_page" in request.json):
			# 	from_result=request.json["prev_page"]
			# else:
			# 	from_result=0
			if("start_index" in request.json):
				from_result=int(request.json["start_index"])
			else:
				from_result=0


			if("author_ids" in request.json):
				author_ids=request.json["author_ids"]
				field_query_values["author_ids"]=author_ids

			if("category_ids" in request.json):
				category_ids=request.json["category_ids"]
				field_query_values["category_ids"]=category_ids

			if("news_type" in request.json):
				news_type=request.json["news_type"]
				field_query_values["news_type"]=news_type

			if("location_ids" in request.json):
				location_ids=request.json["location_ids"]
				field_query_values["location_ids"]=location_ids







			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):
				total_search_results,news_id_list,es_search_took_time=get_es_adv_search_results(es_articles_index_name,from_result,sort_by,field_query_values,request,partner_id,result_size)
				# total_pages=total_search_results/10
				# print("total_pages:",total_pages)

				# current_page=(from_result+10)//10
				# print("current_page:",current_page)
				es_auto_suggs_query={
				  "suggest": {
					"suggs_search_field_phrases": {
					  "text": phrase,
					  "phrase":{
						"field":"suggs_search_field.trigram",
						"highlight":{
						  "pre_tag":"<em>",
						  "post_tag":"</em>"
						},
						"confidence":0,
						"max_errors":3
					  }
					}
				  }
				}
				resp = es.search(index=es_articles_index_name, body=es_auto_suggs_query)
				auto_suggs_suggestions=list()

				for suggestion_list in resp["suggest"]["suggs_search_field_phrases"]:
					for options in suggestion_list["options"]:
						auto_suggs_suggestions.append(options["text"])
				field_query_values.pop("phrase")
				# print("field_query_values:",field_query_values)
				create_search_log(partner_id,phrase,total_search_results,auto_suggs_suggestions,"advanced",field_query_values)


				return_dict=dict()
				return_dict={"news_ids":news_id_list}
				# return_dict=dict()
				# if(total_pages==0):
				# 	return_dict={"news_ids":[]}
				# elif(total_pages<=1):
				# 	return_dict={"news_ids":news_id_list}
				# else:

				# 	if(current_page==1):
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"next_page":from_result+10}
				# 	else:
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10,"next_page":from_result+10}


				return_dict={
					"results":return_dict
				}

				return return_dict,200
			else:
				# error_dict={
				# 	"error_msg":"es partner index not found",
				# 	"error_code":500,
				# 	"request_json":request.json,
				# 	"timestamp":datetime.now()
				# }
				# print("error_dict:",error_dict)
				# create_error_log(partner_id,error_dict)
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

@app.route("/search_articles",methods=["POST"])
def search():
	if(request.method=="POST"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("phrase" in request.json):
				phrase=request.json["phrase"].lower().strip()

			else:
				error_dict={
					"error_msg":"phrase not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("phrase not found",status=500)
			if("result_size" in request.json):
				result_size=int(request.json["result_size"])
			else:
				result_size=10
			sort_by="relv"
			if("sort_by" in request.json):
				sort_by=request.json["sort_by"].strip().lower()
				if(sort_by in ["relv","desc","asc"]):
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

			

			if("start_index" in request.json):
				from_result=int(request.json["start_index"])
			else:
				from_result=0

			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):
				total_search_results,news_id_list,es_search_took_time=get_es_search_results(es_articles_index_name,phrase,from_result,sort_by,["suggs_search_field.trigram"],request,partner_id,result_size)
				# print("total_search_results:",total_search_results)
				# total_pages=total_search_results/10
				# print("total_pages:",total_pages)

				# current_page=(from_result+10)//10
				# print("current_page:",current_page)
				es_auto_suggs_query={
				  "suggest": {
					"suggs_search_field_phrases": {
					  "text": phrase,
					  "phrase":{
						"field":"suggs_search_field.trigram",
						"highlight":{
						  "pre_tag":"<em>",
						  "post_tag":"</em>"
						},
						"confidence":0,
						"max_errors":3
					  }
					}
				  }
				}
				resp = es.search(index=es_articles_index_name, body=es_auto_suggs_query)
				auto_suggs_suggestions=list()

				for suggestion_list in resp["suggest"]["suggs_search_field_phrases"]:
					for options in suggestion_list["options"]:
						auto_suggs_suggestions.append(options["text"])
				create_search_log(partner_id,phrase,total_search_results,auto_suggs_suggestions,"standard",{"sort_by":sort_by})
				return_dict=dict()
				return_dict={"news_ids":news_id_list}
				# return_dict=dict()
				# if(total_pages==0):
				# 	return_dict={"news_ids":[]}
				# elif(total_pages<=1):
				# 	return_dict={"news_ids":news_id_list}
				# else:

				# 	if(current_page==1):
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"next_page":from_result+10}
				# 	else:
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10,"next_page":from_result+10}


				return_dict={
					"results":return_dict
				}

				return return_dict,200
				# title_total_search_results,es_title_search_took_time,title_results_dict=get_es_search_results(es_articles_index_name,search_keyword,from_title_result,sort_by,"news_title.trigram")
				
				# return render_template("search_results.html",closest_match_change=closest_match_change,closest_match=closest_match,user_search=request.form["search"],sort_by=sort_by,
				# 	len_author_results_dict=len(author_results_dict),author_total_search_results=author_total_search_results,es_author_search_took_time=es_author_search_took_time,author_results_dict=author_results_dict,from_author_result=from_author_result,
				# 	len_title_results_dict=len(title_results_dict),title_total_search_results=title_total_search_results,es_title_search_took_time=es_title_search_took_time,title_results_dict=title_results_dict,from_title_result=from_title_result)
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

@app.route("/articles_completion_suggs",methods=["POST"])
def articles_completion_suggs():
	if(request.method=="POST"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("phrase" in request.json):
				phrase=request.json["phrase"].lower().strip()

			else:
				error_dict={
					"error_msg":"phrase not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("phrase not found",status=500)

			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):
				es_auto_completion_query={
								  "suggest": {
								    "completion_suggestions": {
								      "prefix": phrase,
								      "completion": {
								        "field": "completion_field.completion",
								        "size": 5,
								        "skip_duplicates": True,
								        "fuzzy": {
								          "fuzziness": "AUTO"
								        }
								      }
								    }
								  },
								  "sort": [{
								    "_score": {
								      "order": "desc"
								    }
								  }]
								}
				resp = es.search(index=es_articles_index_name, body=es_auto_completion_query)
				# print("resp:",resp)
				completion_suggs_suggestions=list()

				for suggestion_list in resp["suggest"]["completion_suggestions"]:
					for options in suggestion_list["options"]:
						completion_suggs_suggestions.append(options["text"])


				# print("auto_suggs_suggestions:",auto_suggs_suggestions)

				return_dict={"suggestions":completion_suggs_suggestions}
				return return_dict
				
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


@app.route("/articles_auto_suggs",methods=["POST"])
def auto_suggs():
	if(request.method=="POST"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("phrase" in request.json):
				phrase=request.json["phrase"].lower().strip()

			else:
				error_dict={
					"error_msg":"phrase not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("phrase not found",status=500)

			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):

				es_auto_suggs_query={
				  "suggest": {
					"suggs_search_field_phrases": {
					  "text": phrase,
					  "phrase":{
						"field":"suggs_search_field.trigram",
						"highlight":{
						  "pre_tag":"<em>",
						  "post_tag":"</em>"
						},
						"confidence":0,
						"max_errors":3
					  }
					}
				  }
				}
				resp = es.search(index=es_articles_index_name, body=es_auto_suggs_query)
				# print("resp:",resp)
				auto_suggs_suggestions=list()

				for suggestion_list in resp["suggest"]["suggs_search_field_phrases"]:
					for options in suggestion_list["options"]:
						auto_suggs_suggestions.append(options["text"])


				# print("auto_suggs_suggestions:",auto_suggs_suggestions)

				return_dict={"suggestions":auto_suggs_suggestions}
				return return_dict
				
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


	





@app.route("/delete_article",methods=["DELETE"])
def delete_article():
	if(request.method=="DELETE"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("news_id" in request.json):
				news_id=int(request.json["news_id"])		

			else:
				error_dict={
					"error_msg":"news_id not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("news_id not found",status=500)
			# print(os.environ["ARTICLES_INDEX"])
			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):
				es_news_delete_query={
					  "query": {
						"bool": {
						  "must": [
							{"match": {
							  "news_id": news_id
							}}
						  ]
						}
					  }
					}

				es_delete_news_query_response= es.delete_by_query(index=es_articles_index_name, body=es_news_delete_query,refresh=True)
				# print("es_delete_news_query_response:",es_delete_news_query_response)
				if(es_delete_news_query_response["deleted"]>0):
					return Response("deleted article",status=200)
				else:
					error_dict={
						"error_msg":"could not delete article",
						"error_code":500,
						"request_json":request.json,
						"timestamp":datetime.now()
					}
					create_error_log(partner_id,error_dict)
					return Response("could not delete article",status=500)


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




@app.route("/update_article",methods=["PUT"])
def update_article():
	if(request.method=="PUT"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("news_id" in request.json):
				news_id=int(request.json["news_id"])		

			else:
				error_dict={
					"error_msg":"news_id not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("news_id not found",status=500)

			if("article_contents" in request.json):
				article_contents=request.json["article_contents"]
				if(len(article_contents)>0):
					source_string=str()
					# news_parameters_list=["news_id","news_title","news_sub_title","url","english_description","location","date_of_publishing","date_of_updating",
					# 		"author","author_group","editor","editor_team","byline","cover_image_caption_url","description_of_news","other_parameters",
					# 		"tags","keywords","primary_category","other_category","free_premium","news_type"]


					suggs_search_news_parameters_list=["heading","description","url","english_title","location_name","author_name","byline",
											"cover_image_url","cover_image_caption","story","associated_tags","associated_keywords","primary_category_name"]
					news_parameters_not_present_list=list()

					# if("news_id" in article_contents):
					# 	pass
					# else:
					# 	return Response("news_id not found",status=500)

					es_read_news_query={
						  "query": {
							"bool": {
							  "must": [
								{"match": {
								  "news_id": news_id
								}}
							  ]
							}
						  }
						}

					es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
					index_exists=es.indices.exists(index=es_articles_index_name)
					if(index_exists):

						es_read_news_query_response= es.search(index=es_articles_index_name, body=es_read_news_query)
						# print("es_read_news_query_response:",es_read_news_query_response)
						if(len(es_read_news_query_response["hits"]["hits"])>0):
							es_read_news_result=es_read_news_query_response["hits"]["hits"][0]["_source"]
							if("suggs_search_field" in es_read_news_result):
								es_read_news_result.pop("suggs_search_field")

								suggs_search_field=list()
								# auto_suggs_parameters=["news_id","news_title","news_sub_title","url","english_description","description_of_news"]
								for suggs_search_news_parameter in suggs_search_news_parameters_list:
									if(suggs_search_news_parameter in article_contents):
										if(type(article_contents[suggs_search_news_parameter]) is str):
											if(len(article_contents[suggs_search_news_parameter].strip())>0):
												content=remove_stop_words(article_contents[suggs_search_news_parameter])
												suggs_search_field.append(content)
										elif(type(article_contents[suggs_search_news_parameter]) is list):
											for i in article_contents[suggs_search_news_parameter]:
												if(len(i.strip())>0):
													content=remove_stop_words(i)
													suggs_search_field.append(content)
									elif(suggs_search_news_parameter in es_read_news_result):
										if(type(es_read_news_result[suggs_search_news_parameter]) is str):
											if(len(es_read_news_result[suggs_search_news_parameter].strip())>0):
												content=remove_stop_words(es_read_news_result[suggs_search_news_parameter])
												suggs_search_field.append(content)
										elif(type(es_read_news_result[suggs_search_news_parameter]) is list):
											for i in es_read_news_result[suggs_search_news_parameter]:
												if(len(i.strip())>0):
													content=remove_stop_words(i)
													suggs_search_field.append(content)
								# es_read_news_result["suggs_search_field"]=suggs_search_field
								article_contents["suggs_search_field"]=suggs_search_field



								completion_field=list()
								for suggs in suggs_search_field:
									shingle_list=generate_shingles(suggs)
									for shingle in shingle_list:
										completion_field.append({"completion":shingle})
								article_contents["completion_field"]=completion_field

							# print("article_contents:",json.dumps(article_contents))


							for news_parameter in article_contents:
								news_parameter=news_parameter.strip().lower() 
								# if(news_parameter in news_parameters_list):
								temp_string="ctx._source."+news_parameter+"=params."+news_parameter+";"
								source_string+=temp_string
								# else:
								# 	news_parameters_not_present_list.append(news_parameter)

							# if(len(news_parameters_not_present_list)>0):
							# 	return Response(",".join(news_parameters_not_present_list)+" new news parameters found only update existing news parameters",status=500)


							
								# print("source_string:",source_string)
								

							q = {
								  "script": {
									"source": source_string,
									"params":article_contents
								  },
								  "query": {
									"match": {
										"news_id": news_id
									}
								  }
								}
							# print(json.dumps(q))
							es_update_results=es.update_by_query(body=q,index=es_articles_index_name,refresh=True)
							# print("es_update_results:",es_update_results)
							if(es_update_results["updated"]>0):
								return Response("updated article",status=200)
							else:
								error_dict={
									"error_msg":"could not update article",
									"error_code":500,
									"request_json":request.json,
									"timestamp":datetime.now()
								}
								create_error_log(partner_id,error_dict)
								return Response("could not update article",status=500)
						else:
							error_dict={
								"error_msg":"news_id not found",
								"error_code":500,
								"request_json":request.json,
								"timestamp":datetime.now()
							}
							create_error_log(partner_id,error_dict)
							return Response("news_id not found",status=500)


					else:

						return Response("es partner index not found",status=500)


				else:
					error_dict={
						"error_msg":"no data in article_contents",
						"error_code":500,
						"request_json":request.json,
						"timestamp":datetime.now()
					}
					create_error_log(partner_id,error_dict)
					return Response("no data in article_contents",status=500)


			else:
				error_dict={
					"error_msg":"article_contents not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("article_contents not found",status=500)
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

		
	

@app.route("/read_article", methods=["POST"])
def read_article():
	if(request.method=="POST"):
		try:
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)
			if("news_id" in request.json):
				news_id=int(request.json["news_id"])		

			else:
				error_dict={
					"error_msg":"news_id not found",
					"error_code":500,
					"request_json":request.json,
					"timestamp":datetime.now()
				}
				create_error_log(partner_id,error_dict)
				return Response("news_id not found",status=500)

			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):

				es_read_news_query={
						  "query": {
							"bool": {
							  "must": [
								{"match": {
								  "news_id": news_id
								}}
							  ]
							}
						  }
						}

				es_read_news_query_response= es.search(index=es_articles_index_name, body=es_read_news_query)
				# print("es_read_news_query_response:",es_read_news_query_response)
				if(len(es_read_news_query_response["hits"]["hits"])>0):
					es_read_news_result=es_read_news_query_response["hits"]["hits"][0]["_source"]
					if("suggs_search_field" in es_read_news_result):
						es_read_news_result.pop("suggs_search_field")
					if("completion_field" in es_read_news_result):
						es_read_news_result.pop("completion_field")
					return_dict={
						"article_contents":es_read_news_result
					}
					return return_dict,200
				else:
					error_dict={
						"error_msg":"no data found",
						"error_code":500,
						"request_json":request.json,
						"timestamp":datetime.now()
					}
					create_error_log(partner_id,error_dict)
					return Response("no data found",status=500)
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



@app.route("/read_articles", methods=["POST"])
def read_articles():
	if(request.method=="POST"):
		try:
		
			# print("request:",request.json)

			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			if("result_size" in request.json):
				result_size=int(request.json["result_size"])
			else:
				result_size=10
			sort_by="relv"

			if("sort_by" in request.json):
				sort_by=request.json["sort_by"].strip().lower()
				if(sort_by in ["relv","desc","asc"]):
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

			

			# if("next_page" in request.json):
			# 	from_result=request.json["next_page"]
			# elif("prev_page" in request.json):
			# 	from_result=request.json["prev_page"]
			# else:
			# 	from_result=0
			if("start_index" in request.json):
				from_result=int(request.json["start_index"])
			else:
				from_result=0

			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			if(index_exists):
				total_results,news_id_list=get_es_read_results(es_articles_index_name,sort_by,from_result,request,partner_id,result_size)

				# total_pages=total_results/10
				# print(total_pages)

				# current_page=(from_result+10)//10
				# print("current_page:",current_page)
				return_dict=dict()
				return_dict={"news_ids":news_id_list}

				# if(total_pages==0):
				# 	return_dict={"news_ids":[]}
				# elif(total_pages<=1):
				# 	return_dict={"news_ids":news_id_list}
				# else:

				# 	if(current_page==1):
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"next_page":from_result+10}
				# 	else:
				# 		if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 		else:
				# 			return_dict={"news_ids":news_id_list,"prev_page":from_result-10,"next_page":from_result+10}

				# if(current_page==1):
				# 	if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 		return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 	else:
				# 		return_dict={"news_ids":news_id_list,"next_page":from_result+10}
				# else:
				# 	if((total_pages-current_page)!=0 and (total_pages-current_page)<0):
				# 		return_dict={"news_ids":news_id_list,"prev_page":from_result-10}
				# 	else:
				# 		return_dict={"news_ids":news_id_list,"prev_page":from_result-10,"next_page":from_result+10}




				return return_dict,200





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

def remove_stop_words(sentence):
	try:
		stop_words=['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
		words = sentence.split()
		filtered_words = [word for word in words if word.lower() not in stop_words]
		return ' '.join(filtered_words)

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

def generate_3_shingles(text):
    tokens = text.lower().split()
    if(len(tokens)<3):
    	return tokens
    shingles = [tokens[i:i+3] for i in range(len(tokens) - 1)]
    return [' '.join(shingle) for shingle in shingles]

def generate_2_shingles(text):
    tokens = text.lower().split()
    if(len(tokens)<2):
    	return tokens
    shingles = [tokens[i:i+2] for i in range(len(tokens) - 1)]
    return [' '.join(shingle) for shingle in shingles]

@app.route("/create_article", methods=["POST"])
def create_article():
	if(request.method=="POST"):
		try:
			
			partner_id=None
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)
			
			# news_parameters_list=["news_id","news_title","news_sub_title","url","english_description","location","date_of_publishing","date_of_updating",
			# 			"author","author_group","editor","editor_team","byline","cover_image_caption_url","description_of_news","other_parameters",
			# 			"tags","keywords","primary_category","other_category","free_premium","news_type"]
			mandatory_news_parameters_list=["news_id","heading","url","date_created","author_id","author_name","editor_id",
											"primary_category_id","primary_category_name"]

			suggs_search_news_parameters_list=["heading","description","url","english_title","location_name","author_name","byline",
											"cover_image_url","cover_image_caption","story","associated_tags","associated_keywords","primary_category_name"]

			# print("news_parameters_list len",len(news_parameters_list))






			article_dict=dict()

			mandatory_news_parameters_not_present_list=list()
			
			for news_parameter in mandatory_news_parameters_list:
				if(news_parameter in request.json):
					if(len(str(request.json[news_parameter]))>0):
						continue
					else:
						mandatory_news_parameters_not_present_list.append(news_parameter)
				else:
					mandatory_news_parameters_not_present_list.append(news_parameter)

			if(len(mandatory_news_parameters_not_present_list)>0):
				return Response(",".join(mandatory_news_parameters_not_present_list)+" news parameters not found or value is not present",status=500)
			else:
				article_dict=request.json
			


			# print("article_dict:",article_dict)



			
			# print("article_dict:",article_dict)
			es_articles_index_name=partner_id+os.environ["ARTICLES_INDEX"]
			index_exists=es.indices.exists(index=es_articles_index_name)
			# print("index_exists:",index_exists)
			# print("e_sarticles_index_name:",es_articles_index_name)
			if(index_exists):
				if("news_id" in article_dict):
					news_id=article_dict["news_id"]
					es_read_news_query={
							  "query": {
								"bool": {
								  "must": [
									{"match": {
									  "news_id": news_id
									}}
								  ]
								}
							  }
							}

					es_read_news_query_response= es.search(index=es_articles_index_name, body=es_read_news_query)
					# print("es_read_news_query_response:",es_read_news_query_response)
					
					if(len(es_read_news_query_response["hits"]["hits"])>0):
						
						error_dict={
							"error_msg":"article with same news_id found",
							"error_code":500,
							"request_json":request.json,
							"timestamp":datetime.now()
						}
						create_error_log(partner_id,error_dict)
						return Response("article with same news_id found",status=500)
					
					else:
						suggs_search_field=list()
						
						# auto_suggs_parameters=["news_id","news_title","news_sub_title","url","english_description","description_of_news"]
						for suggs_search_news_parameter in suggs_search_news_parameters_list:
							if(suggs_search_news_parameter in article_dict):
								if(type(article_dict[suggs_search_news_parameter]) is str):
									if(len(article_dict[suggs_search_news_parameter].strip())>0):
										content=remove_stop_words(article_dict[suggs_search_news_parameter])
										suggs_search_field.append(content)
								elif(type(article_dict[suggs_search_news_parameter]) is list):
									for i in article_dict[suggs_search_news_parameter]:
										if(len(i.strip())>0):
											content=remove_stop_words(i)
											suggs_search_field.append(content)



							
						
						article_dict["suggs_search_field"]=suggs_search_field
						completion_field=list()
						shingle_list=list()
						for suggs in suggs_search_field:
							# print("\nsuggs:",suggs)
							if(suggs.strip().lower().startswith("http")):
								continue
							shingle_2_list=generate_2_shingles(suggs)
							# print("shingle_2_list:",shingle_2_list)
							shingle_3_list=generate_3_shingles(suggs)
							# print("shingle_3_list:",shingle_3_list)
							shingle_2_list.extend(shingle_3_list)
							shingle_list.extend(list(set(shingle_2_list)))
							# print("shingle_list:",shingle_list)
							for shingle in shingle_list:
								completion_field.append({"completion":shingle})
						article_dict["completion_field"]=completion_field
						
						# for suggs in suggs_search_field:


							
						
						# print("article_dict:",article_dict)
						es_result=es.index(index=es_articles_index_name,body=article_dict,id =news_id)
						
						# print("es_result:",es_result)
						if(es_result['_shards']["successful"]>0):
							return Response("article created",status=200)
						else:
							error_dict={
								"error_msg":"article not created",
								"error_code":500,
								"request_json":request.json,
								"timestamp":datetime.now()
							}
							create_error_log(partner_id,error_dict)
							return Response("article not created",status=500)
						
				else:
					error_dict={
						"error_msg":"news_id not found",
						"error_code":500,
						"request_json":request.json,
						"timestamp":datetime.now()
					}
					create_error_log(partner_id,error_dict)
					Response("news_id not found",status=500)
				

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

@app.route("/create_partner_indexes", methods=["POST"])
def create_partner_indexes():
	if(request.method=="POST"):
		try:
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			indexes_dict={
				"_articles": {
					"settings": {
						"index.mapping.ignore_malformed": True,
						"index": {
							"analysis": {
								"analyzer": {
									"trigram": {
										"type": "custom",
										"tokenizer": "standard",
										"filter": ["lowercase", "shingle"]
									}
								},
								"filter": {
									"shingle": {
										"type": "shingle",
										"min_shingle_size": 2,
										"max_shingle_size": 3
									}
								}
							}
						}
					},
					"mappings": {
						"properties": {
							"suggs_search_field": {
								"type": "keyword",
								"fields": {
									"trigram": {
										"type": "text",
										"analyzer": "trigram"
									}
								}
							},
							"completion_field": {
								"type": "nested",
								"properties": {
									"completion": {
										"type": "completion"
									}
								}
							}
						}
					}
				},
				"_search_logs": {
					"settings": {
						"index.mapping.ignore_malformed": True
					}
				},
				"_error_logs": {
					"settings": {
						"index.mapping.ignore_malformed": True
					}
				}
			}

			for index, index_body in indexes_dict.items():
				index_name=partner_id+index
				es_index_create_response=es.indices.create(index = index_name, body = index_body)
				if(es_index_create_response["acknowledged"]==True):
					continue
				else:
					for index, index_body in indexes_dict.items():
						index_name=partner_id+index
						es.indices.delete(index = index_name)
					error_dict={
								"error_msg":"could not create indexes",
								"error_code":500,
								"request_json":request.json,
								"timestamp":datetime.now()
							}
					create_error_log(partner_id,error_dict)
					return Response("could not create indexes",status=500)
					break


			return Response("created indexes",status=200)			

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

@app.route("/delete_partner_indexes", methods=["POST"])
def delete_partner_indexes():
	if(request.method=="POST"):
		try:
			if("partner_id" in request.json):
				partner_id=request.json["partner_id"]
			else:
				return Response("partner_id not found",status=500)

			indexes_list=["_articles","_search_logs","_error_logs"]
			could_not_delete_indexes_list=list()
			for index in indexes_list:
				index_name=partner_id+index
				es_index_delete_response=es.indices.delete(index = index_name)
				# print("es_index_delete_response:",es_index_create_response)
				if(es_index_delete_response["acknowledged"]==True):
					continue
				else:
					could_not_delete_indexes_list.append(index_name)
			
			if(len(could_not_delete_indexes_list)>0):
				error_dict={
							"error_msg":"could not delete indexes",
							"error_code":500,
							"request_json":request.json,
							"timestamp":datetime.now()
						}
				create_error_log(partner_id,error_dict)
				return Response("could not delete indexes "+",".join(could_not_delete_indexes_list),status=500)

			return Response("deleted indexes",status=200)				

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


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
