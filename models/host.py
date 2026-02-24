class Host:
    def __init__(self, id, max_cpu, max_ram, max_storage):
        self.id = id
        self.max_cpu = max_cpu
        self.max_ram = max_ram
        self.max_storage = max_storage
        self.vms = []
        self.used_cpu = 0
        self.used_ram = 0
        self.used_storage = 0

    def can_host(self, vm):
        return (self.used_cpu + vm.cpu <= self.max_cpu and
                self.used_ram + vm.ram <= self.max_ram and
                self.used_storage + vm.storage <= self.max_storage)

    def add_vm(self, vm):
        if self.can_host(vm):
            self.vms.append(vm)
            self.used_cpu += vm.cpu
            self.used_ram += vm.ram
            self.used_storage += vm.storage
            return True
        return False