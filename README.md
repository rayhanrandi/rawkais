
# ?rawkais

`pip install selenium`

https://googlechromelabs.github.io/chrome-for-testing/

https://selenium-python.readthedocs.io/index.html

## use
1. Setup config @ `config.json`

```json
{
    "username": "<your username here>",
    "password": "<your password here>",
    "term": 1,
    "irs": {
        "c[CSCM603228_01.00.12.01-2020]": [2,1,0],
        "c[CSIE604160_06.00.12.01-2020]": [0]
    }
}
```

  - `username` : SIAK username
  - `password` : SIAK password
  - `term` : 1 : ganjil, 2 : genap, 3: pendek
  - `irs` : key value pairs of `{str: list[int]}`, 
    e.g. `'c[<class_code>_<curriculum_code>]': [<priority>]` as 
    `'c[<class_code>_<curriculum_code>]': [<priority>]`
    with 0 being the topmost class (A class = 0, B class = 1, etc.)

2. Run