# Media Asset API (Digital Asset Management System)

This is my COM661 CW1 back-end. It is a Flask and MongoDB API . The idea is to keep track of media files (footage, audio and so on) and which physical hard drive each one is stored on, so you can find a file without plugging in every drive.

Base URL: `http://127.0.0.1:5001/api/v1.0`

## How to run it

1. Install the packages: `pip install -r requirements.txt`
2. Make sure MongoDB is running on localhost, then import the data (database name is `damDB`):
```
mongoimport --db damDB --collection users    --file users.json    --jsonArray
mongoimport --db damDB --collection projects --file projects.json --jsonArray
mongoimport --db damDB --collection assets   --file assets.json   --jsonArray
mongoimport --db damDB --collection tags     --file tags.json     --jsonArray
```
3. Start the app: `python app.py`

If you want fresh data, run `python dummyData.py` and it rewrites the four JSON files (100 documents in each).

Logins to try (password is `Password123!` for all of them):
- `user1@studio.com` is an Admin
- `user4@studio.com` is a Creator

## Logging in

Send email and password to `POST /login` using Basic Auth and you get a token back. Put that token in an `x-access-token` header for every other request. `GET /logout` puts the token on a blacklist so it can't be used again. Passwords are hashed in the database.

Creators can only see and change their own projects and assets. Admins can see everything. Request bodies are sent as form data, and the list endpoints take `pn` (page number) and `ps` (page size).

## Endpoints (25)

Everything needs a token except register and login.

**Auth**
- `POST /register` - make a new account (always a Creator)
- `POST /login` - log in, returns the token
- `GET /logout` - cancel the token

**Projects**
- `GET /projects` - my projects (admin gets all of them)
- `POST /projects` - add a project
- `GET /projects/<id>` - one project, plus how many assets it has and their total size
- `PUT /projects/<id>` - edit a project
- `DELETE /projects/<id>` - delete a project and the assets inside it

**Assets**
- `GET /projects/<id>/assets` - assets in a project, can filter by `format`, `drive`, `tag` or `has_proxy`
- `POST /projects/<id>/assets` - add an asset and say which drive it is on
- `GET /assets/<id>` - one asset with its tags and audit logs
- `PUT /assets/<id>` - edit an asset
- `DELETE /assets/<id>` - delete an asset
- `GET /search?query=` - search filename, drive, tag name and project title

**Tags**
- `GET /tags` - all tags
- `POST /tags` - add a tag
- `POST /assets/<id>/tags` - put a tag on an asset (send `tag_name`)
- `DELETE /assets/<id>/tags/<tag_id>` - take a tag off an asset

**Audit logs**
- `POST /assets/<id>/audit_logs` - add a log
- `PUT /assets/<id>/audit_logs/<log_id>` - edit a log
- `DELETE /assets/<id>/audit_logs/<log_id>` - delete a log

**Admin only**
- `GET /admin/users` - every user
- `GET /admin/projects` - every project with its owner
- `DELETE /admin/users/<id>` - delete a user and their projects and assets
- `POST /admin/tags` - add a tag

Status codes used: 200, 201, 400 (bad input), 401 (not logged in), 403 (not allowed), 404 (not found), 409 (duplicate).