import json

def check_progress(jsonfile):
    try: 
        with open(jsonfile, "r") as f:
            data = json.load(f)
            last_comp_id = int(data.get("last_comp_id", 0))
    except json.JSONDecodeError:
        last_comp_id = 0
    return last_comp_id

def save_progress(jsonfile, comp_id):
    with open(jsonfile, "w") as f:
        json.dump({"last_comp_id": comp_id}, f)