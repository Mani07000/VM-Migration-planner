def estimate_migration_time(vm, network_bandwidth_mbps=1000):
        # Convert storage from GB to Mb (Gigabytes to Megabits)
    storage_mb = vm.storage * 8 * 1024  # GB -> MB -> Mb
    
    # Calculate transfer time in seconds
    migration_time = storage_mb / network_bandwidth_mbps
    
    # Add overhead (downtime, setup time) - typically 10-20% of transfer time
    overhead_factor = 1.15
    total_time = migration_time * overhead_factor
    
    return round(total_time, 2)


def calculate_resource_usage(vm):
    
    return {
        'cpu_cores': vm.cpu,
        'ram_gb': vm.ram,
        'storage_gb': vm.storage,
        'total_resource_units': vm.cpu + vm.ram + vm.storage
    }


def migration_planner(vms, hosts, network_bandwidth_mbps=1000):
    plan = []
    hosts_map = {host.id: host for host in hosts}
    
    for vm in vms:
        migration_entry = {
            'vm_id': vm.id,
            'host_id': None,
            'estimated_time_seconds': None,
            'estimated_time_minutes': None,
            'resource_usage': calculate_resource_usage(vm)
        }
        
        for host in hosts:
            if host.can_host(vm):
                host.add_vm(vm)
                migration_entry['host_id'] = host.id
                
                # Add time estimation
                time_seconds = estimate_migration_time(vm, network_bandwidth_mbps)
                migration_entry['estimated_time_seconds'] = time_seconds
                migration_entry['estimated_time_minutes'] = round(time_seconds / 60, 2)
                
                break
        
        plan.append(migration_entry)
    
    return plan
