import streamlit as st
from utils.data_io import read_vms, read_hosts, read_network, export_plan
from planners.migration import migration_planner
from utils.network_graph import build_graph, visualize_graph

st.title("VM Migration Planner")

# Add sidebar configuration
st.sidebar.header("Configuration")
network_bandwidth = st.sidebar.slider(
    "Network Bandwidth (Mbps)", 
    min_value=100, 
    max_value=10000, 
    value=1000, 
    step=100,
    help="Adjust network bandwidth for migration time estimation"
)

vm_file = st.file_uploader("Upload VM dataset (CSV/JSON):")
host_file = st.file_uploader("Upload Host dataset (CSV/JSON):")
net_file = st.file_uploader("Upload Network Topology (CSV/JSON):")

if vm_file and host_file and net_file:
    vms = read_vms(vm_file)
    hosts = read_hosts(host_file)
    network_df = read_network(net_file)
    
    # Generate migration plan with estimations
    plan = migration_planner(vms, hosts, network_bandwidth_mbps=network_bandwidth)
    
    # Display migration statistics
    st.header(" Migration Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        successful_migrations = sum(1 for m in plan if m['host_id'] is not None)
        st.metric("Successful Migrations", successful_migrations)
    
    with col2:
        failed_migrations = sum(1 for m in plan if m['host_id'] is None)
        st.metric("Failed Migrations", failed_migrations, delta=None if failed_migrations == 0 else f"-{failed_migrations}")
    
    with col3:
        total_time = sum(m['estimated_time_minutes'] for m in plan if m['estimated_time_minutes'] is not None)
        st.metric("Total Est. Time", f"{total_time:.1f} min")
    
    with col4:
        total_resources = sum(m['resource_usage']['total_resource_units'] for m in plan)
        st.metric("Total Resource Units", f"{total_resources:.0f}")
    
    # Display color legend
    st.header(" Visualization Legend")
    
    legend_col1, legend_col2 = st.columns(2)
    
    with legend_col1:
        st.markdown("**Host Node Colors (by Utilization):**")
        st.markdown("🟢 **Green** - Low utilization (<50%)")
        st.markdown("🟡 **Gold** - Medium utilization (50-75%)")
        st.markdown("🟠 **Orange** - High utilization (75-90%)")
        st.markdown("🔴 **Red** - Very high utilization (>90%)")
    
    with legend_col2:
        st.markdown("**VM Node Colors:**")
        st.markdown("🔵 **Sky Blue** - Being migrated")
        st.markdown("⚪ **Light Gray** - Not migrated")
        st.markdown("\n**Arrows:**")
        st.markdown("🔴 **Red Arrow** - Migration path with time estimate")
    
    # Build and visualize graph
    st.header(" Network Topology & Migration Plan")
    G = build_graph(network_df, hosts, vms, plan)

    html_file = visualize_graph(G, "network_graph.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=750)
    
    # Display detailed migration table
    st.header(" Detailed Migration Plan")
    
    # Create a formatted table for display
    display_plan = []
    for m in plan:
        display_row = {
            'VM ID': m['vm_id'],
            'Target Host': m['host_id'] if m['host_id'] else 'FAILED',
            'CPU (cores)': m['resource_usage']['cpu_cores'],
            'RAM (GB)': m['resource_usage']['ram_gb'],
            'Storage (GB)': m['resource_usage']['storage_gb'],
            'Est. Time (min)': f"{m['estimated_time_minutes']:.2f}" if m['estimated_time_minutes'] else 'N/A',
            'Est. Time (sec)': f"{m['estimated_time_seconds']:.2f}" if m['estimated_time_seconds'] else 'N/A'
        }
        display_plan.append(display_row)
    
    st.dataframe(display_plan, use_container_width=True)
    
    # Export options
    st.header(" Export Migration Plan")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("Export as CSV"):
            export_plan(plan, "migration_plan.csv")
            st.success(' Migration plan exported as migration_plan.csv')
    
    with col_exp2:
        if st.button("Export as JSON"):
            export_plan(plan, "migration_plan.json")
            st.success(' Migration plan exported as migration_plan.json')
    
    # Show raw plan data in expander
    with st.expander("🔍 View Raw Migration Plan Data"):
        st.json(plan)
else:
    st.warning(" Upload all required datasets to proceed.")
