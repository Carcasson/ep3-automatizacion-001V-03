#!/usr/bin/env python3
import os, json, socket, datetime, yaml, requests, urllib3
urllib3.disable_warnings()

VARS = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-03.yaml")))
r = VARS["router"]; c = VARS["cliente"]
BASE = f"https://{r['ip']}/restconf/data"
HDR = {"Accept": "application/yang-data+json"}
AUTH = (r["usuario"], r["password"])

print("=== VALIDACION RESTCONF ===")
print(f"Script : validacion_restconf.py")
print(f"Fecha  : {datetime.datetime.now()}")
print(f"Host   : {socket.gethostname()}")
print("===========================")

os.makedirs("evidencias/responses", exist_ok=True)
endpoints = {
    "get_hostname.json":   "Cisco-IOS-XE-native:native/hostname",
    "get_loopback.json":   f"ietf-interfaces:interfaces/interface=Loopback{r['loopback_id']}",
    "get_interfaces.json": "ietf-interfaces:interfaces/interface=GigabitEthernet1",
    "get_ntp.json":        "Cisco-IOS-XE-native:native/ntp",
}
data = {}
for archivo, ep in endpoints.items():
    resp = requests.get(f"{BASE}/{ep}", headers=HDR, auth=AUTH, verify=False)
    j = resp.json()
    with open(f"evidencias/responses/{archivo}", "w") as f:
        json.dump(j, f, indent=2)
    data[archivo] = j

hostname = data["get_hostname.json"].get("Cisco-IOS-XE-native:hostname")
lo = data["get_loopback.json"]["ietf-interfaces:interface"]
lo_ip = lo.get("ietf-ip:ipv4", {}).get("address", [{}])[0].get("ip")
gi = data["get_interfaces.json"]["ietf-interfaces:interface"]
desc = gi.get("description")
ntp = json.dumps(data["get_ntp.json"])

checks = {
    "hostname": (hostname, c["hostname"]),
    "loopback_ip": (lo_ip, r["loopback_ip"]),
    "descripcion_wan": (desc, r["descripcion_wan"]),
    "ntp": (r["ntp_server"] in ntp, True),
}
ok = 0
for k, (got, exp) in checks.items():
    estado = "[OK]" if got == exp else "[FAIL]"
    if estado == "[OK]": ok += 1
    print(f"{estado} {k}: esperado={exp} obtenido={got}")

print(f"\nResultado: {ok}/4 criterios")
print("CONFORME" if ok == 4 else "NO CONFORME")
