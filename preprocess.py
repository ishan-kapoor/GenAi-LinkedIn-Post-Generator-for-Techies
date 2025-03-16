import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


def process_posts(raw_file_path, processed_file_path=None):
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        enriched_posts = []
        for post in posts:
            metadata = extract_metadata(post['Text'])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags[tag] for tag in current_tags}
        post['tags'] = list(new_tags)

    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4)


def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)
    
    Here is the actual post on which you need to perform this task:  
    {post}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res


def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    # Loop through each post and extract the tags
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])  # Add the tags to the set

    unique_tags_list = ','.join(unique_tags)

    template = '''I will provide a list of tags related to LinkedIn posts. Your task is to unify them based on the following guidelines:

        1. Merge similar tags into a shorter, more standardized list.
         Example 1: "Full Stack Developer", "Full Stack Engineering" → "Full Stack Development"
         Example 2: "Machine Learning", "ML Engineer" → "Machine Learning"
         Example 3: "Software Engineer", "Developer", "Coder" → "Software Engineering"
         Example 4: "Artificial Intelligence", "AI Engineer", "AI" → "Artificial Intelligence"
    2. Follow Title Case formatting for consistency.
         Example: "Deep learning" → "Deep Learning"
         Example: "frontend dev" → "Frontend Development"
    3. Output should be in JSON format with mappings of original tags to the unified tags.
         Example output:  
           ```json
           {
           "Full Stack Developer": "Full Stack Development",
           "ML Engineer": "Machine Learning",
           "AI Engineer": "Artificial Intelligence"
           }
            ```
    4. No extra text or explanations—only return the JSON object.

    Here is the list of tags:  
    {tags}
'''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(unique_tags_list)})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res


if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")