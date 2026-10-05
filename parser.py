def checksum(payload):
    result = 0
    for char in payload:
        result ^= ord(char)
    return f"{result:02X}"


def parse_frame(line):
    if line.count("*") != 1:
        return None

    payload, given_checksum = line.split("*")
    given_checksum = given_checksum.upper()

    if len(given_checksum) != 2:
        return None
    if not all(c in "0123456789ABCDEF" for c in given_checksum):
        return None

    fields = payload.split(",")
    if len(fields) != 3:
        return None
    if not all(field.count(":") == 1 for field in fields):
        return None

    names = [field.split(":")[0] for field in fields]
    if names != ["P", "D", "S"]:
        return None

    p_text = fields[0].split(":")[1]
    d_text = fields[1].split(":")[1]
    s_text = fields[2].split(":")[1]
    values = (p_text, d_text, s_text)

    if len(p_text) != 1 or len(d_text) not in (1, 2, 3) or len(s_text) != 1:
        return None

    if not all(c in "0123456789" for v in values for c in v):
        return None

    if any(len(v) > 1 and v[0] == "0" for v in values):
        return None

    p, d, s = int(p_text), int(d_text), int(s_text)

    if p not in (0, 1) or s not in (0, 1):
        return None
    if not (d == 0 or 2 <= d <= 400):
        return None

    if checksum(payload) != given_checksum:
        return None

    return (p, d, s)