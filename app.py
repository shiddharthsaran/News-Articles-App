from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
from datetime import datetime
import json
from elasticsearch import helpers, Elasticsearch
app = Flask(__name__)
es_connection="http://localhost:9200"
es_news_index_name="all_news_index"
es=Elasticsearch([es_connection])

# es = Elasticsearch(
# 		cloud_id="f7098e2538d04cf3a82420cb52ed7132:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ1OGE1NTIzODJlMzU0MzNhYWFkYzQxYzI3Y2Q2MDY0OSQ1ZjFlZTEwZmQzMGU0NGYwOGYxMjYzMmNjMmFjMGU4ZQ==",
# 		http_auth=("elastic","ZYMAXeNWkqZDkVb9YB2jSQrM"),
# 		scheme="https",
#     	port=443
# 	)
def get_es_read_results(from_result,result_size=10):
	
	es_read_query={
				  "query": {
					"match_all": {
					}
				  }
				  , "from": from_result,
				  "size": 10
				}
	es_read_query_response= es.search(index=es_news_index_name, body=es_read_query)
	es_read_results=es_read_query_response["hits"]["hits"]
	total_read_results=es_read_query_response["hits"]["total"]["value"]
	# print("total_read_results:",total_read_results)
	# print("es_read_results:",es_read_results)
	results_dict={}
	for n,result in enumerate(es_read_results):
		# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
		results_dict["result_"+str(n)]=result["_source"]



	return total_read_results,results_dict

def get_es_search_results(search_keyword,from_result,sort_by,field,result_size=10):

	es_search_query={
					   
					   "query":{
						  "bool":{
							 "must":[
								{
								   "bool":{
									  "should":[
										 {
											"multi_match":{
											   "query":search_keyword,
											   "fields":[
												  field
											   ],
											   "operator":"and",
											   "fuzziness":"auto"
											}
										 }
									  ]
								   }
								}
							 ]
						  }
					   },
					   "from":from_result,
					   "size":result_size
					}

	if(sort_by=="relevance"):
		es_search_query["sort"]=[
								  {
									 "_score":{
										"order":"desc"
									 }
								  }
							   ]
	elif(sort_by=="datetime_desc"):
		es_search_query["sort"]=[
								  {
									 "news_pub_date":{
										"order":"desc"
									 }
								  }
							   ]
	elif(sort_by=="datetime_asc"):
		es_search_query["sort"]=[
								  {
									 "news_pub_date":{
										"order":"asc"
									 }
								  }
							   ]
	print("es_search_query:",es_search_query)
	es_search_query_response= es.search(index=es_news_index_name, body=es_search_query)
	print("\n")
	print("es_search_query_response:",es_search_query_response)
	es_search_took_time=es_search_query_response["took"]
	es_search_results=es_search_query_response["hits"]["hits"]
	total_search_results=es_search_query_response["hits"]["total"]["value"]
	results_dict={}
	for n,result in enumerate(es_search_results):
		# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
		results_dict["result_"+str(n)]=result["_source"]



	return total_search_results,es_search_took_time,results_dict

