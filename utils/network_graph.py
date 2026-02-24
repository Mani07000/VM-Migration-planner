import networkx as nx
from pyvis.network import Network


def get_host_color(host):
    
    # Calculate average utilization percentage
    cpu_util = (host.used_cpu / host.max_cpu * 100) if host.max_cpu > 0 else 0
    ram_util = (host.used_ram / host.max_ram * 100) if host.max_ram > 0 else 0
    storage_util = (host.used_storage / host.max_storage * 100) if host.max_storage > 0 else 0
    
    avg_util = (cpu_util + ram_util + storage_util) / 3
    
    # Color-code based on utilization
    if avg_util < 50:
        return '#90EE90'  # Light green - low utilization
    elif avg_util < 75:
        return '#FFD700'  # Gold - medium utilization
    elif avg_util < 90:
        return '#FFA500'  # Orange - high utilization
    else:
        return '#FF6B6B'  # Red - very high utilization


def get_vm_color(vm, is_migrated):
    
    if is_migrated:
        return '#87CEEB'  # Sky blue - being migrated
    else:
        return '#D3D3D3'  # Light gray - not migrated


def build_graph(network_df, hosts, vms, plan):
    
    G = nx.DiGraph()  # Use directed graph for better arrow visualization
    
    # Add network topology edges (if network_df has the expected columns)
    if not network_df.empty and 'src' in network_df.columns and 'dst' in network_df.columns:
        for idx, row in network_df.iterrows():
            G.add_edge(row['src'], row['dst'], 
                       label=row.get('label', ''),
                       color='#CCCCCC',
                       width=1)
    
    # Create a lookup for migrated VMs
    migrated_vms = {m['vm_id']: m for m in plan if m['host_id'] is not None}
    
    # Add host nodes with color-coding based on utilization
    for host in hosts:
        host_color = get_host_color(host)
        utilization = {
            'cpu': f"{host.used_cpu}/{host.max_cpu}",
            'ram': f"{host.used_ram}/{host.max_ram}",
            'storage': f"{host.used_storage}/{host.max_storage}"
        }
        
        G.add_node(
            host.id, 
            label=f"Host: {host.id}",
            title=f"Host {host.id}\nCPU: {utilization['cpu']}\nRAM: {utilization['ram']} GB\nStorage: {utilization['storage']} GB",
            color=host_color,
            shape='box',
            size=30
        )
    
    # Add VM nodes with color-coding based on migration status
    for vm in vms:
        is_migrated = vm.id in migrated_vms
        vm_color = get_vm_color(vm, is_migrated)
        
        vm_info = f"VM: {vm.id}\nCPU: {vm.cpu} cores\nRAM: {vm.ram} GB\nStorage: {vm.storage} GB"
        
        if is_migrated:
            migration_data = migrated_vms[vm.id]
            vm_info += f"\n\n Migrating to: {migration_data['host_id']}"
            if migration_data['estimated_time_minutes']:
                vm_info += f"\n Est. Time: {migration_data['estimated_time_minutes']} min"
        
        G.add_node(
            vm.id,
            label=f"VM: {vm.id}",
            title=vm_info,
            color=vm_color,
            shape='ellipse',
            size=20
        )
    
    # Add migration plan as prominent arrows with labels
    for mapping in plan:
        if mapping['host_id']:
            # Create migration edge label
            edge_label = "Migration"
            if mapping['estimated_time_minutes']:
                edge_label += f"\n {mapping['estimated_time_minutes']} min"
            
            # Add edge with styling
            G.add_edge(
                mapping['vm_id'], 
                mapping['host_id'],
                label=edge_label,
                title=f"Migrating {mapping['vm_id']} → {mapping['host_id']}\nTime: {mapping['estimated_time_seconds']}s ({mapping['estimated_time_minutes']} min)",
                color='#FF4444',  # Red for migration arrows
                width=3,
                arrows='to',
                dashes=False,
                physics=True
            )
    
    return G


def visualize_graph(G, output_html):
    
    net = Network(
        height="700px", 
        width="100%", 
        directed=True,
        bgcolor="#FFFFFF",
        font_color="black"
    )
    
    # Configure physics for better layout
    net.set_options("""
    {
        "nodes": {
            "font": {
                "size": 14,
                "face": "arial"
            },
            "borderWidth": 2,
            "borderWidthSelected": 4
        },
        "edges": {
            "font": {
                "size": 12,
                "align": "middle"
            },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                }
            },
            "smooth": {
                "enabled": true,
                "type": "continuous"
            }
        },
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04
            },
            "stabilization": {
                "iterations": 150
            }
        }
    }
    """)
    
    net.from_nx(G)
    net.write_html(output_html)
    
    return output_html
