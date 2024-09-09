## Setting Up a New Project
Run new-project.sh in a directory where you want to create the project folder.

## Setting Up a New VPS
- SSH into the VPS
- Create SSH key
```shell
ssh-keygen -t rsa -b 4096"```
```
- Copy the key
```shell
cat ~/.ssh/id_rsa.pub
```
- Update and upgrade the system
```shell
sudo apt update && sudo apt upgrade -y
```
- Update and upgrade the system
```shell
sudo apt install -y docker.io docker-compose
```
- Create Development dir
```shell
mkdir development
```
- Clone repo
```shell
git clone {repo_url}
```
- Set up SSL with Certbot (optional, comment out if not using SSL)
```shell
sudo apt install -y certbot python3-certbot-nginx
```
- Move docker-compose for prod
- Move env file for prod
```shell
~ scp ~/Documents/Development/shariq1989-django-starter/{docker-compose-for-prod.yml} root@root@165.227.205.174:~/
~ scp ~/Documents/Development/shariq1989-django-starter/{dot env} root@root@165.227.205.174:~/
```
- Start container
```shell
➜  ~ sudo docker-compose -f docker-compose-prod.yml up --build -d
```
- Stop container
```shell
➜  ~ docker-compose down --remove-orphans
```
- Generate a new django key and update prod dockerfile
```python
import secrets
print(secrets.token_urlsafe(50))
```
### Domain Configuration
- Add records to domain registrar
  - A, @, IP.Address, Automatic
  - CNAME, www, url.com, Automatic
- Update URL in 
  - {repo}/nginx/nginx.conf
  - ALLOWED_HOSTS in docker-compose-prod.yml
### SSL Configuration
- SSL (run commands on HOST machine, not in a container!)
```shell
apt-get update
apt-get install -y certbot python3-certbot-nginx
# Stop your Docker containers temporarily:
docker-compose down
sudo certbot --nginx -d pushmypost.com -d www.pushmypost.com
```

- Update docker-compose-prod.yml
```yml
nginx:
  # ... other configurations ...
  volumes:
    - ./nginx:/etc/nginx/conf.d
    - /etc/letsencrypt:/etc/letsencrypt:ro
    - /var/lib/letsencrypt:/var/lib/letsencrypt
  ports:
    - "80:80"
    - "443:443"
```

- Update Nginx configuration In {repo}/nginx/nginx.conf:
```text
server {
    listen 80;
    server_name pushmypost.com www.pushmypost.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name pushmypost.com www.pushmypost.com;

    ssl_certificate /etc/letsencrypt/live/pushmypost.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pushmypost.com/privkey.pem;
    # ... rest of your SSL configuration ...
```

- If port 443 is already in use, you may need to identify and stop the process using it
```shell
sudo lsof -i :443
sudo kill -9 {PID}
sudo systemctl disable nginx && sudo systemctl stop nginx
```

### Useful commands

## Management Commands
```shell
# Create a trends request
docker-compose exec web python manage.py post_trending
# Check to see if the request was fulfilled.
# If so, fetch daily trends
docker-compose exec web python manage.py get_trending

```

```shell
#### BASE COMMANDS
# Start local docker instances
docker-compose up -d --build
# Take instances down
docker-compose down --remove-orphans
# View logs
docker logs --follow recipe_research-web-1
# Run tests
docker-compose exec web python manage.py test

# Django migrations
docker-compose exec web python manage.py makemigrations
# ONLY RUN LOCALLY
docker-compose exec web python manage.py migrate

# Connect to Postgres
docker-compose exec db psql --username=postgres --dbname=postgres
# run your SQL commands now

# Wipe DB
sudo docker volume rm recipe_research_postgres_data

```

### Postgres DB backup/restore

```shell
docker exec b07c0d3d66e1 pg_dump -U postgres >backup.sql
# Backup specific tables
docker exec b07c0d3d66e1 pg_dump -U postgres -d postgres -t watchmyteam_arena -t watchmyteam_league -t watchmyteam_season -t watchmyteam_team -t watchmyteam_game -t
watchmyteam_distance >watchmyteam.sql

# restore backup
# copy file to container
sudo docker cp backup.sql edd255f87e94:/
# load backup file
sudo docker exec 5ca62fdcdefe psql -U postgres -d postgres -f /backup.sql

```

### Delete today's Trending KW

```postgresql
DELETE
FROM trends_trending
WHERE DATE(created_on) = CURRENT_DATE;
```
### Manually insert a row

```postgresql
--- Do a SELECT to verify columns
SELECT *
FROM trends_trendingbatch
LIMIT 1;

--- INSERT SQL
INSERT INTO trends_trendingbatch
VALUES (1, '07210409-4355-0170-0000-fb6660100e70', 'google.com', 't', NOW());
```
### Deleting duplicate keywords

```postgresql
--  Delete keyword from Batch Result
DELETE
FROM trends_batchresult
WHERE keyword_id IN (SELECT a.kw_id
                     FROM trends_keyword a
                              JOIN trends_keyword b ON a.keyword = b.keyword AND a.kw_id < b.kw_id);

--  Delete keyword from Trending
DELETE
FROM trends_trending
WHERE keyword_id IN (SELECT a.kw_id
                     FROM trends_keyword a
                              JOIN trends_keyword b ON a.keyword = b.keyword AND a.kw_id < b.kw_id);

--  Delete keyword from RankingForumPosts
DELETE
FROM trends_rankingforumposts
WHERE keyword_id IN (SELECT a.kw_id
                     FROM trends_keyword a
                              JOIN trends_keyword b ON a.keyword = b.keyword AND a.kw_id < b.kw_id);


--  Delete keyword from Related Keyword 
DELETE
FROM trends_relatedkeyword
WHERE related_keyword_id IN (SELECT a.kw_id
                             FROM trends_keyword a
                                      JOIN trends_keyword b ON a.keyword = b.keyword AND a.kw_id < b.kw_id);
DELETE
FROM trends_relatedkeyword
WHERE keyword_id IN (SELECT a.kw_id
                     FROM trends_keyword a
                              JOIN trends_keyword b ON a.keyword = b.keyword AND a.kw_id < b.kw_id);

--  Delete the keyword
delete
from trends_keyword a using trends_keyword b
where a.kw_id < b.kw_id
  AND a.keyword = b.keyword;

-- Verify
select a.kw_id
from trends_keyword AS a,
     trends_keyword AS b
where a.kw_id < b.kw_id
  AND a.keyword = b.keyword;


```

### AWS

```shell
# copy file to aws
scp -i ~/Documents/Development/AWS/2022RTW.pem watchmyteam.sql ubuntu@34.229.15.11:~/

```