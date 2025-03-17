import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm



def process_posts(raw_file_path, processed_file_path="data/processed_post.json"):
    enriched_posts= []
    with open(raw_file_path, encoding ='utf-8') as file:
        posts=json.load(file)
        for post in posts:
            metadata = extract_metadata(post['text'])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags.get(tag, tag) for tag in current_tags}
        post['tags'] = list(new_tags)
    with open(processed_file_path, mode='w', encoding='utf-8') as outfile:
        json.dump(enriched_posts, outfile, indent=4)

def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])

    unique_tags_list = ', '.join(unique_tags)

    template = """ I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list.
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search"
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to Scams 
    2. Each tag should follow title case convention. Examples: "Motivation", "Job Search"
    3. Output must be a JSON object, no Preamble
       for example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation":"Motivation"}}
    
    Here is the list of tags:
    {tags}
    """

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke({'tags': str(unique_tags_list)})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException as e:
        raise OutputParserException(f"Error processing LLM response: {str(e)}")

    return res


def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. Extract metadata in **valid JSON format**:

    1. Return a **valid JSON object**. Do not include any text before or after the JSON.
    2. JSON object should have exactly three keys: `line_count`, `language`, and `tags`.
    3. `line_count`: Count the number of **lines** in the post (counting `\n` as line breaks).
    4. `language`: Always return `"English"`.
    5. `tags`: An **array** of **at most two** keyword tags based on the post's content.

    Here is the post:
    ```
    {post}
    ```

    **Return only JSON output. No explanations, comments, or code.**
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke({'post': post})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException as e:
        raise OutputParserException(f"Error processing LLM response: {str(e)}")

    return res

if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_post.json")