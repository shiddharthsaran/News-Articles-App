
# Create Article Endpoint

This code defines a Flask endpoint that handles the creation of articles.

## Endpoint URL
`/create_article`

## Request Method
`POST`

## Request Body
The following parameters are mandatory news parameters:
- `partner_id` (string, required): The ID of the partner.
- `news_id` (integer, required): The ID of the news article.
- `heading` (string, required): The heading/title of the news article.
- `url` (string, required): The URL of the news article.
- `date_created` (date, required): The date when the article was created Format: "YYYY-MM-DDTHH:MM:SS".
- `author_id` (integer, required): The ID of the author of the article.
- `author_name` (string, required): The name of the author of the article.
- `editor_id` (integer, required): The ID of the editor of the article.
- `primary_category_id` (integer, required): The ID of the primary category of the article.
- `primary_category_name` (string, required): The name of the primary category of the article.

The following optional parameters are used for generating suggestion search fields:

- `heading` (string): The heading/title of the news article.
- `description` (string): The description of the news article.
- `url` (string): The URL of the news article.
- `english_title` (string): The English title of the news article.
- `location_name` (string): The name of the location mentioned in the news article.
- `author_name` (string): The name of the author of the news article.
- `byline` (string): The byline of the news article.
- `cover_image_url` (string): The URL of the cover image associated with the news article.
- `cover_image_caption` (string): The caption of the cover image associated with the news article.
- `story` (string): The main story/content of the news article.
- `associated_tags` (list): An list of associated tags related to the news article.
- `associated_keywords` (list): An list of associated keywords related to the news article.
- `primary_category_name` (string): The name of the primary category of the news article.

## Response Codes
- `200 OK`: The article was created successfully.
- `500 Internal Server Error`: An error occurred during the article creation process. The response body may contain an error message.

## Error Logging
In case of any error during the article creation process, an error log is generated. The error log includes the following details:

- `error_msg` (string): The error message describing the encountered error.
- `error_code` (integer): The error code associated with the error.
- `request_json` (object): The JSON data received in the request that caused the error.
- `timestamp` (string): The timestamp indicating when the error occurred.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/create_article` endpoint. It performs the following steps:

1. Checks if the request method is `POST`.
2. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
3. Checks for the presence of mandatory news parameters in the JSON data. If any of the parameters are missing or have an empty value, it returns a response with an error message (`<parameter_name> not found` or `<parameter_name> news parameters not found or value is not present`).
4. If all the mandatory news parameters are present, the code assigns the JSON data to the `article_dict` variable.
5. Constructs the Elasticsearch index name based on the `partner_id` and a constant value.
6. Checks if the Elasticsearch index exists.
7. If the index exists:
   - Checks if an article with the same `news_id` already exists in the index. If so, it returns a response with an error message (`article with same news_id found`).
   - Generates a list of suggestions search fields based on various news parameters, including `heading`, `description`, `url`, `english_title`, `location_name`, `author_name`, `byline`, `cover_image_url`, `cover_image_caption`, `story`, `associated_tags`, `associated_keywords`, and `primary_category_name`.
   - Adds the `suggs_search_field` to the `article_dict` to be indexed in Elasticsearch.
   - Generates completion fields and adds them to the `article_dict`.
   - Indexes the `article_dict` in Elasticsearch with the `news_id` as the document ID.
   - If the indexing is successful, it returns a response with a message (`article created`).
   - If the indexing fails, it returns a response with an error message (`article not created`).
8. If the Elasticsearch index does not exist, it returns a response with an error message (`es partner index not found`).
9. If any exception occurs during the process, it catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.



# Create Partner Indexes Endpoint

This code defines a Flask endpoint that handles the creation of partner indexes.

## Endpoint URL
`/create_partner_indexes`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameter:

- `partner_id` (string, required): The ID of the partner.

## Response Codes
- `200 OK`: The indexes were created successfully.
- `500 Internal Server Error`: An error occurred during the index creation process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/create_partner_indexes` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Defines the index mappings and settings in the `indexes_dict` variable. This dictionary contains mappings for `_articles`, `_search_logs`, and `_error_logs` indexes.
3. Iterates through the `indexes_dict` and creates the partner-specific indexes using the Elasticsearch Python client's `indices.create` method.
4. If the index creation is successful, it adds the index name to the `indexes_created` array.
5. If the index creation fails, it deletes any previously created indexes and updates the respective boolean values (`error_logs_created` or `search_logs_created`) accordingly.
6. After completing the index creation process, it constructs the response body JSON object with the appropriate fields (`message`, `indexes_created`, `error_logs_created`, `search_logs_created`).
7. Returns the response body JSON object as the response with a status code of `200` (OK) if all indexes were created successfully. If there were any errors during the process, it returns a response with a status code of `500` (Internal Server Error).

