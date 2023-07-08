
# get_es_read_results Function

This function retrieves results from Elasticsearch based on specified parameters.

## Parameters
- `es_articles_index_name` (string): The name of the Elasticsearch index to search.
- `sort_by` (string): The sorting option for the results. Possible values are "relv" (relevance), "desc" (descending), or "asc" (ascending).
- `from_result` (integer): The starting index from which to retrieve results.
- `request` (object): The Flask request object containing the JSON data.
- `partner_id` (string): The ID of the partner.
- `result_size` (integer, optional): The maximum number of results to retrieve. Default value is 10.

## Return Value
The function returns a tuple containing the total number of results and a list of news IDs.

## Error Handling
If any exception occurs during the process, the function catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.

# Code Overview

The function performs the following steps:

1. Constructs the Elasticsearch query based on the provided parameters, including the `es_articles_index_name`, `sort_by`, `from_result`, and `result_size`.
2. Handles the different sorting options by modifying the Elasticsearch query accordingly.
3. Executes the Elasticsearch search and retrieves the results.
4. Extracts the news IDs from the retrieved results.
5. Returns the total number of results and the list of news IDs.

# get_es_search_results Function

This function retrieves search results from Elasticsearch based on specified parameters.

## Parameters
- `es_articles_index_name` (string): The name of the Elasticsearch index to search.
- `search_keyword` (string): The keyword to search for.
- `from_result` (integer): The starting index from which to retrieve results.
- `sort_by` (string): The sorting option for the results. Possible values are "relv" (relevance), "desc" (descending), or "asc" (ascending).
- `fields` (list): The list of fields to search within.
- `request` (object): The Flask request object containing the JSON data.
- `partner_id` (string): The ID of the partner.
- `result_size` (integer, optional): The maximum number of results to retrieve. Default value is 10.

## Return Value
The function returns a tuple containing the total number of search results, a list of news IDs, and the time taken for the search.

## Error Handling
If any exception occurs during the process, the function catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.

# Code Overview

The function performs the following steps:

1. Processes the search keyword to handle different types of search queries.
2. Constructs the Elasticsearch query based on the provided parameters, including the `es_articles_index_name`, `search_keyword`, `from_result`, `sort_by`, and `fields`.
3. Handles the different sorting options by modifying the Elasticsearch query accordingly.
4. Executes the Elasticsearch search and retrieves the results.
5. Extracts the news IDs from the retrieved results.
6. Returns the total number of search results, the list of news IDs, and the time taken for the search.

# get_es_adv_search_results Function

This function retrieves advanced search results from Elasticsearch based on specified parameters.

## Parameters
- `es_articles_index_name` (string): The name of the Elasticsearch index to search.
- `from_result` (integer): The starting index from which to retrieve results.
- `sort_by` (string): The sorting option for the results. Possible values are "relv" (relevance), "desc" (descending), or "asc" (ascending).
- `field_query_values` (dictionary): The dictionary containing field-specific query values for advanced search.
- `request` (object): The Flask request object containing the JSON data.
- `partner_id` (string): The ID of the partner.
- `result_size` (integer, optional): The maximum number of results to retrieve. Default value is 10.

## Return Value
The function returns a tuple containing the total number of search results, a list of news IDs, and the time taken for the search.

## Error Handling
If any exception occurs during the process, the function catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.

# Code Overview

The function performs the following steps:

1. Processes the field-specific query values provided in the `field_query_values` dictionary.
2. Constructs the Elasticsearch query based on the provided parameters, including the `es_articles_index_name`, `from_result`, `sort_by`, and field-specific query values.
3. Handles the different sorting options by modifying the Elasticsearch query accordingly.
4. Executes the Elasticsearch search and retrieves the results.
5. Extracts the news IDs from the retrieved results.
6. Returns the total number of search results, the list of news IDs, and the time taken for the search.


# remove_stop_words Function

This function removes stop words from a given sentence.

## Parameters
- `sentence` (string): The sentence from which to remove stop words.

## Return Value
The function returns a string containing the sentence with stop words removed.

## Error Handling
If any exception occurs during the process, the function catches the exception, logs the error details using the `create_error_log` function, and returns a response with the error message.

# Code Overview

The function performs the following steps:

1. Defines a list of stop words to be removed from the sentence.
2. Splits the sentence into individual words.
3. Filters out the stop words from the list of words using a list comprehension.
4. Joins the filtered words back into a string.
5. Returns the string with stop words removed.

# generate_3_shingles Function

This function generates 3-shingles from a given text.

## Parameters
- `text` (string): The text from which to generate the 3-shingles.

## Return Value
The function returns a list of 3-shingles.

## Code Overview

The function performs the following steps:

1. Converts the text to lowercase and splits it into individual tokens.
2. Checks if the number of tokens is less than 3. If true, returns the list of tokens.
3. Generates 3-shingles by creating sliding windows of size 3 over the tokens.
4. Joins each 3-shingle into a string.
5. Returns the list of generated 3-shingles.

# generate_2_shingles Function

This function generates 2-shingles from a given text.

## Parameters
- `text` (string): The text from which to generate the 2-shingles.

## Return Value
The function returns a list of 2-shingles.

## Code Overview

The function performs the following steps:

1. Converts the text to lowercase and splits it into individual tokens.
2. Checks if the number of tokens is less than 2. If true, returns the list of tokens.
3. Generates 2-shingles by creating sliding windows of size 2 over the tokens.
4. Joins each 2-shingle into a string.
5. Returns the list of generated 2-shingles.

# create_error_log Function

This function creates an error log in Elasticsearch for a given partner ID and error dictionary.

## Parameters
- `partner_id` (string): The ID of the partner for whom the error log is being created.
- `error_dict` (dictionary): A dictionary containing the details of the error log. The dictionary should have the following keys:
  - `"error_msg"` (string): The error message.
  - `"error_code"` (integer): The error code.
  - `"request_json"` (dictionary): The JSON data of the request that resulted in the error.
  - `"timestamp"` (datetime): The timestamp when the error occurred.

## Return Value
The function returns a response indicating the status of the error log creation.

## Code Overview

The function performs the following steps:

1. Constructs the Elasticsearch index name for error logs based on the partner ID and environment variables.
2. Checks if the Elasticsearch index exists for error logs.
3. If the index exists, indexes the error log using the Elasticsearch client.
4. Checks the result of the indexing operation and returns an appropriate response indicating the success or failure of the error log creation.

# create_search_log Function

This function creates a search log in Elasticsearch for a given partner ID and search details.

## Parameters
- `partner_id` (string): The ID of the partner for whom the search log is being created.
- `phrase` (string): The search phrase or keyword used in the search.
- `total_search_results` (integer): The total number of search results returned for the search.
- `auto_suggs_suggestions` (list): A list of suggested search terms provided by the autocomplete feature.
- `search_type` (string): The type of search performed, such as "basic" or "advanced".
- `search_parameters` (dictionary): A dictionary containing the parameters used in the search.

## Return Value
The function returns a response indicating the status of the search log creation.

## Code Overview

The function performs the following steps:

1. Constructs the Elasticsearch index name for search logs based on the partner ID and environment variables.
2. Checks if the Elasticsearch index exists for search logs.
3. If the index exists, creates a search log dictionary containing the search details.
4. Indexes the search log using the Elasticsearch client.
5. Checks the result of the indexing operation and returns an appropriate response indicating the success or failure of the search log creation.


