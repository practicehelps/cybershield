import uuid
import re

class PIIMasker:
    def __init__(self):
        """Initialize the PII masker with pattern mappings and priority order."""
        # Create dictionaries for mapping original PII to placeholders and vice versa.
        self.mask_map = {}
        self.unmask_map = {}

        # Define regex patterns for different types of PII.
        # Ensure the patterns cover common formats (e.g., email, phone, IP address, credit card, SSN).
        self.ssn_regex = ["\d{3}-\d{2}-\d{4}"]
        self.ip_regex = ["\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"]
        self.credit_card_regex = ["^\d{4}-\d{4}-\d{4}-\d{4}"]
        self.phone_regex = ["\d{3}-\d{3}-\d{4}"]
        # Define Regex to detect email address
        self.email_regex = ["[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"]

        # Define the order in which patterns should be processed.
        self.regex_patterns = [
            self.email_regex,
            self.ssn_regex,
            self.ip_regex,
            self.credit_card_regex,
            self.phone_regex,
        ]
        # This ensures that more specific patterns (e.g., email) are matched before broader ones (e.g., domain).

    def mask(self, text: str) -> str:
        """Mask PII in text with unique placeholders."""
        # Iterate through PII patterns in priority order.
        for pattern_list in self.regex_patterns:
            for pattern in pattern_list:
              # Use regex to find occurrences of PII in the text.
              # while matches is not empty
              matches = re.findall(pattern, text)
              print("matches = %s" % matches)

              # Check if the matched PII has already been masked to avoid duplicate masking.
              # If not already masked, generate a unique placeholder using UUID.
              for match_str in matches:
                if match_str not in self.mask_map:
                  placeholder = str(uuid.uuid4())
                  # Replace the original PII with the placeholder in the text.
                  text = text.replace(match_str, placeholder)
                  # Store the original PII value in a mapping for unmasking.
                  self.mask_map[match_str] = placeholder
                  # Store the placeholder value in a mapping for unmasking.
                  self.unmask_map[placeholder] = match_str

        # Return the masked text
        return text

    def unmask(self, text: str) -> str:
        """Unmask PII placeholders back to original values."""
        # Sort placeholders by length to prevent partial replacements.
        sorted_placeholders = sorted(self.unmask_map.keys(), key=len, reverse=True)

        # Iterate through placeholders and replace them with the original values.
        for placeholder in sorted_placeholders:
            text = text.replace(placeholder, self.unmask_map[placeholder])

        # Return the unmasked text.
        return text

    def clear(self):
        """Clear stored PII mappings to remove all stored associations."""
        # Reset both the mask map and unmask map to free memory.
        self.mask_map = {}
        self.unmask_map = {}

