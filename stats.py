from datetime import datetime

data = {
    "total_users": 0,
    "request_number": 0,
    "by_section": {},
    "by_subject": {},
    "by_course": {},
    "resolved": 0,
    "unresolved": 0,
    "to_manager": 0,
}
manager_stats = {}
requests_log = []

def today():
    return datetime.now().strftime("%d.%m.%Y")

def now_str():
    return datetime.now().strftime("%d.%m.%Y %H:%M")

def inc_section(section):
    data["by_section"].setdefault(section, {"total": 0, "resolved": 0, "unresolved": 0})
    data["by_section"][section]["total"] += 1

def inc_resolved_section(section):
    data["by_section"].setdefault(section, {"total": 0, "resolved": 0, "unresolved": 0})
    data["by_section"][section]["resolved"] += 1
    data["resolved"] += 1

def inc_unresolved_section(section):
    data["by_section"].setdefault(section, {"total": 0, "resolved": 0, "unresolved": 0})
    data["by_section"][section]["unresolved"] += 1
    data["unresolved"] += 1

def inc_subject(subject):
    data["by_subject"][subject] = data["by_subject"].get(subject, 0) + 1

def inc_course(course):
    data["by_course"][course] = data["by_course"].get(course, 0) + 1

def next_req_no():
    data["request_number"] += 1
    return data["request_number"]

def add_request(req):
    requests_log.append(req)
    data["to_manager"] += 1

def manager_received(uname, req_info):
    manager_stats.setdefault(uname, {})
    d = today()
    manager_stats[uname].setdefault(d, {"received": 0, "contacted": 0, "resolved": 0, "requests": []})
    manager_stats[uname][d]["received"] += 1
    manager_stats[uname][d]["requests"].append(req_info)

def manager_contacted(uname):
    d = today()
    manager_stats.setdefault(uname, {}).setdefault(d, {"received": 0, "contacted": 0, "resolved": 0, "requests": []})
    manager_stats[uname][d]["contacted"] += 1

def manager_resolved(uname):
    d = today()
    manager_stats.setdefault(uname, {}).setdefault(d, {"received": 0, "contacted": 0, "resolved": 0, "requests": []})
    manager_stats[uname][d]["resolved"] += 1
    data["resolved"] += 1

def get_manager_report(uname, date_str=None):
    if uname not in manager_stats:
        return None
    if date_str:
        return manager_stats[uname].get(date_str)
    total = {"received": 0, "contacted": 0, "resolved": 0, "requests": []}
    for d, v in manager_stats[uname].items():
        total["received"] += v["received"]
        total["contacted"] += v["contacted"]
        total["resolved"] += v["resolved"]
        total["requests"] += v["requests"]
    return total

def get_manager_report_range(uname, date_from, date_to):
    if uname not in manager_stats:
        return None
    from datetime import datetime
    fmt = "%d.%m.%Y"
    d1 = datetime.strptime(date_from, fmt)
    d2 = datetime.strptime(date_to, fmt)
    total = {"received": 0, "contacted": 0, "resolved": 0, "requests": []}
    for d_str, v in manager_stats[uname].items():
        try:
            d = datetime.strptime(d_str, fmt)
            if d1 <= d <= d2:
                total["received"] += v["received"]
                total["contacted"] += v["contacted"]
                total["resolved"] += v["resolved"]
                total["requests"] += v["requests"]
        except:
            pass
    return total