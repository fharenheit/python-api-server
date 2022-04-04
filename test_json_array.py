import json

music_id = '{"id":1,"username":"ziy0ung","display_name":["ziy0ung", "jiy0ung"]}'
jsonObject = json.loads(music_id)
jsonArray = jsonObject['display_name']
for name in jsonArray:
    print(name)
