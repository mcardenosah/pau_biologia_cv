import json

files = [
    "webapp/src/data_2011_2014.json",
    "webapp/src/data_2015_2019.json",
    "webapp/src/data_2020_2025.json"
]

master_data = []

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        for q in data:
            q['id'] = f"q_{len(master_data) + 1}"
            master_data.append(q)

with open('webapp/src/master_data.json', 'w', encoding='utf-8') as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)

print(f"Fusionados {len(master_data)} exámenes en master_data.json")
