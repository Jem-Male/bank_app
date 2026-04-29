1. #### fix and improve templates

2. #### check for data receipt in get:

`test.py:`

```python
data = request.form.get('data') or False
if data is not False:
    return True
elif:
    return False
```

3. #### Implementing validation - Pydantic / Marshmallow