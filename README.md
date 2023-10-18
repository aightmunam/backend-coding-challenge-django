# Backend Coding Challenge

[![Build Status](https://github.com/Thermondo/backend-code-challenge/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/Thermondo/backend-code-challenge/actions)

We appreciate you taking the time to participate and submit a coding challenge. In the next step we would like you to
create/extend a backend REST API for a simple note-taking app. Below you will find a list of tasks and limitations
required for completing the challenge.

### Application:

* Users can add, delete and modify their notes
* Users can see a list of all their notes
* Users can filter their notes via tags
* Users must be logged in, in order to view/add/delete/etc. their notes

### The notes are plain text and should contain:

* Title
* Body
* Tags

### Optional Features 🚀

* [x] Search contents of notes with keywords
* [x] Notes can be either public or private
    * Public notes can be viewed without authentication, however they cannot be modified
* [x] User management API to create new users

### Limitations:

* use Python / Django
* test accordingly

### What if I don't finish?

Try to produce something that is at least minimally functional. Part of the exercise is to see what you prioritize first when you have a limited amount of time. For any unfinished tasks, please do add `TODO` comments to your code with a short explanation. You will be given an opportunity later to go into more detail and explain how you would go about finishing those tasks.

# Summary and Next Steps:

* Added notes CRUD implementation:
  * Users can add, delete and modify their notes (only if authenticated and authorized).
  * Users can see a list of all their notes and all public notes.
  * Users can filter their notes via tags (via tag title or tag id).
  * Users can search contents of notes (title and body) with keywords.
* Added User registration endpoint along with an endpoint for getting a token.
* Swagger docs can be accessed at `0.0.0.0:8000/docs`
* Some things to consider:
  * Discuss team style/code guide for a more opinionated approach (e.g. ViewSets vs other Generics, service layer vs custom Managers/QuerySets, unittest vs pytest etc.).
  * Move to JWT from DRF's simple token authentication scheme.
  * Use inverted index approach like Elasticsearch, if real time notes search results are needed.
  * Depending on priority, access patterns, usage, some things could be changed:
    * API design could be revisited. For example: nested writes for related objects vs separate endpoint.
    * Adding indexes, cache layer etc.
