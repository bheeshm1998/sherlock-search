import openai

openai.api_key = "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"

response = openai.api_requestor.Requestor().request("GET", "/dashboard/billing/credit_grants")

print(response)
