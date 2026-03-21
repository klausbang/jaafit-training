import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.skool.com/jaafit/classroom/1b2baa38?md="

exercises_raw = [
    # Bryst
    {"id": "2b1ab4ce18d84fc8a6989120e00d1824", "title": "Brystfly m. haandtag",           "muscle_group": "Bryst",                         "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "573e4c0f38d147f593ab1f52f036eb16", "title": "Staaende Brystpres m. bar",      "muscle_group": "Bryst",                         "equipment": ["bar"],      "requires_door_anchor": True},
    {"id": "1f7932321cb340d38ccead6c6bf3d28b", "title": "Fritstaaende Brystpres m. bar",  "muscle_group": "Bryst",                         "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "7a19ac3633ea47688ad8de5859c93f03", "title": "Armboejning m. elastik",          "muscle_group": "Bryst",                         "equipment": ["elastik"],  "requires_door_anchor": False},
    # Ryg
    {"id": "2a85ddf941904c7b8793f91cbee7a963", "title": "Bent over Row m. bar",            "muscle_group": "Ryg",                           "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "1a2b6b6a598941259e97506f0dde70c6", "title": "Traek til Hofte m. haandtag",    "muscle_group": "Ryg",                           "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "bc8448939d6b4de4bbaf1f868898f220", "title": "Staaende Row m. bar",             "muscle_group": "Ryg",                           "equipment": ["bar"],      "requires_door_anchor": True},
    {"id": "21c670a4f5d84c01a8a0e3a84280d087", "title": "Pullover m. bar",                 "muscle_group": "Ryg",                           "equipment": ["bar"],      "requires_door_anchor": True},
    {"id": "a4612851822b47518aa797ab0c28fc72", "title": "Siddende Traek til Bryst m. bar", "muscle_group": "Ryg",                           "equipment": ["bar"],      "requires_door_anchor": True},
    {"id": "12d5fec659a34a0aaae05ae43a8e2de3", "title": "Siddende pull down 1 arm",        "muscle_group": "Ryg",                           "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "b74385a88ac44026b5bed3bbbba35218", "title": "Siddende traek til hofte haandtag en arm", "muscle_group": "Ryg",                  "equipment": ["haandtag"], "requires_door_anchor": True},
    # Forlaar
    {"id": "bb50d1d9bee444528887906d40c07b34", "title": "Squat m. bar",                    "muscle_group": "Forlaar",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "8461e0d9e9dd4c35872734d03092b8ea", "title": "Split Squat m. bar",              "muscle_group": "Forlaar",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "ce15f8fe0c9d47ec8f2278f534b96b20", "title": "Front Squat m. bar",              "muscle_group": "Forlaar",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "ea1a793cfae948e2819054015ce6a5cd", "title": "Begyndervenlig Squat m. bar",      "muscle_group": "Forlaar",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "23cda7c5540d4549996cf51ecd23479a", "title": "Leg Extension m. ankelstropper",   "muscle_group": "Forlaar",                       "equipment": ["ankelstropper"], "requires_door_anchor": True},
    # Baglaar og baller
    {"id": "7aee8ec48aab422fb2df2b4a09452b55", "title": "Hofte Extension m. haandtag",     "muscle_group": "Baglaar og baller",             "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "171aaafa82e147439900695ac5eaec36", "title": "Donkey Kick m. ankelstropper",    "muscle_group": "Baglaar og baller",             "equipment": ["ankelstropper"], "requires_door_anchor": True},
    {"id": "4a63032c35fe402ab6416a127eac5ecd", "title": "Rumaensk Doedloeft m. bar",       "muscle_group": "Baglaar og baller",             "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "f77d97b6c2db4271af5496cb9d036bf5", "title": "Doedloeft m. bar",                "muscle_group": "Baglaar og baller",             "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "ff6526db998140368cee351fa2184ed1", "title": "Leg Curl m. ankelstropper",       "muscle_group": "Baglaar og baller",             "equipment": ["ankelstropper"], "requires_door_anchor": True},
    {"id": "b43cec0635494eeaa7eb602bab97b6c1", "title": "Hip Thrust m. bar",               "muscle_group": "Baglaar og baller",             "equipment": ["bar"],      "requires_door_anchor": False},
    # Inder og ydersiden
    {"id": "794c1c718af9464a9d8099973e00fdaa", "title": "Adduction m. ankelstropper",      "muscle_group": "Inder og ydersiden af laarene", "equipment": ["ankelstropper"], "requires_door_anchor": True},
    {"id": "5aeac24a3d354740b2314864e005386a", "title": "Abduktion m. ankelstropper",      "muscle_group": "Inder og ydersiden af laarene", "equipment": ["ankelstropper"], "requires_door_anchor": True},
    # Biceps
    {"id": "1e407305f56e4c178e5f67fea9ca5d84", "title": "Biceps Curl m. bar",              "muscle_group": "Biceps",                        "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "6f01796cb46f4d798d2ec24e017edff9", "title": "Biceps Curl Faceaway m. haandtag","muscle_group": "Biceps",                        "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "3be46dbb6f4d45b08d0570c100b2e835", "title": "Hammercurl m. elastik",           "muscle_group": "Biceps",                        "equipment": ["elastik"],  "requires_door_anchor": False},
    # Triceps
    {"id": "07d4f5ea9a444a83901be6c2485164a5", "title": "Triceps Pushdown m. haandtag",    "muscle_group": "Triceps",                       "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "39e9e9e70fd441b0978840bcb99fbcf0", "title": "Skullcrusher m. bar",             "muscle_group": "Triceps",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "6c5732539ca24ce69ba99790fc39d519", "title": "Triceps Extension m. elastik",    "muscle_group": "Triceps",                       "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "1883d88e769548d3a6a09419e4ae1b8c", "title": "Triceps Kickback m. elastik",     "muscle_group": "Triceps",                       "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "3d282b1b76424a8a88850cae89c55ff2", "title": "Triceps Pushdown m. elastik",     "muscle_group": "Triceps",                       "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "831f796f738d41478e165a2c03924dcb", "title": "Triceps Pushdown m. bar",         "muscle_group": "Triceps",                       "equipment": ["bar"],      "requires_door_anchor": True},
    # Skulder
    {"id": "03b4a420e2b04921a89813fd2dfddbe7", "title": "Overhead Press m. bar",           "muscle_group": "Skulder",                       "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "785b16d8e44744a49db0c2abd1322004", "title": "Lateral Raises m. haandtag",      "muscle_group": "Skulder",                       "equipment": ["haandtag"], "requires_door_anchor": False},
    {"id": "3e7115bbf11a4b3186734902c07c59a1", "title": "Rear Delt Fly m. elastik",        "muscle_group": "Skulder",                       "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "0f13ee8efc0449e582961b757adefdc1", "title": "Lateral Raise m. dooranker Oevetl","muscle_group": "Skulder",                      "equipment": ["haandtag"], "requires_door_anchor": True},
    {"id": "946f3cabfd314b2883520918a2abfc82", "title": "Front Raise m. haandtag",         "muscle_group": "Skulder",                       "equipment": ["haandtag"], "requires_door_anchor": False},
    {"id": "55b79aab39ad4e1f9ac8323abe15f3ac", "title": "Face Pull m. haandtag",           "muscle_group": "Skulder",                       "equipment": ["haandtag"], "requires_door_anchor": True},
    # Mave
    {"id": "fa7a7fc50aeb41688709858222bf800e", "title": "Side Bend m. elastik",            "muscle_group": "Mave",                          "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "3c405fd6ecf94a53b5d10e6f2c7e48b3", "title": "Chrunches m. elastik",            "muscle_group": "Mave",                          "equipment": ["elastik"],  "requires_door_anchor": False},
    {"id": "4c48a8783f3f4925b5ece9a0c3b2c767", "title": "Leg Raises m. ankelstropper",     "muscle_group": "Mave",                          "equipment": ["ankelstropper"], "requires_door_anchor": True},
    # Laeg
    {"id": "888cc143f1214523adb2bfd576b1356d", "title": "Calf Raises m. bar",              "muscle_group": "Laeg",                          "equipment": ["bar"],      "requires_door_anchor": False},
    {"id": "e9278e59e4e54c3e86d3b5d08b636d38", "title": "Calf Raises m. kropsvagt",        "muscle_group": "Laeg",                          "equipment": ["kropsvagt"], "requires_door_anchor": False},
    # PowerPress
    {"id": "0801acfa4fa54e1d8845df77df3ef9f0", "title": "Seated row m. PowerPress",        "muscle_group": "Ryg",                           "equipment": ["PowerPress"], "requires_door_anchor": False},
    {"id": "8731db109e424017a2472dbf9bd9c55b", "title": "Liggende brystpres m. PowerPress","muscle_group": "Bryst",                         "equipment": ["PowerPress"], "requires_door_anchor": False},
    {"id": "28d05260cca14bc691a153777324c7b8", "title": "Staaende brystpres m. PowerPress","muscle_group": "Bryst",                         "equipment": ["PowerPress"], "requires_door_anchor": False},
    {"id": "bbc611bcea8946ba9267da0fb9493b84", "title": "Rumaensk doedloeft m. PowerPress","muscle_group": "Baglaar og baller",             "equipment": ["PowerPress"], "requires_door_anchor": False},
    {"id": "1ee1031e9c6343fe81b612194b620437", "title": "Bent over row m. PowerPress",     "muscle_group": "Ryg",                           "equipment": ["PowerPress"], "requires_door_anchor": False},
]

# Display names (Danish with special chars)
display_names = {
    "2b1ab4ce18d84fc8a6989120e00d1824": "Brystfly m. haandtag",
    "573e4c0f38d147f593ab1f52f036eb16": "Staaende Brystpres m. bar",
    "1f7932321cb340d38ccead6c6bf3d28b": "Fritstaaende Brystpres m. bar",
    "7a19ac3633ea47688ad8de5859c93f03": "Armboejning m. elastik",
    "2a85ddf941904c7b8793f91cbee7a963": "Bent over Row m. bar",
    "1a2b6b6a598941259e97506f0dde70c6": "Traek til Hofte m. haandtag",
    "bc8448939d6b4de4bbaf1f868898f220": "Staaende Row m. bar",
    "21c670a4f5d84c01a8a0e3a84280d087": "Pullover m. bar",
    "a4612851822b47518aa797ab0c28fc72": "Siddende Traek til Bryst m. bar",
    "12d5fec659a34a0aaae05ae43a8e2de3": "Siddende pull down (1 arm)",
    "b74385a88ac44026b5bed3bbbba35218": "Siddende traek til hofte m. haandtag (en arm)",
}

# Add URLs
for e in exercises_raw:
    e["url"] = BASE_URL + e["id"]

programs = [
    {
        "id": "prog1", "name": "Effektiv Velvaere", "number": 1,
        "url": "https://www.skool.com/jaafit/classroom/448639cb",
        "days": [
            {"day": 1, "type": "Fullbody", "exercise_ids": [
                "573e4c0f38d147f593ab1f52f036eb16", "bc8448939d6b4de4bbaf1f868898f220",
                "785b16d8e44744a49db0c2abd1322004", "6c5732539ca24ce69ba99790fc39d519",
                "23cda7c5540d4549996cf51ecd23479a", "ff6526db998140368cee351fa2184ed1"]},
            {"day": 2, "type": "Fullbody", "exercise_ids": [
                "f77d97b6c2db4271af5496cb9d036bf5", "ea1a793cfae948e2819054015ce6a5cd",
                "2b1ab4ce18d84fc8a6989120e00d1824", "1a2b6b6a598941259e97506f0dde70c6",
                "03b4a420e2b04921a89813fd2dfddbe7", "1e407305f56e4c178e5f67fea9ca5d84"]},
        ]
    },
    {
        "id": "prog2", "name": "Feminin Styrke", "number": 2,
        "url": "https://www.skool.com/jaafit/classroom/448639cb",
        "days": [
            {"day": 1, "type": "Fullbody", "exercise_ids": [
                "4a63032c35fe402ab6416a127eac5ecd", "5aeac24a3d354740b2314864e005386a",
                "794c1c718af9464a9d8099973e00fdaa", "1a2b6b6a598941259e97506f0dde70c6",
                "07d4f5ea9a444a83901be6c2485164a5", "3c405fd6ecf94a53b5d10e6f2c7e48b3"]},
            {"day": 2, "type": "Fullbody", "exercise_ids": [
                "ce15f8fe0c9d47ec8f2278f534b96b20", "03b4a420e2b04921a89813fd2dfddbe7",
                "1e407305f56e4c178e5f67fea9ca5d84", "7aee8ec48aab422fb2df2b4a09452b55",
                "171aaafa82e147439900695ac5eaec36", "4c48a8783f3f4925b5ece9a0c3b2c767"]},
            {"day": 3, "type": "Fullbody", "exercise_ids": [
                "f77d97b6c2db4271af5496cb9d036bf5", "ea1a793cfae948e2819054015ce6a5cd",
                "2a85ddf941904c7b8793f91cbee7a963", "785b16d8e44744a49db0c2abd1322004",
                "573e4c0f38d147f593ab1f52f036eb16", "fa7a7fc50aeb41688709858222bf800e"]},
        ]
    },
    {
        "id": "prog3", "name": "Hverdagskrigeren", "number": 3,
        "url": "https://www.skool.com/jaafit/classroom/448639cb",
        "days": [
            {"day": 1, "type": "Ben og Biceps", "exercise_ids": ["f77d97b6c2db4271af5496cb9d036bf5","1e407305f56e4c178e5f67fea9ca5d84"]},
            {"day": 2, "type": "Ryg og Triceps", "exercise_ids": ["1a2b6b6a598941259e97506f0dde70c6","07d4f5ea9a444a83901be6c2485164a5"]},
            {"day": 3, "type": "Bryst og Skuldre", "exercise_ids": ["573e4c0f38d147f593ab1f52f036eb16","785b16d8e44744a49db0c2abd1322004"]},
            {"day": 4, "type": "Ben og Biceps", "exercise_ids": ["ce15f8fe0c9d47ec8f2278f534b96b20","3be46dbb6f4d45b08d0570c100b2e835"]},
            {"day": 5, "type": "Mave og Skuldre", "exercise_ids": ["03b4a420e2b04921a89813fd2dfddbe7","3c405fd6ecf94a53b5d10e6f2c7e48b3"]},
        ]
    },
    {
        "id": "prog4", "name": "Fundamental Styrke", "number": 4,
        "url": "https://www.skool.com/jaafit/classroom/448639cb",
        "days": [
            {"day": 1, "type": "Lower 1", "exercise_ids": [
                "ce15f8fe0c9d47ec8f2278f534b96b20","4a63032c35fe402ab6416a127eac5ecd",
                "23cda7c5540d4549996cf51ecd23479a","ff6526db998140368cee351fa2184ed1",
                "3c405fd6ecf94a53b5d10e6f2c7e48b3"]},
            {"day": 2, "type": "Upper 1", "exercise_ids": [
                "2b1ab4ce18d84fc8a6989120e00d1824","1a2b6b6a598941259e97506f0dde70c6",
                "03b4a420e2b04921a89813fd2dfddbe7","1e407305f56e4c178e5f67fea9ca5d84",
                "39e9e9e70fd441b0978840bcb99fbcf0"]},
            {"day": 3, "type": "Lower 2", "exercise_ids": [
                "f77d97b6c2db4271af5496cb9d036bf5","8461e0d9e9dd4c35872734d03092b8ea",
                "5aeac24a3d354740b2314864e005386a","794c1c718af9464a9d8099973e00fdaa",
                "4c48a8783f3f4925b5ece9a0c3b2c767"]},
            {"day": 4, "type": "Upper 2", "exercise_ids": [
                "1f7932321cb340d38ccead6c6bf3d28b","2a85ddf941904c7b8793f91cbee7a963",
                "6c5732539ca24ce69ba99790fc39d519","6f01796cb46f4d798d2ec24e017edff9",
                "785b16d8e44744a49db0c2abd1322004"]},
        ]
    },
    {
        "id": "prog5", "name": "Maksimal Styrke", "number": 5,
        "url": "https://www.skool.com/jaafit/classroom/448639cb",
        "days": [
            {"day": 1, "type": "Push 1", "exercise_ids": [
                "7a19ac3633ea47688ad8de5859c93f03","2b1ab4ce18d84fc8a6989120e00d1824",
                "07d4f5ea9a444a83901be6c2485164a5","785b16d8e44744a49db0c2abd1322004"]},
            {"day": 2, "type": "Pull 1", "exercise_ids": [
                "a4612851822b47518aa797ab0c28fc72","21c670a4f5d84c01a8a0e3a84280d087",
                "1e407305f56e4c178e5f67fea9ca5d84","55b79aab39ad4e1f9ac8323abe15f3ac"]},
            {"day": 3, "type": "Legs 1", "exercise_ids": [
                "23cda7c5540d4549996cf51ecd23479a","ff6526db998140368cee351fa2184ed1",
                "ce15f8fe0c9d47ec8f2278f534b96b20","f77d97b6c2db4271af5496cb9d036bf5"]},
            {"day": 4, "type": "Push 2", "exercise_ids": [
                "03b4a420e2b04921a89813fd2dfddbe7","2b1ab4ce18d84fc8a6989120e00d1824",
                "1f7932321cb340d38ccead6c6bf3d28b","3d282b1b76424a8a88850cae89c55ff2"]},
            {"day": 5, "type": "Pull 2", "exercise_ids": [
                "2a85ddf941904c7b8793f91cbee7a963","12d5fec659a34a0aaae05ae43a8e2de3",
                "3e7115bbf11a4b3186734902c07c59a1","3be46dbb6f4d45b08d0570c100b2e835"]},
            {"day": 6, "type": "Legs 2", "exercise_ids": [
                "ce15f8fe0c9d47ec8f2278f534b96b20","f77d97b6c2db4271af5496cb9d036bf5",
                "23cda7c5540d4549996cf51ecd23479a","ff6526db998140368cee351fa2184ed1"]},
        ]
    },
]

muscle_groups_order = ["Bryst","Ryg","Forlaar","Baglaar og baller","Inder og ydersiden af laarene",
                        "Biceps","Triceps","Skulder","Mave","Laeg"]
all_equipment = ["elastik","bar","haandtag","ankelstropper","PowerPress","kropsvagt"]

graph = {
    "meta": {
        "description": "JAAFIT oevelsesdatabase - graph model",
        "source": "https://www.skool.com/jaafit",
        "exercises_library_url": "https://www.skool.com/jaafit/classroom/1b2baa38",
        "programs_url": "https://www.skool.com/jaafit/classroom/448639cb",
        "last_updated": "2026-03-16",
        "note": "Kraever JAAFIT-medlemskab for adgang. Webadresser virker kun med login paa skool.com."
    },
    "nodes": {
        "muscle_groups": [{"id": f"mg_{mg}", "label": mg} for mg in muscle_groups_order],
        "equipment": [{"id": f"eq_{eq}", "label": eq} for eq in all_equipment],
        "exercises": exercises_raw,
        "programs": programs
    },
    "edges": []
}

# Exercise -> MuscleGroup
for e in exercises_raw:
    graph["edges"].append({"from": e["id"], "to": f"mg_{e['muscle_group']}", "relation": "TRAENER_MUSKEL"})

# Exercise -> Equipment
for e in exercises_raw:
    for eq in e["equipment"]:
        graph["edges"].append({"from": e["id"], "to": f"eq_{eq}", "relation": "BRUGER_UDSTYR"})

# Program -> Day -> Exercise
for prog in programs:
    for day in prog["days"]:
        day_id = f"{prog['id']}_dag{day['day']}"
        graph["edges"].append({"from": prog["id"], "to": day_id, "relation": "HAR_DAG",
                                "label": f"Dag {day['day']}: {day['type']}"})
        for ex_id in day["exercise_ids"]:
            graph["edges"].append({"from": day_id, "to": ex_id, "relation": "INKLUDERER_OEVELSE"})

with open("jaafit_database.json", "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)

print(f"OK: jaafit_database.json")
print(f"  {len(exercises_raw)} oevelser")
print(f"  {len(muscle_groups_order)} muskelgrupper")
print(f"  {len(all_equipment)} udstyrstyper")
print(f"  {len(programs)} traeningsprogrammer")
print(f"  {len(graph['edges'])} kanter")