def get_es_adv_search_results(search_keyword,tags,from_pub_date,to_pub_date,from_result,sort_by,field,result_size=10):
	tags_should_list=list()

	for tag in tags:
		temp_dict={
			"multi_match":{
				"query":tag,
				"fields":["news_tags"],
				"operator":"and",
				"fuzziness":"auto"
			}
		}
		tags_should_list.append(temp_dict)

	es_adv_search_query={
					   
					   "query":{
						  "bool":{
							 "must":[
								{
								   "bool":{
									  "should":[
										 {
											"multi_match":{
											   "query":search_keyword,
											   "fields":[
												  field
											   ],
											   "operator":"and",
											   "fuzziness":"auto"
											}
										 }
									  ]
								   }
								},
								{
									"range":{
										"news_pub_date":{
											"gte":from_pub_date,
											"lte":to_pub_date
										}
									}
								},
								{
									"bool":{
										"should":tags_should_list
									}
								}
							 ]
						  }
					   },
					   "from":from_result,
					   "size":result_size
					}
	if(sort_by=="relevance"):
		es_adv_search_query["sort"]=[
								  {
									 "_score":{
										"order":"desc"
									 }
								  }
							   ]
	elif(sort_by=="datetime_desc"):
		es_adv_search_query["sort"]=[
								  {
									 "news_pub_date":{
										"order":"desc"
									 }
								  }
							   ]
	elif(sort_by=="datetime_asc"):
		es_adv_search_query["sort"]=[
								  {
									 "news_pub_date":{
										"order":"asc"
									 }
								  }
							   ]
	es_adv_search_query_response= es.search(index=es_news_index_name, body=es_adv_search_query)
	es_adv_search_took_time=es_adv_search_query_response["took"]
	es_adv_search_results=es_adv_search_query_response["hits"]["hits"]
	total_search_results=es_adv_search_query_response["hits"]["total"]["value"]
	results_dict={}
	for n,result in enumerate(es_adv_search_results):
		# result["_source"]["article_timestamp"]=datetime.fromtimestamp(int(result["_source"]["article_timestamp"])/1000)
		results_dict["result_"+str(n)]=result["_source"]



	return total_search_results,es_adv_search_took_time,results_dict


@app.route("/adv_search",methods=["GET","POST"])
def adv_search():
	if(request.method=="GET"):
		return render_template("adv_search.html")
	elif(request.method=="POST"):
		# print(request.form)
		from_title_result=0
		from_author_result=0
		closest_match_change=0
		closest_match=""
		search_keyword=request.form['search_keyword']
		if("closest_match" in request.form):
			if(len(request.form["closest_match"].lower().strip())>0 and request.form["closest_match"].lower().strip()!=search_keyword):
				closest_match_change=1
				closest_match=request.form["closest_match"]
				search_keyword=request.form["closest_match"]
		tags=[tag.strip() for tag in request.form['tags'].split(",")]
		from_pub_date=request.form["from_pub_date"]
		to_pub_date=request.form["to_pub_date"]
		# print("search_keyword:",search_keyword)
		# print("tags:",tags)
		# print("from_pub_date:",from_pub_date)
		# print("to_pub_date:",to_pub_date)

		# print("request.form:",request.form)
		if("next_page_title" in request.form):
			from_title_result=int(request.form["next_page_title"])+10
		elif("prev_page_title" in request.form):
			from_title_result=int(request.form["prev_page_title"])-10

		if("next_page_author" in request.form):
			from_author_result=int(request.form["next_page_author"])+10
		elif("prev_page_author" in request.form):
			from_author_result=int(request.form["prev_page_author"])-10
		sort_by="relevance"
		if("sort_by" in request.form):
			sort_by=request.form["sort_by"]

		title_total_search_results,es_title_search_took_time,title_results_dict=get_es_adv_search_results(search_keyword,tags,from_pub_date,to_pub_date,from_title_result,sort_by,"news_title.trigram")
		author_total_search_results,es_author_search_took_time,author_results_dict=get_es_adv_search_results(search_keyword,tags,from_pub_date,to_pub_date,from_author_result,sort_by,"news_author.trigram")
		# total_search_results,es_search_took_time,results_dict=get_es_adv_search_results(search_keyword,tags,from_pub_date,to_pub_date,from_result,sort_by)

		# print("results_dict:",results_dict)

		return render_template("adv_search_results.html",closest_match_change=closest_match_change,closest_match=closest_match,user_search=request.form["search_keyword"],sort_by=sort_by,to_pub_date=to_pub_date,from_pub_date=from_pub_date,tags=",".join(tags),search_keyword=search_keyword,
			len_author_results_dict=len(author_results_dict),author_total_search_results=author_total_search_results,es_author_search_took_time=es_author_search_took_time,author_results_dict=author_results_dict,from_author_result=from_author_result,
			len_title_results_dict=len(title_results_dict),title_total_search_results=title_total_search_results,es_title_search_took_time=es_title_search_took_time,title_results_dict=title_results_dict,from_title_result=from_title_result)

