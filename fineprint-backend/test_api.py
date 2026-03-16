import requests

with open("Hackathon_Demo_Contract.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/upload-contract", files={"file": f})
    print(response.status_code)
    print(response.json())
