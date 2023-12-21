import slimDNS

dns = slimDNS.server(slimDNS.UDP)

@dns.records
def records(server):
	return {
		"example.com" : {
			"A" : {"target" : "10.3.0.3", "ttl" : 60},
			"SOA" : {"target" : "example.com", "ttl" : 60},
			"NS" : {"target" : "example.com", "ttl" : 60, "priority" : 10}
		},
	}

dns.run()
