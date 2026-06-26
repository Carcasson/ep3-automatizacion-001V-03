#!/usr/bin/env python3
import os, sys, socket, datetime, yaml, re
from ncclient import manager
import xml.etree.ElementTree as ET

VARS = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-03.yaml")))
r = VARS["router"]; c = VARS["cliente"]

print("=== VALIDACION NETCONF ===")
print(f"Script : validacion_netconf.py")
print(f"Fecha  : {datetime.datetime.now()}")
print(f"Host   : {socket.gethostname()}")
print("==========================")

filtro = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>
</filter>"""

with manager.connect(host=r["ip"], port=830, username=r["usuario"],
                     password=r["password"], hostkey_verify=False,
                     allow_agent=False, look_for_keys=False,
                     device_params={"name": "iosxe"}) as m:
    reply = m.get_config(source="running", filter=filtro)
    xml = reply.xml
    with open("evidencias/rpc_reply_raw.xml", "w") as f:
        f.write(xml)

ns = {"n": "http://cisco.com/ns/yang/Cisco-IOS-XE-native"}
root = ET.fromstring(xml)

def find(path):
    el = root.find(path, ns)
    return el.text if el is not None else None

obtenido = {
    "hostname":   find(".//n:native/n:hostname"),
    "loopback_ip":   find(f".//n:interface/n:Loopback[n:name='{r['loopback_id']}']/n:ip/n:address/n:primary/n:address"),
    "loopback_mask": find(f".//n:interface/n:Loopback[n:name='{r['loopback_id']}']/n:ip/n:address/n:primary/n:mask"),
    "descripcion_wan": find(".//n:interface/n:GigabitEthernet[n:name='1']/n:description"),
    "ntp": (re.search(r'<ntp>.*?<ip-address>\s*([\d.]+)', xml, re.DOTALL).group(1)
            if re.search(r'<ntp>.*?<ip-address>', xml, re.DOTALL) else None),
}
esperado = {
    "hostname": c["hostname"], "loopback_ip": r["loopback_ip"],
    "loopback_mask": r["loopback_mask"], "descripcion_wan": r["descripcion_wan"],
    "ntp": r["ntp_server"],
}

ok = 0
for k in esperado:
    estado = "[OK]" if obtenido[k] == esperado[k] else "[FAIL]"
    if estado == "[OK]": ok += 1
    print(f"{estado} {k}: esperado={esperado[k]} obtenido={obtenido[k]}")

print(f"\nResultado: {ok}/5 criterios")
print("CONFORME" if ok == 5 else "NO CONFORME")