@app.route("/auto_suggs")
def auto_suggs():
	search_keyword = request.args["q"].lower().strip()
	# tokens = query.split(" ")

	# print("query:",query)
	# print("tokens:",tokens)

	es_auto_suggs_query={
	  "suggest": {
		"news_title_phrase_suggester": {
		  "text": search_keyword,
		  "phrase":{
			"field":"news_title.trigram",
			"highlight":{
			  "pre_tag":"<em>",
			  "post_tag":"</em>"
			},
			"confidence":0,
			"max_errors":3
		  }
		},
		"news_author_phrase_suggester": {
		  "text": search_keyword,
		  "phrase":{
			"field":"news_author.trigram",
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
	resp = es.search(index=es_news_index_name, body=es_auto_suggs_query)
	# print("resp:",resp)
	all_suggestions=list()
	news_title_suggestions=list()
	news_author_suggestions=list()

	for suggestion_list in resp["suggest"]["news_title_phrase_suggester"]:
		for options in suggestion_list["options"]:
			news_title_suggestions.append(options["text"]+"_"+str(eval(str(options["score"]))))

	# print("news_title_suggestions:",news_title_suggestions)

	for suggestion_list in resp["suggest"]["news_author_phrase_suggester"]:
		for options in suggestion_list["options"]:
			news_author_suggestions.append(options["text"]+"_"+str(eval(str(options["score"]))))

	# print("news_author_suggestions:",news_author_suggestions)
	# print("scores:",scores)
	# scores=sorted(scores)
	# print("scores:",scores)
	# scores.reverse()
	# print("scores:",scores)
	temp=news_author_suggestions+news_title_suggestions
	# print("temp:",temp)
	temp = sorted(temp, key=lambda k: float(k.split("_")[-1]),reverse=True)
	# temp.reverse()

	# print("temp:",temp)

	temp=[x.split("_")[0] for x in temp]
	for x in temp:
		if(x in all_suggestions):
			continue
		else:
			all_suggestions.append(x)
	# [all_suggestions.append(x)  if x not in all_suggestions]

	# print("all_suggestions:",all_suggestions)


	return all_suggestions
	# print("resp:",resp)
	# return [result['_source']['news_title'] for result in resp['hits']['hits']]
	# total_search_results,es_search_took_time,results_dict=get_es_search_results(search_keyword,from_result)

# @app.route("/auto_suggs")
# def auto_suggs():
# 	search_keyword = request.args["q"].lower()
# 	# tokens = query.split(" ")

# 	# print("query:",query)
# 	# print("tokens:",tokens)

# 	es_auto_suggs_query={
# 					   "sort":[
# 						  {
# 							 "_score":{
# 								"order":"desc"
# 							 }
# 						  }
# 					   ],
# 					   "query":{
# 						  "bool":{
# 							 "must":[
# 								{
# 								   "bool":{
# 									  "should":[
# 										 {
# 											"multi_match":{
# 											   "query":search_keyword,
# 											   "fields":[
# 												  "news_title.trigram",
# 												  "news_author.trigram"
# 											   ],
# 											   "operator":"and",
# 											   "fuzziness":"auto"
# 											}
# 										 }
# 									  ]
# 								   }
# 								}
# 							 ]
# 						  }
# 					   },
# 					   "from":0,
# 					   "size":5
# 					}
# 	resp = es.search(index=es_news_index_name, body=es_auto_suggs_query)
# 	return [result['_source']['news_title'] for result in resp['hits']['hits']]
# 	# total_search_results,es_search_took_time,results_dict=get_es_search_results(search_keyword,from_result)



@app.route("/tags_auto_suggs")
def tags_auto_suggs():
	tags = request.args["q"].lower()
	# print("tags:",tags)
	search_tag=tags.split(",")[-1]
	# print("search_tag:",search_tag)
	# tokens = query.split(" ")

	# print("query:",query)
	# print("tokens:",tokens)

	es_auto_suggs_query={
					   "sort":[
						  {
							 "_score":{
								"order":"desc"
							 }
						  }
					   ],
					   "query":{
						  "bool":{
							 "must":[
								{
								   "bool":{
									  "should":[
										 {
											"multi_match":{
											   "query":search_tag,
											   "fields":[
												  "tag_name"
											   ],
											   "operator":"and",
											   "fuzziness":"auto"
											}
										 }
									  ]
								   }
								}
							 ]
						  }
					   },
					   "from":0,
					   "size":5
					}
	resp = es.search(index="tags_index", body=es_auto_suggs_query)
	return [result['_source']['tag_name'] for result in resp['hits']['hits']]

@app.route("/search",methods=["GET","POST"])
def search_news():
	if(request.method=="GET"):
		return render_template("search.html")
	elif(request.method=="POST"):
		search_keyword=request.form['search'].lower().strip()
		# print("search_keyword:",search_keyword)
		from_title_result=0
		from_author_result=0
		closest_match_change=0
		closest_match=""
		
		# print("request.form:",request.form)
		if("closest_match" in request.form):
			if(len(request.form["closest_match"].lower().strip())>0 and request.form["closest_match"].lower().strip()!=search_keyword):
				closest_match_change=1
				closest_match=request.form["closest_match"]
				search_keyword=request.form["closest_match"]
		if("next_page_title" in request.form):
			from_title_result=int(request.form["next_page_title"])+10
		elif("prev_page_title" in request.form):
			from_title_result=int(request.form["prev_page_title"])-10

		if("next_page_author" in request.form):
			from_author_result=int(request.form["next_page_author"])+10
		elif("prev_page_author" in request.form):
			from_author_result=int(request.form["prev_page_author"])-10
		sort_by="relevance"
		if("sort_by" in request.form):
			sort_by=request.form["sort_by"]
		title_total_search_results,es_title_search_took_time,title_results_dict=get_es_search_results(search_keyword,from_title_result,sort_by,"news_title.trigram")
		author_total_search_results,es_author_search_took_time,author_results_dict=get_es_search_results(search_keyword,from_author_result,sort_by,"news_author.trigram")
		# print("results_dict:",results_dict)
		# print("title_results_dict:",title_results_dict)
		# print("author_results_dict:",author_results_dict)
		return render_template("search_results.html",closest_match_change=closest_match_change,closest_match=closest_match,user_search=request.form["search"],sort_by=sort_by,
			len_author_results_dict=len(author_results_dict),author_total_search_results=author_total_search_results,es_author_search_took_time=es_author_search_took_time,author_results_dict=author_results_dict,from_author_result=from_author_result,
			len_title_results_dict=len(title_results_dict),title_total_search_results=title_total_search_results,es_title_search_took_time=es_title_search_took_time,title_results_dict=title_results_dict,from_title_result=from_title_result)


		

@app.route("/update_news/<news_id>",methods=["GET","POST"])
def update_news(news_id):
	if(request.method=="GET"):
		# print("request.method:",request.method)
		# print("news_id:",news_id)
		news_id=int(news_id)
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
		es_read_news_query_response= es.search(index=es_news_index_name, body=es_read_news_query)
		es_read_news_result=es_read_news_query_response["hits"]["hits"][0]
		# print(es_read_news_result)
		es_news_doc_id=es_read_news_result["_id"]
		news_id=es_read_news_result["_source"]["news_id"]
		news_title=es_read_news_result["_source"]["news_title"]
		news_pub_date=es_read_news_result["_source"]["news_pub_date"]
		format = '%Y-%m-%dT%H:%M:%S'
		news_pub_date=datetime.strptime(news_pub_date,format)
		news_tags=es_read_news_result["_source"]["news_tags"]
		news_tags=",".join(news_tags)
		news_story_description=es_read_news_result["_source"]["news_story_description"]
		news_author=es_read_news_result["_source"]["news_author"]
		return render_template("update_news.html",es_news_doc_id=es_news_doc_id,news_author=news_author,news_id=news_id,news_title=news_title,news_story_description=news_story_description,news_tags=news_tags,news_pub_date=news_pub_date)
	elif(request.method=="POST"):
		# news_id=None
		# print("request.method:",request.method)
		news_title=None
		news_pub_date=None
		news_tags=None
		news_tags_list=list()
		news_story_description=None
		es_news_doc_id=None
		news_author=None
		if("id" in request.form):
			updated_news_id=int(request.form['id'])
		if("title" in request.form):
			news_title=request.form['title']
		if("story" in request.form):
			news_story_description=request.form['story']
		if("author" in request.form):
			news_author=request.form['author']
		if("tags" in request.form):
			news_tags=request.form['tags']
			news_tags_list=[x.strip() for x in news_tags.split(",")]
		if("datetime" in request.form):
			news_pub_date=request.form['datetime']
			# 2023-01-31T07:06
			format = '%Y-%m-%dT%H:%M:%S'
			news_pub_date=datetime.strptime(news_pub_date,format)
		if("es_news_doc_id" in request.form):
			es_news_doc_id=request.form["es_news_doc_id"]
		# print("es_news_doc_id:",es_news_doc_id)

		article_dict=dict()
		article_dict["news_id"]=updated_news_id
		article_dict["news_title"]=news_title
		article_dict["news_author"]=news_author
		article_dict["news_tags"]=news_tags_list
		article_dict["news_pub_date"]=news_pub_date
		article_dict["news_story_description"]=news_story_description
		# print("article_dict:",article_dict)
		# es_update_news_query={
		# 		  "query": {
		# 		    "bool": {
		# 		      "must": [
		# 		        {"match": {
		# 		          "news_id": news_id
		# 		        }}
		# 		      ]
		# 		    }
		# 		  }
		# 		}

		es_update_news_query_response= es.index(index=es_news_index_name,id=es_news_doc_id, body=article_dict,refresh=True)
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
		es_read_news_query_response= es.search(index=es_news_index_name, body=es_read_news_query)
		es_read_news_result=es_read_news_query_response["hits"]["hits"][0]
		# print(es_read_news_result)
		news_id=es_read_news_result["_source"]["news_id"]
		news_title=es_read_news_result["_source"]["news_title"]
		news_pub_date=es_read_news_result["_source"]["news_pub_date"]
		format = '%Y-%m-%dT%H:%M:%S'
		news_pub_date=datetime.strptime(news_pub_date,format)
		news_tags=es_read_news_result["_source"]["news_tags"]
		news_story_description=es_read_news_result["_source"]["news_story_description"]
		news_author=es_read_news_result["_source"]["news_author"]

		# print("news_id:",news_id)
		# print(type(news_id))
		# print("news_title:",news_title)
		# print("news_story_description:",news_story_description)
		# print("news_tags:",news_tags)
		# print("news_pub_date:",news_pub_date)
		# print("news_pub_date:",type(news_pub_date))

		return render_template("read_news.html",news_author=news_author,news_id=news_id,news_title=news_title,news_story_description=news_story_description,news_tags=news_tags,news_pub_date=news_pub_date)



@app.route("/read_news/<news_id>", methods=["GET","POST"])
def read_news(news_id):
	if(request.method=="GET"):
		news_id=int(news_id)
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
		es_read_news_query_response= es.search(index=es_news_index_name, body=es_read_news_query)
		es_read_news_result=es_read_news_query_response["hits"]["hits"][0]
		# print(es_read_news_result)
		news_id=es_read_news_result["_source"]["news_id"]
		news_title=es_read_news_result["_source"]["news_title"]
		news_pub_date=es_read_news_result["_source"]["news_pub_date"]
		format = '%Y-%m-%dT%H:%M:%S'
		news_pub_date=datetime.strptime(news_pub_date,format)
		news_tags=es_read_news_result["_source"]["news_tags"]
		news_story_description=es_read_news_result["_source"]["news_story_description"]
		news_author=es_read_news_result["_source"]["news_author"]

		# print("news_id:",news_id)
		# print(type(news_id))
		# print("news_title:",news_title)
		# print("news_story_description:",news_story_description)
		# print("news_tags:",news_tags)
		# print("news_pub_date:",news_pub_date)
		# print("news_pub_date:",type(news_pub_date))

		return render_template("read_news.html",news_author=news_author,news_id=news_id,news_title=news_title,news_story_description=news_story_description,news_tags=news_tags,news_pub_date=news_pub_date)
	elif(request.method=="POST"):
		if("update" in request.form):
			print("")
		elif("delete" in request.form):
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
			es_delete_news_query_response= es.delete_by_query(index=es_news_index_name, body=es_news_delete_query,refresh=True)
			# print("es_delete_news_query_response:",es_delete_news_query_response)
			from_result=0
			# if("next_page" in request.form):
			# 	from_result=int(request.form["next_page"])+10
			# elif("prev_page" in request.form):
			# 	from_result=int(request.form["prev_page"])-10
			total_results,results_dict=get_es_read_results(from_result)
			# print("results_dict:",results_dict)
			return render_template("read.html",len_results_dict=len(results_dict),total_results=total_results,results_dict=results_dict,from_result=from_result)


@app.route("/read", methods=["GET","POST"])
def read():
	if(request.method=="GET"):
		from_result=0
		if("next_page" in request.form):
			from_result=int(request.form["next_page"])+10
		elif("prev_page" in request.form):
			from_result=int(request.form["prev_page"])-10
		total_results,results_dict=get_es_read_results(from_result)
		return render_template("read.html",len_results_dict=len(results_dict),total_results=total_results,results_dict=results_dict,from_result=from_result)
	elif(request.method=="POST"):
		from_result=0
		# print("request.form:",request.form)
		if("next_page" in request.form):
			from_result=int(request.form["next_page"])+10
		elif("prev_page" in request.form):
			from_result=int(request.form["prev_page"])-10
		# print("from_result:",from_result)
		total_results,results_dict=get_es_read_results(from_result)
		return render_template("read.html",len_results_dict=len(results_dict),total_results=total_results,results_dict=results_dict,from_result=from_result)



@app.route("/create", methods=["GET","POST"])
def create():
	if(request.method=="GET"):
		return render_template("create.html")
	elif(request.method=="POST"):
		news_id=None
		news_title=None
		news_pub_date=None
		news_tags=None
		news_tags_list=list()
		news_story_description=None
		news_author=None
		if("id" in request.form):
			news_id=int(request.form['id'])
		if("title" in request.form):
			news_title=request.form['title']
		if("story" in request.form):
			news_story_description=request.form['story']
		if("author" in request.form):
			news_author=request.form['author']
		if("tags" in request.form):
			news_tags=request.form['tags']
			news_tags_list=[x.strip() for x in news_tags.split(",")]
		if("datetime" in request.form):
			news_pub_date=request.form['datetime']
			# 2023-01-31T07:06
			format = '%Y-%m-%dT%H:%M:%S'
			news_pub_date=datetime.strptime(news_pub_date,format)
		# print("news_id:",news_id)
		# print(type(news_id))
		# print("news_title:",news_title)
		# print("news_story_description:",news_story_description)
		# print("news_tags:",news_tags)
		# print("news_tags_list:",news_tags_list)
		# print("news_pub_date:",news_pub_date)
		# print("news_pub_date:",type(news_pub_date))

		article_dict=dict()
		article_dict["news_id"]=news_id
		article_dict["news_title"]=news_title
		article_dict["news_author"]=news_author
		article_dict["news_tags"]=news_tags_list
		article_dict["news_pub_date"]=news_pub_date
		article_dict["news_story_description"]=news_story_description

		
		es_result=es.index(index=es_news_index_name,body=article_dict)
		if(es_result['_shards']["successful"]>0):
			return render_template("home.html")




@app.route("/", methods=["GET"])
def home():
	if(request.method=="GET"):
		return render_template("home.html")

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)