# Delete Partner Indexes Endpoint

This code defines a Flask endpoint that handles the deletion of partner indexes.

## Endpoint URL
`/delete_partner_indexes`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameter:

- `partner_id` (string, required): The ID of the partner.

## Response Codes
- `200 OK`: The indexes were deleted successfully.
- `500 Internal Server Error`: An error occurred during the index deletion process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/delete_partner_indexes` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Defines a list of index names to be deleted (`_articles`, `_search_logs`, `_error_logs`).
3. Iterates through the index list and deletes the partner-specific indexes using the Elasticsearch Python client's `indices.delete` method.
4. If the index deletion is successful, it continues to the next index.
5. If the index deletion fails, it adds the index name to the `could_not_delete_indexes_list`.
6. After completing the index deletion process, it checks if there are any indexes that could not be deleted. If so, it returns a response with an error message (`could not delete indexes`) along with the names of the indexes that could not be deleted.
7. If all indexes are deleted successfully, it returns a response with a message (`deleted indexes`).
8. If any exception occurs during the process, it catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.
# Read Articles Endpoint

This code defines a Flask endpoint that handles the retrieval of articles.

## Endpoint URL
`/read_articles`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `result_size` (integer, optional): The number of articles to retrieve per request. Default is 10.
- `sort_by` (string, optional): The sorting criteria for the articles. Possible values are "relv" (relevance), "desc" (date created - descending order), or "asc" (date created - ascending order). Default is "relv".
- `start_index` (integer, optional): The starting index for retrieving articles. Default is 0.

## Response Codes
- `200 OK`: The articles were retrieved successfully.
- `500 Internal Server Error`: An error occurred during the article retrieval process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following field:

- `news_ids` (array): An array containing the IDs of the retrieved articles.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/read_articles` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Sets the `result_size`, `sort_by`, and `start_index` variables based on the request JSON data. If these parameters are not provided, default values are used.
3. Calls the `get_es_read_results` function to retrieve the total number of results and the list of news IDs from Elasticsearch.
4. Constructs the response JSON object with the retrieved news IDs.
5. Returns the response JSON object as the response with a status code of `200` (OK) if the articles were retrieved successfully. If there were any errors during the process, it returns a response with a status code of `500` (Internal Server Error).
# Read Article Endpoint

This code defines a Flask endpoint that handles the retrieval of a specific article.

## Endpoint URL
`/read_article`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `news_id` (integer, required): The ID of the article to retrieve.

## Response Codes
- `200 OK`: The article was retrieved successfully.
- `500 Internal Server Error`: An error occurred during the article retrieval process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following field:

- `article_contents` (object): An object containing the contents of the retrieved article.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/read_article` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `news_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`news_id not found`).
3. Constructs the Elasticsearch query to retrieve the specific article based on the provided `news_id`.
4. Executes the Elasticsearch query using the Elasticsearch Python client's `search` method and retrieves the relevant article.
5. Constructs the response JSON object with the retrieved article contents.
6. Returns the response JSON object as the response with a status code of `200` (OK) if the article was retrieved successfully. If the article is not found, it returns a response with a status code of `500` (Internal Server Error) and an error message (`no data found`).
7. If any exception occurs during the process, it catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.
# Update Article Endpoint

This code defines a Flask endpoint that handles the update of a specific article.

## Endpoint URL
`/update_article`

## Request Method
`PUT`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `news_id` (integer, required): The ID of the article to update.
- `article_contents` (object, required): An object containing the updated contents of the article.

## Response Codes
- `200 OK`: The article was updated successfully.
- `500 Internal Server Error`: An error occurred during the article update process. The response body may contain an error message.
# Code Overview

