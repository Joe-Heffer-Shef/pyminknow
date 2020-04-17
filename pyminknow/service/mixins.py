class ServiceMixin:
    server_adder = None

    def add_to_server(self, server):
        self.server_adder(self, server)
