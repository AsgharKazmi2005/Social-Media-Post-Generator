from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    elif length == "Medium":
        return "6 to 10 lines"
    elif length == "Long":
        return "11 to 20 lines"

def generate_post(tag, length, language):
    length_str = get_length_str(length)
    prompt = f'''
    Generate a linkedin post usin the below information. No preamble.
    
    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    
    
'''
    examples = few_shot.get_filtered_posts(length, language, tag)
    print(examples)
    if len(examples)>0:
        prompt+="4) Use the writing style as per the following examples:"
        for i, post in enumerate(examples):
            post_text=post['text']
            prompt+=f"\n\n Example {i+1} \n\n {post_text}"
            if i == 1:
                break

    response = llm.invoke(prompt)
    return response.content

if __name__ == '__main__':
    post = generate_post("Short", "English", "Motivation")
    print(post)