The code follows the Flask framework's routing approach to handle the `/update_article` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `news_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`news_id not found`).
3. Attempts to extract the `article_contents` from the JSON data in the request. If it is not found or empty, it returns a response with an error message (`article_contents not found` or `no data in article_contents`).
4. Constructs the Elasticsearch query to retrieve the specific article based on the provided `news_id`.
5. Executes the Elasticsearch query using the Elasticsearch Python client's `search` method and retrieves the relevant article.
6. Removes the `suggs_search_field` and `completion_field` keys from the retrieved article.
7. Updates the retrieved article with the new contents provided in the `article_contents` object.
8. Constructs the Elasticsearch update query using the updated article contents.
9. Executes the Elasticsearch update query using the Elasticsearch Python client's `update_by_query` method to update the article.
10. Checks the update results to verify if the article was successfully updated.
11. Returns a response with a status code of `200` (OK) and a success message if the article was updated successfully. If the article is not found or an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.
# Delete Article Endpoint

This code defines a Flask endpoint that handles the deletion of a specific article.

## Endpoint URL
`/delete_article`

## Request Method
`DELETE`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `news_id` (integer, required): The ID of the article to delete.

## Response Codes
- `200 OK`: The article was deleted successfully.
- `500 Internal Server Error`: An error occurred during the article deletion process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/delete_article` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `news_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`news_id not found`).
3. Constructs the Elasticsearch query to delete the specific article based on the provided `news_id`.
4. Executes the Elasticsearch delete query using the Elasticsearch Python client's `delete_by_query` method to delete the article.
5. Checks the delete results to verify if the article was successfully deleted.
6. Returns a response with a status code of `200` (OK) and a success message if the article was deleted successfully. If the article is not found or an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.

# Articles Auto Suggestions Endpoint

This code defines a Flask endpoint that provides auto-suggestions for articles based on a given phrase.

## Endpoint URL
`/articles_auto_suggs`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `phrase` (string, required): The phrase for which auto-suggestions are requested.

## Response Codes
- `200 OK`: The auto-suggestions were generated successfully.
- `500 Internal Server Error`: An error occurred during the auto-suggestion generation process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following parameter:

- `suggestions` (list): A list of auto-suggestions generated based on the provided phrase.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/articles_auto_suggs` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `phrase` from the JSON data in the request. If it is not found, it returns a response with an error message (`phrase not found`).
3. Constructs the Elasticsearch query to generate auto-suggestions based on the provided `phrase`.
4. Executes the Elasticsearch search query using the Elasticsearch Python client's `search` method.
5. Retrieves the auto-suggestions from the Elasticsearch response.
6. Constructs a response JSON object containing the auto-suggestions.
7. Returns a response with a status code of `200` (OK) and the auto-suggestions if they were generated successfully. If an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.
# Articles Completion Suggestions Endpoint

This code defines a Flask endpoint that provides completion suggestions for articles based on a given prefix phrase.

## Endpoint URL
`/articles_completion_suggs`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `phrase` (string, required): The prefix phrase for which completion suggestions are requested.

## Response Codes
- `200 OK`: The completion suggestions were generated successfully.
- `500 Internal Server Error`: An error occurred during the completion suggestion generation process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following parameter:

- `suggestions` (list): A list of completion suggestions generated based on the provided prefix phrase.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/articles_completion_suggs` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `phrase` from the JSON data in the request. If it is not found, it returns a response with an error message (`phrase not found`).
3. Constructs the Elasticsearch query to generate completion suggestions based on the provided prefix `phrase`.
4. Executes the Elasticsearch search query using the Elasticsearch Python client's `search` method.
5. Retrieves the completion suggestions from the Elasticsearch response.
6. Constructs a response JSON object containing the completion suggestions.
7. Returns a response with a status code of `200` (OK) and the completion suggestions if they were generated successfully. If an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.
# Search Articles Endpoint

This code defines a Flask endpoint that performs a search for articles based on a given phrase.

## Endpoint URL
`/search_articles`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `phrase` (string, required): The phrase to search for in the articles.
- `result_size` (integer, optional): The maximum number of search results to return (default: 10).
- `sort_by` (string, optional): The sorting criteria for the search results. Valid values are "relv" (relevance), "desc" (descending), or "asc" (ascending) (default: "relv").
- `start_index` (integer, optional): The starting index of the search results (default: 0).

## Response Codes
- `200 OK`: The search results were generated successfully.
- `500 Internal Server Error`: An error occurred during the search process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following parameters:

