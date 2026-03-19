
import json, datetime, pathlib

out = pathlib.Path("exports/dashboard")
out.mkdir(parents=True, exist_ok=True)

content = {
"generated": str(datetime.datetime.now()),
"lessons":[
{
"title":"Local Power Awareness",
"hook":"Most people don't know who actually runs their town.",
"reality":"Decisions are made by small groups with low visibility.",
"actions":[
"Find your city council",
"Attend one meeting",
"Write down who speaks"
]
}
]
}

(out/"phase12_content.json").write_text(json.dumps(content,indent=2))
(out/"phase12_content.js").write_text("window.PHASE12_CONTENT="+json.dumps(content))
print("built")
