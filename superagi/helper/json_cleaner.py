import json
import re

import json5


class JsonCleaner:

    @classmethod
    def check_and_clean_json(cls, json_string: str):
        try:
            json_string = cls.remove_escape_sequences(json_string)
            json_string = cls.remove_trailing_newline_spaces(json_string)
            json_string = cls.clean_newline_characters(json_string)

            json5.loads(json_string)
            return json_string
        except (ValueError, json.JSONDecodeError) as e:
            # If the json is invalid, try to clean it up
            json_string = cls.extract_json_section(json_string)
            json_string = cls.preprocess_json_input(json_string)
            json_string = cls.add_quotes_to_property_names(json_string)
            json_string = cls.remove_escape_sequences(json_string)
            # call this post remove_escape_sequences
            json_string = cls.clean_newline_characters(json_string)
            json_string = cls.balance_braces(json_string)
            try:
                json5.loads(json_string)
                return json_string
            except (ValueError, json.JSONDecodeError) as e:
                print(json_string)
                # If the json is still invalid, try to extract the json section
                json_string = cls.extract_json_section(json_string)
                return json_string
        return json_string

    @classmethod
    def preprocess_json_input(cls, input_str: str) -> str:
        # Replace single backslashes with double backslashes,
        # while leaving already escaped ones intact
        corrected_str = re.sub(
            r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r"\\\\", input_str
        )
        return corrected_str

    @classmethod
    def extract_json_section(cls, input_str: str = ""):
        try:
            first_brace_index = input_str.index("{")
            final_json = input_str[first_brace_index:]
            last_brace_index = final_json.rindex("}")
            final_json = final_json[: last_brace_index + 1]
            return final_json
        except ValueError:
            pass
        return input_str

    @classmethod
    def remove_escape_sequences(cls, string):
        return string.encode('utf-8').decode('unicode_escape').encode('raw_unicode_escape').decode('utf-8')

    @classmethod
    def remove_trailing_newline_spaces(cls, json_string):
        json_string = re.sub(r'\n+\s+"', '"', json_string)
        json_string = re.sub(r'}\n+\s+}', '}}', json_string)
        json_string = re.sub(r'"\n+\s+}', '"}', json_string)
        json_string = re.sub(r'\n+}', '}', json_string)
        return json_string.strip()
    @classmethod
    def clean_newline_characters(cls, string):
        string = string.replace("\t", "\\t")
        string = string.replace("\n", "\\n")
        return string

    @classmethod
    def add_quotes_to_property_names(cls, json_string: str) -> str:
        def replace(match: re.Match) -> str:
            return f'"{match.group(1)}":'

        json_string = re.sub(r'(\b\w+\b):', replace, json_string)

        return json_string

    @classmethod
    def balance_braces(cls, json_string: str) -> str:
        open_braces_count = json_string.count('{')
        closed_braces_count = json_string.count('}')

        while closed_braces_count > open_braces_count:
            json_string = json_string.rstrip("}")
            closed_braces_count -= 1

        open_braces_count = json_string.count('{')
        closed_braces_count = json_string.count('}')

        if open_braces_count > closed_braces_count:
            json_string += '}' * (open_braces_count - closed_braces_count)

        return json_string
