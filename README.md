
# rawkais

## use
1. Install selenium
   ```
   pip install selenium
   ```
   
2. Setup config @ `config.json`

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
       e.g. `"c[CSGE602012_01.00.12.01-2020]": [1,2,0,3,4]` as 
       `'c[<class_code>_<curriculum_code>]': [<priority>]`
       with 0 being the topmost class (A class = 0, B class = 1, etc.)

3. Run