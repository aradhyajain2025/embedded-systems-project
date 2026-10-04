def checksum(payload):
        result = 0
        for char in payload:
            result ^= ord(char)
        return f"{result:02X}"

def parse_frame(line):
    if line.count("*") != 1:
        return None
    
    payload, given_checksum = line .split("*")
    given_checksum = given_checksum.upper()

    if len(given_checksum) != 2:
        return None

    if not all(c in '0123456789ABCDEF' for c in given_checksum):
        return None

    fields = payload.split(",")

    if len(fields) != 3:
        return None

    if not all(field.count(":") == 1 for field in fields):
        return None

    names = [field.split(":")[0] for field in fields]

    if names != ["P", "D", "S"]:
        return None

    if not all(field.split(":")[1] for field in fields):
        return None
    
    p = fields[0].split(":")[1]
    d = fields[1].split(":")[1]
    s = fields[2].split(":")[1]
    if len(str(p)) != 1 or len(str(d)) not in [1, 2, 3] or len(str(s)) != 1:
        return None

    value = p,d,s
    if not all(c in "0123456789" for v in value for c in v):
        return None
    try:
        p, d, s = [int(v) for v in value]
    except ValueError:
        return None

    if len(str(p)) != 1 or len(str(d)) not in [1, 2, 3] or len(str(s)) != 1:
        return None

    if not (p in [0, 1] and s in [0, 1]):
        return None

    if not (d == 0 or (2 <= d <= 400)):
        return None
    
    calculated_checksum = checksum(payload)
    if calculated_checksum != given_checksum:
        return None

    return (p, d, s)

