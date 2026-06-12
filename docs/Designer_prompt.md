# Cabinet Designer Prompt

Copy the block below into Claude (or any LLM), append your cabinet description at the end, and Claude will return a ready-to-use DSL.

---

## The prompt

````
You are a cabinet design assistant. Use the DSL specification below to produce a valid cabinet DSL for the user's request. Output YAML only — no explanation, no markdown fences.

<dsl_spec>
[paste the full contents of docs/DSL.md here]
</dsl_spec>

User request:
````

Append your request after "User request:" — one or two sentences is enough.

---

## Example requests and outputs

### Standalone wardrobe with shelves, drawers, and hanging

**Prompt tail:**
> User request: 2000 x 2200 x 600 mm freestanding wardrobe. Left half: full-height hanging. Right half: 5 adjustable shelves on top, 2 drawer bays at the bottom (600 mm high). Slab doors, white body, oak doors.

**Expected output:**
```yaml
use: euro_builtin_v1
material: plywood_18

space:
  kind: free

cabinet:
  type: standing
  width: 2000
  height: 2200
  depth: 600
  split: none
  base: legs 80

layout:
  main:
    columns:
      1000: hanging rod 1900
      "*":
        rows:
          - height: "*"
            columns:
              - width: "*"
                function: shelves 5 adjustable
          - height: 600
            columns:
              - width: "*"
                function: drawers

doors:
  main: auto
  style: slab
  hinges: concealed

finish:
  body: white
  doors: oak
```

---

### Niche with shelves only

**Prompt tail:**
> User request: Built-in niche 800 x 2400 x 350 mm. 6 adjustable shelves, no hanging. No doors. White throughout.

**Expected output:**
```yaml
use: euro_builtin_v1
material: plywood_18

space: niche 800 x 2400 x 350

cabinet:
  type: built_in
  split: auto
  base: legs 80

layout:
  main:
    columns:
      "*": shelves 6 adjustable

doors:
  main: none

finish:
  body: white
```

---

### Entryway unit with shoes and hooks

**Prompt tail:**
> User request: Built-in niche 1200 x 2100 x 400 mm. Bottom 700 mm: 3 rows of shoe shelves. Top: open hooks storage. No doors. Anthracite MDF.

**Expected output:**
```yaml
use: euro_builtin_v1
material: mdf_18

space: niche 1200 x 2100 x 400

cabinet:
  type: built_in
  split: none
  base: plinth 100

layout:
  main:
    rows:
      - height: "*"
        columns:
          - width: "*"
            function: hooks
      - height: 700
        columns:
          - width: "*"
            function: shoes 3

doors:
  main: none

finish:
  body: anthracite
```
