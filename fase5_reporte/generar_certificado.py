#!/usr/bin/env python3
import os, glob, datetime, yaml

VARS = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-03.yaml")))
c = VARS["cliente"]

def leer(path):
    try: return open(path).read()
    except: return ""

netconf = leer("../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt")
restconf = leer("../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt")
diff_files = glob.glob("evidencias/diff_001V-03/*")

net_ok = "CONFORME" in netconf and "NO CONFORME" not in netconf
rest_ok = "CONFORME" in restconf and "NO CONFORME" not in restconf
diff_ok = len(diff_files) > 0
compliance = net_ok and rest_ok and diff_ok

cert = f"""============================================
   CERTIFICADO DE COMPLIANCE - EP3 DRY7122
============================================
Alumno   : {VARS['nombre']} ({VARS['codigo']})
Cliente  : {c['empresa']}
Hostname : {c['hostname']}
Fecha    : {datetime.datetime.now()}
--------------------------------------------
Validacion NETCONF  : {"CONFORME" if net_ok else "NO CONFORME"}
Validacion RESTCONF : {"CONFORME" if rest_ok else "NO CONFORME"}
Diff detectado      : {"SI" if diff_ok else "NO"} ({len(diff_files)} archivos)
--------------------------------------------
RESULTADO GLOBAL    : {"CONFORME" if compliance else "NO CONFORME"}
============================================
Equipo {"LISTO PARA OPERAR" if compliance else "REQUIERE REVISION"}.
"""
with open("evidencias/certificado_compliance_001V-03.txt", "w") as f:
    f.write(cert)
print(cert)