- `results` (dictionary): A dictionary containing the search results.
  - `news_ids` (list): A list of news IDs matching the search criteria.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/search_articles` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `phrase` from the JSON data in the request. If it is not found, it returns a response with an error message (`phrase not found`).
3. Extracts the optional parameters (`result_size`, `sort_by`, `start_index`) from the JSON data in the request. If any of the parameters are not found, default values are used.
4. Constructs the Elasticsearch query to search for articles based on the provided `phrase`, `result_size`, `sort_by`, and `start_index`.
5. Executes the Elasticsearch search query using the Elasticsearch Python client's `search` method.
6. Retrieves the search results (news IDs) from the Elasticsearch response.
7. Constructs a response JSON object containing the search results.
8. Returns a response with a status code of `200` (OK) and the search results if they were generated successfully. If an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.
# Advanced Search Articles Endpoint

This code defines a Flask endpoint that performs an advanced search for articles based on various criteria.

## Endpoint URL
`/adv_search_articles`

## Request Method
`POST`

## Request Body
The request body should contain a JSON object with the following parameters:

- `partner_id` (string, required): The ID of the partner.
- `phrase` (string, required): The phrase to search for in the articles.
- `from_pub_date` (string, optional): The starting publication date for the search results. Format: "YYYY-MM-DD".
- `to_pub_date` (string, optional): The ending publication date for the search results. Format: "YYYY-MM-DD".
- `author_name` (string, optional): The name of the author to filter the search results.
- `category_name` (string, optional): The name of the category to filter the search results.
- `topic` (string, optional): The topic to filter the search results.
- `location` (string, optional): The location to filter the search results.
- `result_size` (integer, optional): The maximum number of search results to return (default: 10).
- `sort_by` (string, optional): The sorting criteria for the search results. Valid values are "relv" (relevance), "desc" (descending), or "asc" (ascending) (default: "relv").
- `start_index` (integer, optional): The starting index of the search results (default: 0).
- `author_ids` (list, optional): A list of author IDs to filter the search results.
- `category_ids` (list, optional): A list of category IDs to filter the search results.
- `news_type` (string, optional): The type of news to filter the search results.
- `location_ids` (list, optional): A list of location IDs to filter the search results.

## Response Codes
- `200 OK`: The search results were generated successfully.
- `500 Internal Server Error`: An error occurred during the search process. The response body may contain an error message.

## Response Body
The response body will contain a JSON object with the following parameters:

- `results` (dict): A dictionary containing the search results.
  - `news_ids` (list): A list of news IDs matching the search criteria.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/adv_search_articles` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Attempts to extract the `phrase` from the JSON data in the request. If it is not found, it returns a response with an error message (`phrase not found`).
3. Extracts the optional parameters (`from_pub_date`, `to_pub_date`, `author_name`, `category_name`, `topic`, `location`, `result_size`, `sort_by`, `start_index`, `author_ids`, `category_ids`, `news_type`, `location_ids`) from the JSON data in the request. If any of the parameters are not found, default values are used.
4. Constructs the Elasticsearch query to perform an advanced search based on the provided criteria.
5. Executes the Elasticsearch search query using the Elasticsearch Python client's `search` method.
6. Retrieves the search results (news IDs) from the Elasticsearch response.
7. Constructs a response JSON object containing the search results.
8. Returns a response with a status code of `200` (OK) and the search results if they were generated successfully. If an error occurs, it returns a response with a status code of `500` (Internal Server Error) and an error message.
# Searches by Volume Endpoint

This code defines a Flask endpoint that handles searching logs by volume.

## Endpoint URL
`/searches_by_volume`

## Request Method
`POST`

## Request Body
The following parameters are required:
- `partner_id` (string, required): The ID of the partner.
- `result_size` (integer, optional): The number of results to return (default: 10).
- `sort_by` (string, optional): The sorting order for the search results. Valid values are "desc" (descending) and "asc" (ascending) (default: "desc").
- `from_timestamp` (string, optional): The starting timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `to_timestamp` (string, optional): The ending timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `search_type` (string, optional): The type of search to filter the logs by.

## Response
The response will be a list of objects containing the search terms and their corresponding volume:

