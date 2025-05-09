def truncate_response(response, max_length=1000):
    """Truncate and format API responses to prevent token limit issues."""

    response_str = response
    # Check if the response is a dictionary or list.
    if isinstance(response, dict):
      # Convert the dictionary to a string representation for length evaluation.
      response_str = str(response)
    elif isinstance(response, list):
       # from tests, we see that openai returns responses that could be strings or dictionaries.
       # thus, go through each item individually and do strict type checking
       response_str = ""
       for item in response:
          if isinstance(item, dict):
             response_str += str(item)
          elif isinstance(item, str):
             response_str = response_str + "," + item

          if len(response_str) > max_length:
            # If it exceeds, truncate the string to the specified maximum length.
            response_str = response_str[:max_length]
            # - Append a marker to indicate truncation
            response_str += "#"
            break
             
    elif isinstance(response, str):
       pass
    else:
       raise Exception("unexpected openai message response type %s" % type(response))

    # Check if the length of the string exceeds the maximum allowed length.
    if len(response_str) > max_length:
        # If it exceeds, truncate the string to the specified maximum length.
        response_str = response_str[:max_length]
        # - Append a marker to indicate truncation
        response_str += "#"

    return response_str