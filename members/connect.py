import urllib.request, json    

def connect() -> dict:
    # Connect to PeterPortal
    body = {'query': 'query { allCourses {id, title, department, department_name, description, units, prerequisite_text, overlap, same_as, restriction, corequisite}}'}
    headers = {'Content-Type' : 'application/json'}
    request = urllib.request.Request("https://api.peterportal.org/graphql", data=json.dumps(body).encode('utf-8'), headers=headers)
    response = urllib.request.urlopen(request)
    obj = json.loads(response.read().decode(encoding="utf-8"))
    response.close()

    # Terminal Representation of Parsed Information
    allCourses: list = obj['data']['allCourses']

    # Parse all ints in a class's id, used for lambda sorts
    def parse_int(course: dict) -> int:
        return int(''.join([c for c in course['id'] if c.isnumeric()]))
    
    allCourses.sort(key = parse_int)
    # Replaces all / characters with a space to avoid url issues (these spaces become %20 later)
    for c in allCourses: 
        if '/' in c['department']:
            c['department'] = c['department'].replace('/', ' ')

    return allCourses