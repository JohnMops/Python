1. Create volume for data:

```bash
mkdir /custom
```

2. Run the docker image locally:

```bash
run -d --name ps -e POSTGRES_PASSWORD=5961772 \ 
-e PGDATA=/var/lib/postgresql/data/pgdata \ 
-v /custom \ 
-p 5432:5432 \ 
postgres
```

3. ```bash
    pip3 install -r requirements.txt
    ```

4. ``` 
   python3 main.py
```

5. Make a curl request to update revision
```
    curl -H 'Content-Type: application/json' -X PUT \
    -d '{"revision":"<your_revision_number>",
         "deployment":"<your_deployment_name>"}' \
    http://localhost:8080/api/v1/update_deployment
```