## Response Codes
- `200 OK`: The search logs by volume were retrieved successfully.
- `500 Internal Server Error`: An error occurred during the search process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/searches_by_volume` endpoint. It performs the following steps:

1. Checks if the request method is `POST`.
2. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
3. Parses the optional parameters from the JSON data: `result_size`, `sort_by`, `from_timestamp`, `to_timestamp`, and `search_type`.
4. Constructs the Elasticsearch index name based on the `partner_id` and a constant value.
5. Checks if the Elasticsearch index exists.
6. Constructs the Elasticsearch query to retrieve the most searched terms by volume.
7. Applies optional filters based on the provided parameters: `from_timestamp`, `to_timestamp`, and `search_type`.
8. Executes the Elasticsearch search and retrieves the search results.
9. Returns the search results in the response.

# Most Search Results Endpoint

This code defines a Flask endpoint that retrieves the most search results.

## Endpoint URL
`/most_search_results`

## Request Method
`POST`

## Request Body
The following parameters are required:
- `partner_id` (string, required): The ID of the partner.
- `result_size` (integer, optional): The number of results to return (default: 10).
- `from_index` (integer, optional): The starting index for the results (default: 0).
- `from_timestamp` (string, optional): The starting timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `to_timestamp` (string, optional): The ending timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `search_type` (string, optional): The type of search to filter the logs by.

## Response
The response will be a list of objects containing the most search results.

## Response Codes
- `200 OK`: The most search results were retrieved successfully.
- `500 Internal Server Error`: An error occurred during the search process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/most_search_results` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Parses the optional parameters from the JSON data: `result_size`, `from_index`, `from_timestamp`, `to_timestamp`, and `search_type`.
3. Constructs the Elasticsearch index name based on the `partner_id` and a constant value.
4. Checks if the Elasticsearch index exists.
5. Constructs the Elasticsearch query to retrieve the most search results.
6. Applies optional filters based on the provided parameters: `from_timestamp`, `to_timestamp`, and `search_type`.
7. Executes the Elasticsearch search and retrieves the search results.
8. Processes the search results and returns them in the response.
  

# Search Types Count Endpoint

This code defines a Flask endpoint that retrieves the count of search types.

## Endpoint URL
`/search_types_count`

## Request Method
`POST`

## Request Body
The following parameters are required:
- `partner_id` (string, required): The ID of the partner.
- `from_timestamp` (string, optional): The starting timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `to_timestamp` (string, optional): The ending timestamp for the search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `search_type` (string, optional): The specific search type to filter the logs by.

## Response
The response will be a list of objects containing the search types and their counts.

## Response Codes
- `200 OK`: The search types count was retrieved successfully.
- `500 Internal Server Error`: An error occurred during the search process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/search_types_count` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Parses the optional parameters from the JSON data: `from_timestamp`, `to_timestamp`, and `search_type`.
3. Constructs the Elasticsearch index name based on the `partner_id` and a constant value.
4. Checks if the Elasticsearch index exists.
5. Constructs the Elasticsearch query to retrieve the search types count.
6. Applies optional filters based on the provided parameters: `from_timestamp`, `to_timestamp`, and `search_type`.
7. Executes the Elasticsearch search and retrieves the search types count.
8. Processes the search types count and returns them in the response.
# Read Error Logs Endpoint

This code defines a Flask endpoint that retrieves error logs based on specified filters.

## Endpoint URL
`/read_error_logs`

## Request Method
`POST`

## Request Body
The following parameters are required:
- `partner_id` (string, required): The ID of the partner.
- `result_size` (integer, optional): The maximum number of error logs to retrieve. Default value is 10.
- `from_index` (integer, optional): The starting index from which to retrieve error logs. Default value is 0.
- `from_timestamp` (string, optional): The starting timestamp for the error logs search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `to_timestamp` (string, optional): The ending timestamp for the error logs search range. Format: "YYYY-MM-DDTHH:MM:SS".
- `error_code` (integer, optional): The specific error code to filter the error logs by.
- `error_msg` (string, optional): The specific error message to filter the error logs by.

## Response
The response will be a list of error log objects matching the specified filters.

## Response Codes
- `200 OK`: The error logs were retrieved successfully.
- `500 Internal Server Error`: An error occurred during the retrieval process. The response body may contain an error message.

# Code Overview

The code follows the Flask framework's routing approach to handle the `/read_error_logs` endpoint. It performs the following steps:

1. Attempts to extract the `partner_id` from the JSON data in the request. If it is not found, it returns a response with an error message (`partner_id not found`).
2. Parses the optional parameters from the JSON data: `result_size`, `from_index`, `from_timestamp`, `to_timestamp`, `error_code`, and `error_msg`.
3. Constructs the Elasticsearch index name based on the `partner_id` and a constant value.
4. Checks if the Elasticsearch index exists.
5. Constructs the Elasticsearch query to retrieve the error logs.
6. Applies optional filters based on the provided parameters: `from_timestamp`, `to_timestamp`, `error_code`, and `error_msg`.
7. Executes the Elasticsearch search and retrieves the error logs.
8. Processes the error logs and returns them in the response.

