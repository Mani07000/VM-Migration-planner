import pandas as pd
import json

from models.vm import VM

def read_vms(uploaded_file):
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)
    # Create and return a list of VM objects
    return [VM(row['id'], row['cpu'], row['ram'], row['storage']) for _, row in df.iterrows()]


from models.host import Host  # Make sure to import the Host class!

def read_hosts(uploaded_file):
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)
    # Correct: instantiate Host, not recursive call to read_hosts
    return [Host(row['id'], row['max_cpu'], row['max_ram'], row['max_storage']) for _, row in df.iterrows()]


def read_network(uploaded_file):
    if uploaded_file.name.endswith('csv'):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_json(uploaded_file)

def export_plan(plan, file_path):
    if file_path.endswith('csv'):
        pd.DataFrame(plan).to_csv(file_path, index=False)
    else:
        with open(file_path, 'w') as f:
            json.dump(plan, f, indent=2)
