def truncate_response(response, max_length=1000):
    """Truncate and format API responses to prevent token limit issues."""

    response_str = ""
    # Check if the response is a dictionary.
    if  isinstance(response, dict):
      # Convert the dictionary to a string representation for length evaluation.
      response_str = str(response)

    # Check if the length of the string exceeds the maximum allowed length.
    if len(response_str) > max_length:
        # If it exceeds, truncate the string to the specified maximum length.
        truncated_response = response_str[:max_length]
        # - Append a marker to indicate truncation
        response_str += "#"

    return response_str