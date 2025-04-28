import json
from index import lambda_handler  # your file 名に合わせて

# 擬似的な Lambda コンテキスト
class Context:
    invoked_function_arn = "arn:aws:lambda:ap-northeast-1:123456789012:function:LocalTest"

if __name__ == "__main__":
    with open("lambda/event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
    context = Context()
    response = lambda_handler(event, context)
    print(json.dumps(response, ensure_ascii=False, indent=2))
