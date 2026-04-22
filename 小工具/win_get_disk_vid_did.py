import re
import subprocess
import sys


def ps(command: str) -> str:
    r = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True)
    out = r.stdout.decode("gbk", errors="ignore").strip()
    err = r.stderr.decode("gbk", errors="ignore").strip()
    if r.returncode != 0:
        raise RuntimeError(err or "PowerShell 执行失败")
    return out


# 磁盘编号，默认3
disk_no = int(sys.argv[1]) if len(sys.argv) > 1 else 3
disk_id = ps(
    f"Get-CimInstance Win32_DiskDrive | Where-Object {{$_.Index -eq {disk_no}}} "
    "| Select-Object -ExpandProperty PNPDeviceID"
)
parent_id = ps(
    f"Get-PnpDeviceProperty -InstanceId '{disk_id}' -KeyName 'DEVPKEY_Device_Parent' "
    "| Select-Object -ExpandProperty Data"
)

vid = re.search(r"(VID|VEN)_([0-9A-Fa-f]{4})", parent_id, re.I)
did = re.search(r"(DID|DEV|PID)_([0-9A-Fa-f]{4})", parent_id, re.I)

print(f"磁盘: {disk_no}")
print(f"VID: {vid.group(2).upper() if vid else '未找到'}")
print(f"DID: {did.group(2).upper() if did else '未找到'}")