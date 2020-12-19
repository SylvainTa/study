# 小学春游 - 两组同学，每组1-3人，每组有一个队长;春游期间，由于景点人数较多，秩序混乱，班主任要求在指定地点，按组集合

# 源数据
s = [{'name': 'leader-1', 'belong_to': None},
     {'name': 'jack', 'belong_to': 'leader-2'},
     {'name': 'lili', 'belong_to': 'leader-1'},
     {'name': 'leader-2', 'belong_to': None},
     {'name': 'Tom', 'belong_to': 'leader-1'}]
# 目标数据
d = [
    {'name': 'leader-1', 'team': [{'name': 'lili'}, {'name': 'Tom'}]},
    {'name': 'leader-2', 'team': [{'name': 'jack'}]}
]


def find_team(data):
    leader_data = []

    m_dict = {}

    for i in data:
       if  i['belong_to']:
           m_dict.setdefault(i['belong_to'],[])
           m_dict[i['belong_to']].append({'name':i['name']})
       else:
           leader_data.append({'name': i['name'], 'team': []})
    print(m_dict)
    print(leader_data)
    for l in leader_data:
        if l['name'] in m_dict:
            l['team'] = m_dict[l['name']]
    return leader_data


print(find_team(s))
